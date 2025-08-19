from pydantic import BaseModel

class CreateLabelResponse(BaseModel):
    id: int
    name: str
    
class LabelAddRequest(BaseModel):
    name: str
    
class Label(BaseModel):
    id: int
    name: str

class LabelListResponse(BaseModel):
    data: list[Label]
    
class CreateLabelResponse(BaseModel):
    id: int
    name: str
    
class LabelAddRequest(BaseModel):
    name: str

class DocumentCreateResponse(BaseModel):
    document_id: int  
  
class FileDocumentParameters(BaseModel):
    title: str | None = None
    description: str | None = None
    sections: list[int]
    auto_summary: bool
    labels: list[int] | None = None
    cover: str | None = None
    file_name: str | None = None

class WebsiteDocumentParameters(BaseModel):
    title: str | None = None
    description: str | None = None
    sections: list[int]
    auto_summary: bool
    labels: list[int] | None = None
    cover: str | None = None
    url: str | None = None


class QuickNoteDocumentParameters(BaseModel):
    title: str | None = None
    description: str | None = None
    sections: list[int]
    auto_summary: bool
    labels: list[int] | None = None
    cover: str | None = None
    content: str | None = None