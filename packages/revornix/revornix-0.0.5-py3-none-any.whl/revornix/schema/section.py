from pydantic import BaseModel

class LabelAddRequest(BaseModel):
    name: str
    
class BaseSectionInfo(BaseModel):
    id: int
    title: str
    description: str
    
class AllMySectionsResponse(BaseModel):
    data: list[BaseSectionInfo]
        
class AllMySectionsResponse(BaseModel):
    data: list[BaseSectionInfo]
    
class SectionCreateRequest(BaseModel):
    title: str
    description: str
    public: bool
    cover: str | None = None
    labels: list[int]
    
class SectionCreateResponse(BaseModel):
    id: int