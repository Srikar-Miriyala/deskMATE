from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.schema import JobCreate
from app.core.agent_core import DeskMateAgent
from app.db.database import get_db
from app.db.models import Job
import uuid
import json

router = APIRouter()
agent = DeskMateAgent()

@router.post("/query")
async def process_agent_query(request: JobCreate, db: Session = Depends(get_db)):
    """Process a natural language command through the agent"""
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Process command
    result = agent.process_command(request.command)
    
    # Store job in database
    db_job = Job(
        job_id=job_id,
        command=request.command,
        intent=result["intent"]["intent"],
        status="completed",
        result=json.dumps(result)
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Return the complete result
    return {
        **result,
        "job_id": job_id,
        "status": "completed",
        "created_at": db_job.created_at.isoformat()
    }

@router.get("/intent/{command}")
async def parse_intent_only(command: str):
    """Parse command intent without execution (for testing)"""
    intent = agent.llm_client.parse_intent(command)
    return intent.dict()