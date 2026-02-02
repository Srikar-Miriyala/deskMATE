from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables
from app.api import agent, files, jobs

# Create database tables
create_tables()

app = FastAPI(
    title="DeskMate AI Agent",
    description="Local-first AI Agent for file processing and task automation",
    version="1.0.0"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173", 
        "http://localhost:3000",  # Create React App
        "http://127.0.0.1:3000",
        "http://localhost:5174",  # Vite alternate
        "http://127.0.0.1:5174",
        "http://localhost:5175",  # Another Vite port
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])

@app.get("/")
async def root():
    return {"message": "DeskMate AI Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Add a simple test endpoint
@app.get("/test")
async def test_endpoint():
    return {"message": "Backend is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)