import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sensory_data_client.exceptions import DatabaseError
from sensory_data_client.models.line import Line  # Pydantic-модель (минимальная)
from sensory_data_client.db.base import get_session
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# ВАЖНО: проверьте корректность импортов ORM-классов под вашу структуру модулей
from sensory_data_client.db.documents.lines.rawline_orm import RawLineORM
from sensory_data_client.db.documents.lines.documentLine_orm import DocumentLineORM  # __tablename__="lines_document"
from sensory_data_client.db.documents.lines.imageLine_orm import ImageLineORM        # __tablename__="lines_image"
from sensory_data_client.db.documents.lines.audioLine_orm import AudioLineORM        # __tablename__="lines_audio"
from sensory_data_client.repositories import DocumentDetailsRepository
from sensory_data_client.repositories import ImageRepository
from sensory_data_client.repositories import AudioRepository
from sensory_data_client.db.uow import AsyncUnitOfWork

logger = logging.getLogger(__name__)


class LineRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        doc_repo: DocumentDetailsRepository,
        img_repo: ImageRepository,
        audio_repo: AudioRepository,
    ):
        self._session_factory = session_factory
        self._doc_repo = doc_repo
        self._img_repo = img_repo
        self._audio_repo = audio_repo

    # ------------- Вспомогательные методы классификации модальности -------------

    @staticmethod
    def _detect_block_type(obj: Any) -> Optional[str]:
        """
        Унифицирует чтение типа блока из pydantic-объекта/словаря.
        Допускаем, что поле может называться block_type или type.
        """
        bt = getattr(obj, "block_type", None)
        if bt:
            return bt
        # Pydantic Line мог называться 'type'
        return getattr(obj, "type", None)

    @staticmethod
    def _is_image_line(block_type: Optional[str], obj: Any) -> bool:
        if block_type is None:
            return False
        bt = str(block_type).lower()
        # Расширяемый список синонимов для изображений
        if bt in {"image", "image_placeholder", "img", "picture"}:
            return True
        # флаги из модели
        return bool(getattr(obj, "is_image", False))

    @staticmethod
    def _is_audio_line(block_type: Optional[str], obj: Any) -> bool:
        if block_type is None:
            # наличие тайм-кодов часто сигналит про аудио
            return any(hasattr(obj, x) for x in ("start_ts", "end_ts", "duration"))
        bt = str(block_type).lower()
        if bt in {"audio", "audio_sentence", "audio_segment"}:
            return True
        return any(hasattr(obj, x) for x in ("start_ts", "end_ts", "duration"))

    @staticmethod
    def _geometry_dict(obj: Any) -> Optional[dict]:
        """
        Унификация получения geometry: либо уже dict, либо собираем из polygon/bbox.
        """
        geom = getattr(obj, "geometry", None)
        if isinstance(geom, dict):
            return geom
        polygon = getattr(obj, "polygon", None) #TODO
        bbox = getattr(obj, "bbox", None)
        if polygon or bbox:
            return {"polygon": polygon, "bbox": bbox}
        return None

    # ------------- Основные public-методы (ИМЕНА СОХРАНЕНЫ) -------------

    async def save_lines(self, doc_id: UUID, lines: list[Line]):
        if not lines:
            return
        async with AsyncUnitOfWork(self._session_factory) as uow:
            try:
                await uow.advisory_lock_doc(str(doc_id))

                # 0) Полная очистка предыдущего содержимого
                await uow.session.execute(delete(RawLineORM).where(RawLineORM.doc_id == doc_id))

                # 1) Ядро
                core_values = []
                for ln in lines:
                    position = getattr(ln, "position", None)
                    if position is None:
                        raise DatabaseError("Line is missing 'line_no'/'position'")

                    block_type = self._detect_block_type(ln)
                    content = getattr(ln, "content", "") or ""
                    core_values.append(
                        {
                            "doc_id": doc_id,
                            "position": int(position),
                            "block_type": block_type or "text",
                            "content": content,
                        }
                    )

                stmt_core = pg_insert(RawLineORM).values(core_values).returning(RawLineORM.id, RawLineORM.position)
                res = await uow.session.execute(stmt_core)
                inserted = res.fetchall()
                pos2id = {row.position: row.id for row in inserted}

                # 2) Детали
                doc_details_values: List[Dict[str, Any]] = []
                img_details_values: List[Dict[str, Any]] = []
                audio_details_values: List[Dict[str, Any]] = []

                for ln in lines:
                    position = getattr(ln, "line_no", None) or getattr(ln, "position", None)
                    line_id = pos2id.get(int(position))
                    block_type = self._detect_block_type(ln)

                    # document-details
                    page_idx = getattr(ln, "page_idx", None)
                    block_id = getattr(ln, "block_id", None)
                    sheet_name = getattr(ln, "sheet_name", None)
                    geometry = self._geometry_dict(ln)
                    hierarchy = getattr(ln, "hierarchy", None)
                    if any([page_idx is not None, block_id, sheet_name, geometry, hierarchy]):
                        doc_details_values.append(
                            {
                                "line_id": line_id,
                                "doc_id": doc_id,
                                "page_idx": page_idx,
                                "block_id": block_id,
                                "sheet_name": sheet_name,
                                "geometry": geometry,
                                "hierarchy": hierarchy,
                            }
                        )

                    # image-details
                    if self._is_image_line(block_type, ln):
                        status = getattr(ln, "status", None)
                        result_text = getattr(ln, "result_text", None)
                        ocr_text = getattr(ln, "ocr_text", None)
                        object_key = getattr(ln, "object_key", None)
                        filename = getattr(ln, "filename", None)
                        image_hash = getattr(ln, "image_hash", None)
                        img_details_values.append(
                            {
                                "line_id": line_id,
                                "doc_id": doc_id,
                                "status": status or "pending",
                                "result_text": result_text,
                                "ocr_text": ocr_text,
                                "object_key": object_key,
                                "filename": filename,
                                "image_hash": image_hash,
                            }
                        )

                    # audio-details
                    if self._is_audio_line(block_type, ln):
                        start_ts = getattr(ln, "start_ts", None)
                        end_ts = getattr(ln, "end_ts", None)
                        duration = getattr(ln, "duration", None)
                        speaker_label = getattr(ln, "speaker_label", None)
                        speaker_idx = getattr(ln, "speaker_idx", None)
                        confidence = getattr(ln, "confidence", None)
                        audio_details_values.append(
                            {
                                "line_id": line_id,
                                "doc_id": doc_id,
                                "start_ts": start_ts,
                                "end_ts": end_ts,
                                "duration": duration,
                                "speaker_label": speaker_label,
                                "speaker_idx": speaker_idx,
                                "confidence": confidence,
                            }
                        )

                # 3) Вставка деталей одной транзакцией
                await self._doc_repo.bulk_insert_in_session(uow.session, doc_details_values)
                await self._img_repo.bulk_insert_in_session(uow.session, img_details_values)
                await self._audio_repo.bulk_insert_in_session(uow.session, audio_details_values)

            except SQLAlchemyError as e:
                raise DatabaseError(f"Failed to save lines for document {doc_id}: {e}") from e

    async def update_lines(self, doc_id: UUID, block_id: str, new_content: str) -> bool:
        async for session in get_session(self._session_factory):
            try:
                q_ids = (
                    select(RawLineORM.id)
                    .join(DocumentLineORM, DocumentLineORM.line_id == RawLineORM.id)
                    .where(RawLineORM.doc_id == doc_id, DocumentLineORM.block_id == block_id)
                )
                rows = await session.execute(q_ids)
                line_ids = [r[0] for r in rows.fetchall()]
                if not line_ids:
                    await session.rollback()
                    return False

                # upsert в lines_image
                img_rows = [
                    {"line_id": lid, "doc_id": doc_id, "status": "done", "result_text": new_content}
                    for lid in line_ids
                ]
                stmt_upsert_img = (
                    pg_insert(ImageLineORM)
                    .values(img_rows)
                    .on_conflict_do_update(
                        index_elements=[ImageLineORM.line_id],
                        set_={
                            "doc_id": doc_id,
                            "status": "done",
                            "result_text": new_content,
                        },
                    )
                )
                await session.execute(stmt_upsert_img)

                # обновим plain-текст ядра
                await session.execute(
                    update(RawLineORM)
                    .where(RawLineORM.id.in_(line_ids))
                    .values(content=new_content)
                )

                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise DatabaseError(f"Failed to update image alt-text for block {block_id}: {e}") from e

    async def copy_lines(self, source_doc_id: UUID, target_doc_id: UUID):
        async for session in get_session(self._session_factory):
            try:
                src_stmt = (
                    select(RawLineORM)
                    .where(RawLineORM.doc_id == source_doc_id)
                    .order_by(RawLineORM.position)
                )
                src_core = (await session.execute(src_stmt)).scalars().all()
                if not src_core:
                    return

                core_values = [
                    {
                        "doc_id": target_doc_id,
                        "position": r.position,
                        "block_type": r.block_type,
                        "content": r.content,
                    }
                    for r in src_core
                ]
                insert_target = (
                    pg_insert(RawLineORM)
                    .values(core_values)
                    .returning(RawLineORM.id, RawLineORM.position)
                )
                inserted = (await session.execute(insert_target)).fetchall()
                pos2newid = {row.position: row.id for row in inserted}
                if not pos2newid:
                    await session.rollback()
                    raise DatabaseError("copy_lines: failed to insert target core rows")

                # lines_document
                src_doc_d = (
                    select(DocumentLineORM, RawLineORM.position)
                    .join(RawLineORM, RawLineORM.id == DocumentLineORM.line_id)
                    .where(RawLineORM.doc_id == source_doc_id)
                    .order_by(RawLineORM.position)
                )
                doc_rows = (await session.execute(src_doc_d)).all()
                if doc_rows:
                    doc_values = []
                    for d, pos in doc_rows:
                        new_line_id = pos2newid.get(pos)
                        if not new_line_id:
                            continue
                        doc_values.append(
                            {
                                "line_id": new_line_id,
                                "doc_id": target_doc_id,
                                "page_idx": d.page_idx,
                                "block_id": d.block_id,
                                "sheet_name": d.sheet_name,
                                "geometry": d.geometry,
                                "hierarchy": d.hierarchy,
                            }
                        )
                    if doc_values:
                        await session.execute(pg_insert(DocumentLineORM).values(doc_values))

                # lines_image
                src_img_d = (
                    select(ImageLineORM, RawLineORM.position)
                    .join(RawLineORM, RawLineORM.id == ImageLineORM.line_id)
                    .where(RawLineORM.doc_id == source_doc_id)
                )
                img_rows = (await session.execute(src_img_d)).all()
                if img_rows:
                    img_values = []
                    for img, pos in img_rows:
                        new_line_id = pos2newid.get(pos)
                        if not new_line_id:
                            continue
                        img_values.append(
                            {
                                "line_id": new_line_id,
                                "doc_id": target_doc_id,
                                "status": img.status,
                                "result_text": img.result_text,
                                "ocr_text": img.ocr_text,
                                "object_key": img.object_key,
                                "filename": img.filename,
                                "image_hash": img.image_hash,
                            }
                        )
                    if img_values:
                        await session.execute(pg_insert(ImageLineORM).values(img_values))

                # lines_audio
                src_audio_d = (
                    select(AudioLineORM, RawLineORM.position)
                    .join(RawLineORM, RawLineORM.id == AudioLineORM.line_id)
                    .where(RawLineORM.doc_id == source_doc_id)
                )
                audio_rows = (await session.execute(src_audio_d)).all()
                if audio_rows:
                    audio_values = []
                    for a, pos in audio_rows:
                        new_line_id = pos2newid.get(pos)
                        if not new_line_id:
                            continue
                        audio_values.append(
                            {
                                "line_id": new_line_id,
                                "doc_id": target_doc_id,
                                "start_ts": a.start_ts,
                                "end_ts": a.end_ts,
                                "duration": a.duration,
                                "speaker_label": a.speaker_label,
                                "speaker_idx": a.speaker_idx,
                                "confidence": a.confidence,
                                "emo_primary": a.emo_primary,
                                "emo_scores": a.emo_scores,
                            }
                        )
                    if audio_values:
                        await session.execute(pg_insert(AudioLineORM).values(audio_values))

                await session.commit()
                logger.info("Successfully copied %d lines from %s to %s", len(src_core), str(source_doc_id), str(target_doc_id))
            except SQLAlchemyError as e:
                await session.rollback()
                raise DatabaseError(f"Failed to copy lines: {e}") from e

    async def get_lines_for_document(self, doc_id: UUID) -> List[RawLineORM]:
        async for session in get_session(self._session_factory):
            stmt = (
                select(RawLineORM)
                .where(RawLineORM.doc_id == doc_id)
                .order_by(RawLineORM.position)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def list_all(self, doc_id: UUID | None = None) -> list[Line]:
        async for session in get_session(self._session_factory):
            q = select(RawLineORM)
            if doc_id:
                q = q.where(RawLineORM.doc_id == doc_id).order_by(RawLineORM.position)
            else:
                q = q.order_by(RawLineORM.doc_id, RawLineORM.position)
            rows = (await session.execute(q)).scalars().all()
            return [
                Line.model_validate(
                    {
                        "doc_id":       o.doc_id,
                        "block_id":     None,
                        "position":     o.position,
                        "type":         o.block_type,
                        "content":      o.content,
                    }
                )
                for o in rows
            ]

    async def get_line_core(self, line_id: UUID) -> Optional[RawLineORM]:
        async for session in get_session(self._session_factory):
            stmt = select(RawLineORM).where(RawLineORM.id == line_id)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def get_lines_for_document_joined(self, doc_id: UUID) -> list[dict]:
        async for session in get_session(self._session_factory):
            stmt = (
                select(RawLineORM, DocumentLineORM, ImageLineORM, AudioLineORM)
                .join(DocumentLineORM, DocumentLineORM.line_id == RawLineORM.id, isouter=True)
                .join(ImageLineORM, ImageLineORM.line_id == RawLineORM.id, isouter=True)
                .join(AudioLineORM, AudioLineORM.line_id == RawLineORM.id, isouter=True)
                .where(RawLineORM.doc_id == doc_id)
                .order_by(RawLineORM.position)
            )
            rows = (await session.execute(stmt)).all()

            enriched: list[dict] = []
            for raw, docd, imgd, audd in rows:
                enriched.append(
                    {
                        "line_id": str(raw.id),
                        "doc_id": str(raw.doc_id),
                        "position": raw.position,
                        "block_type": raw.block_type,
                        "content": raw.content,
                        "created_at": raw.created_at,

                        "page_idx": getattr(docd, "page_idx", None),
                        "block_id": getattr(docd, "block_id", None),
                        "sheet_name": getattr(docd, "sheet_name", None),
                        "geometry": getattr(docd, "geometry", None),
                        "hierarchy": getattr(docd, "hierarchy", None),

                        "image_status": getattr(imgd, "status", None),
                        "image_text": getattr(imgd, "result_text", None),
                        "image_ocr_text": getattr(imgd, "ocr_text", None),

                        "start_ts": getattr(audd, "start_ts", None),
                        "end_ts": getattr(audd, "end_ts", None),
                        "duration": getattr(audd, "duration", None),
                        "speaker_label": getattr(audd, "speaker_label", None),
                        "speaker_idx": getattr(audd, "speaker_idx", None),
                        "confidence": getattr(audd, "confidence", None),
                        "emo_primary": getattr(audd, "emo_primary", None),
                        "emo_scores": getattr(audd, "emo_scores", None),
                    }
                )
  
    async def upsert_image_result(self, line_id: UUID, doc_id: UUID, status: str, result_text: Optional[str]) -> bool:
        async for session in get_session(self._session_factory):
            try:
                stmt = (
                    pg_insert(ImageLineORM)
                    .values(
                        {
                            "line_id": line_id,
                            "doc_id": doc_id,
                            "status": status,
                            "result_text": result_text,
                        }
                    )
                    .on_conflict_do_update(
                        index_elements=[ImageLineORM.line_id],
                        set_={"doc_id": doc_id, "status": status, "result_text": result_text},
                    )
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise DatabaseError(f"upsert_image_result failed for line {line_id}: {e}") from e