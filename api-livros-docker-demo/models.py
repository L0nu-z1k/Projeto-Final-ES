from pydantic import BaseModel, Field


class LivroCriar(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    ano: int = Field(..., ge=0, le=2100)
    isbn: str = Field(..., min_length=1)


class LivroAtualizar(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    ano: int = Field(..., ge=0, le=2100)
    isbn: str = Field(..., min_length=1)


class Livro(BaseModel):
    id: int
    titulo: str
    autor: str
    ano: int
    isbn: str
