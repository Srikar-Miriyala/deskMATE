from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import shutil
from app.db.database import get_db
from app.db.models import File as FileModel
from app.core.schema import FileUploadResponse

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a file for processing"""
    
    # Validate file type
    allowed_types = {'.pdf', '.txt'}  # Only PDF and TXT for now
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported. Only PDF and TXT files are supported.")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Store file metadata in database
    db_file = FileModel(
        filename=file.filename,
        file_path=file_path,
        file_type=file_extension
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return FileUploadResponse(
        filename=file.filename,
        file_path=file_path,
        message="File uploaded successfully"
    )

@router.get("/list")
async def list_uploaded_files(db: Session = Depends(get_db)):
    """List all uploaded files"""
    files = db.query(FileModel).all()
    return [{"filename": f.filename, "file_path": f.file_path, "uploaded_at": f.uploaded_at} for f in files]