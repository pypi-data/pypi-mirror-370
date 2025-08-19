from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Dict, Optional


class ESLine(BaseModel):
    line_id: str
    doc_id: str
    text_content: str | None = None
    block_type: str | None = None
    position: int | None = None
    page_idx: int | None = None
    hierarchy: str | None = None
    vector: List[float] | None = None
    source_line_id: str | None = None
    
    
class RawLine(BaseModel):
    """Базовая модель, соответствующая таблице raw_lines."""
    id: UUID
    doc_id: UUID
    position: int
    type: str = Field(alias="block_type")
    content: str
    
    class Config:
        from_attributes = True 
        populate_by_name = True 
    
class DocumentLineDetails(BaseModel):
    """Детали для текстовых/структурных блоков."""
    page_idx: Optional[int] = None
    block_id: Optional[str] = None
    polygon: List[List[float]] | None = None  # Координаты 4-х углов блока [[x1,y1], [x2,y2], ...]
    bbox: List[float] | None = None          # Ограничивающий прямоугольник [x_min, y_min, x_max, y_max]
    hierarchy: Optional[Dict[int, str]] = None
    class Config:
        from_attributes = True 
        populate_by_name = True # Разрешает использовать и 'line_no', и 'position'
     
class ImageLineDetails(BaseModel):
    """Детали для изображений."""
    result_text: Optional[str] = None
    ocr_text: Optional[str] = None
    class Config:
        from_attributes = True 
        populate_by_name = True
        
class AudioLineDetails(BaseModel):
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None
    duration: Optional[float] = None
    speaker_label: Optional[str] = None
    speaker_idx: Optional[int] = None
    confidence: Optional[float] = None
    emo_primary: Optional[str] = None
    emo_scores: Optional[dict] = None

    tasks: Optional[dict] = None # например {"tasks":["transcribe","diarization","emotion"]}

    model_config = {"from_attributes": True}

# Единая модель для входных и выходных данных
class EnrichedLine(RawLine, DocumentLineDetails, ImageLineDetails, AudioLineDetails):   
    pass

Line = EnrichedLine # Используем EnrichedLine как основной тип