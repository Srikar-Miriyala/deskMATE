from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Job
from app.core.schema import JobResponse

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get job status and result"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        created_at=job.created_at
    )

@router.get("/")
async def list_jobs(db: Session = Depends(get_db)):
    """List all jobs"""
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return [{
        "job_id": j.job_id,
        "command": j.command,
        "status": j.status,
        "created_at": j.created_at
    } for j in jobs]