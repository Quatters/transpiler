from pydantic import BaseModel


class Code(BaseModel):
    code: str


class TranspileResult(BaseModel):
    success: bool
    result: str
