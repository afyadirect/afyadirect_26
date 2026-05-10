# app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Optional, Any

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = "desc"