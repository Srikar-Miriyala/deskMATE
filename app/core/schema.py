from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Intent(BaseModel):
    intent: str
    target: Optional[str] = None
    steps: List[Dict[str, Any]]
    confirmation_required: bool = False
    assumptions: List[str] = []
    clarification_question: Optional[str] = None

class ActionStep(BaseModel):
    action: str
    params: Dict[str, Any]

class ExecutionResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None

class JobCreate(BaseModel):
    command: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    created_at: datetime

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    message: str