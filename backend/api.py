from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from flow import TravelPlannerFlow

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY environment variable not set. "
        "Create a .env file with: GOOGLE_API_KEY=your_key_here"
    )

app = FastAPI(
    title="Itinera Travel Planner API",
    description="AI-powered travel itinerary planning with budget validation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plans_store: Dict[str, Dict[str, Any]] = {}
jobs_store: Dict[str, Dict[str, Any]] = {}

class TravelRequest(BaseModel):
    interests: str = Field(..., min_length=3, max_length=200, description="User interests (e.g., 'culture, food, history')")
    budget: int = Field(..., gt=0, description="Total budget in INR")
    duration: int = Field(..., ge=1, le=30, description="Trip duration in days")
    start_city: str = Field(..., min_length=2, max_length=100, description="Departure city")
    season: str = Field(..., description="Travel season (summer/winter/monsoon/spring/autumn)")
    people: int = Field(..., ge=1, le=20, description="Number of travelers")
    currency: Optional[str] = Field("INR", description="Currency code")
    
    @validator('season')
    def validate_season(cls, v):
        valid_seasons = ['summer', 'winter', 'monsoon', 'spring', 'autumn']
        if v.lower() not in valid_seasons:
            raise ValueError(f'Season must be one of: {", ".join(valid_seasons)}')
        return v.lower()
    
    @validator('interests')
    def validate_interests(cls, v):
        if not v.strip():
            raise ValueError('Interests cannot be empty')
        return v.strip()

class PlanResponse(BaseModel):
    plan_id: str
    status: str
    destination: Optional[str] = None
    total_cost: Optional[int] = None
    budget_limit: int
    within_budget: Optional[bool] = None
    created_at: str
    message: Optional[str] = None
    plan_data: Optional[Dict[str, Any]] = None

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    message: Optional[str] = None
    plan_id: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

def generate_plan_sync(job_id: str, request: TravelRequest):
    """Background task to generate travel plan"""
    try:
        jobs_store[job_id]["status"] = "processing"
        
        flow = TravelPlannerFlow()
        plan = flow.run(request.dict())
        
        plan_id = str(uuid.uuid4())
        

        plans_store[plan_id] = {
            "plan_id": plan_id,
            "status": "completed",
            "destination": plan["destination"]["city"],
            "total_cost": plan["budget"]["total_cost"],
            "budget_limit": request.budget,
            "within_budget": plan["budget"]["within_budget"],
            "created_at": datetime.now().isoformat(),
            "plan_data": plan
        }
        

        jobs_store[job_id].update({
            "status": "completed",
            "plan_id": plan_id,
            "completed_at": datetime.now().isoformat()
        })
        

        plans_dir = Path("generated_plans")
        plans_dir.mkdir(exist_ok=True)
        with open(plans_dir / f"{plan_id}.json", "w") as f:
            json.dump(plan, f, indent=2)
            
    except ValueError as e:
        jobs_store[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
    except Exception as e:
        jobs_store[job_id].update({
            "status": "failed",
            "error": f"Unexpected error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })

@app.get("/")
def root():
    """API health check"""
    return {
        "service": "Itinera Travel Planner",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "POST /plan": "Create travel plan (async)",
            "GET /plan/{plan_id}": "Get plan by ID",
            "GET /job/{job_id}": "Check job status"
        }
    }

@app.post("/plan", response_model=JobStatus, status_code=202)
async def create_plan(request: TravelRequest, background_tasks: BackgroundTasks):
    """
    Create a travel plan (async processing)
    
    Returns a job ID to track the plan generation progress.
    """
    job_id = str(uuid.uuid4())
    
    jobs_store[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    background_tasks.add_task(generate_plan_sync, job_id, request)
    
    return JobStatus(
        job_id=job_id,
        status="pending",
        message="Plan generation started. Check /job/{job_id} for status.",
        created_at=jobs_store[job_id]["created_at"]
    )

@app.get("/job/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    """Check the status of a plan generation job"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        message=job.get("message"),
        plan_id=job.get("plan_id"),
        error=job.get("error"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at")
    )

@app.get("/plan/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str):
    """Retrieve a generated travel plan by ID"""
    if plan_id not in plans_store:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan = plans_store[plan_id]
    
    return PlanResponse(**plan)

@app.post("/plan/sync", response_model=PlanResponse)
def create_plan_sync(request: TravelRequest):
    """
    Create a travel plan (synchronous - may take 30-60 seconds)
    
    Use this for testing or when you need immediate results.
    For production, use the async /plan endpoint.
    """
    try:
        flow = TravelPlannerFlow()
        plan = flow.run(request.dict())
        
        plan_id = str(uuid.uuid4())
        
        result = {
            "plan_id": plan_id,
            "status": "completed",
            "destination": plan["destination"]["city"],
            "total_cost": plan["budget"]["total_cost"],
            "budget_limit": request.budget,
            "within_budget": plan["budget"]["within_budget"],
            "created_at": datetime.now().isoformat(),
            "plan_data": plan
        }
        
        plans_store[plan_id] = result
        
        plans_dir = Path("generated_plans")
        plans_dir.mkdir(exist_ok=True)
        with open(plans_dir / f"{plan_id}.json", "w") as f:
            json.dump(plan, f, indent=2)
        
        return PlanResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@app.get("/plans", response_model=list[dict])
def list_plans(limit: int = 10):
    """List all generated plans"""
    plans = list(plans_store.values())
    return plans[-limit:]  

@app.delete("/plan/{plan_id}")
def delete_plan(plan_id: str):
    """Delete a plan"""
    if plan_id not in plans_store:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    del plans_store[plan_id]
    
    plan_file = Path("generated_plans") / f"{plan_id}.json"
    if plan_file.exists():
        plan_file.unlink()
    
    return {"message": "Plan deleted", "plan_id": plan_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)