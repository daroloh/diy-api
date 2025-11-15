from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorResponse(BaseModel):
    error: str
    code: int
    message: str
    fix: str
    timestamp: Optional[str] = None
    request_id: Optional[str] = None

class SlowResponse(BaseModel):
    status: str
    delay_seconds: int
    message: str

class RateLimitResponse(BaseModel):
    error: str
    code: int
    message: str
    retry_after: int
    limit: int
    remaining: int

class SuccessResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None