from typing import Any, Dict, List
from pydantic import BaseModel


class Chunk(BaseModel):
    original_text: str
    concise_summary: str
    question: str
    answer: str


class Message(BaseModel):
    role: str
    content: str


class Document(BaseModel):
    page_number: int
    chunks: List[Chunk] = []


class MarkdownifyRequest(BaseModel):
    url: str
    page_number: int = 1
    temperature: float = 0.0
    max_tokens: int = 8192
    include_image_captioning: bool = False


class MarkdownifyResponse(BaseModel):
    markdown: str


class ChunksRequest(BaseModel):
    text: str
    temperature: float = 0.0
    max_tokens: int = 8192


class ChunksResponse(BaseModel):
    chunks: List[Chunk] = []


class DocumentsRequest(BaseModel):
    url: str
    page_number: int = 1
    temperature: float = 0.0
    max_tokens: int = 8192
    include_image_captioning: bool = False


class DocumentsResponse(BaseModel):
    documents: List[Document]


class MemoriesRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.0
    max_tokens: int = 8192


class MemoriesResponse(BaseModel):
    memories: Dict[str, Any]
