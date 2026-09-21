from pydantic import BaseModel, Field
from typing import Any, Optional

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: Optional[str] = None
    document_ids: list[str] = []
    image_data_url: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    agent: str
    citations: list[dict[str, Any]] = []
    conversation_id: str

class RouteRequest(BaseModel):
    message: str

class UploadResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    pages: int = 0
