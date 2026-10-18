from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
from case_graph import case_graph
from case_manager import (
    initialize_db,
    create_case,
    get_case,
)
from redis_cache import get_case_cached
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    initialize_db()
    yield
app = FastAPI(
    title="Support Case Management API",
    lifespan=lifespan,
)
class CaseCreateRequest(BaseModel):
    description: str = Field(min_length=1)



@app.post("/cases")
def create_support_case(request: CaseCreateRequest):

    try:
        result = case_graph.invoke({'task_id':str(uuid.uuid4()),'description': request.description})

        if result.get('error'):
            raise HTTPException(status_code=400,detail=result['error'])
        return {
            'case':result['case_record'],
            'a2a_response':result['agent_result']
        }        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/cases/{case_id}")
def fetch_case(case_id: str):

    case = get_case_cached(case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return case