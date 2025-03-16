from pydantic import BaseModel, Field


class NoteSchema(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    content: str = Field(min_length=10, max_length=100000)
    priority: int = Field(0, ge=0, le=100)


class NoteResponseSchema(BaseModel):
    id: int = Field(ge=0)
    title: str = Field(min_length=5, max_length=100)
    content: str = Field(min_length=10, max_length=100000)
    priority: int = Field(0, ge=0, le=100)
    user_email: str = Field(min_length=5, max_length=100)

    class Config:
        orm_mode = True


class NoteUpdateSchema(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    content: str = Field(min_length=10, max_length=100000)
    priority: int = Field(0, ge=0, le=100)