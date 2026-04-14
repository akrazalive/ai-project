from fastapi import APIRouter
from pydantic import BaseModel
from core.vector_store import get_vector_store, index_jobs

router = APIRouter()


class MatchRequest(BaseModel):
    query: str
    skills: list[str] = []
    top_k: int = 10


class MatchResult(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    score: float
    reason: str


class JobIndexItem(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str


@router.post("/", response_model=list[MatchResult])
def match_jobs(req: MatchRequest):
    store = get_vector_store()
    query = req.query
    if req.skills:
        query += " skills: " + ", ".join(req.skills)

    results = store.similarity_search_with_relevance_scores(query, k=req.top_k)

    output = []
    for doc, score in results:
        meta = doc.metadata
        output.append(MatchResult(
            job_id=meta.get("id", ""),
            title=meta.get("title", ""),
            company=meta.get("company", ""),
            location=meta.get("location", ""),
            score=round(score, 3),
            reason=f"Matched based on semantic similarity. Score: {round(score*100, 1)}%"
        ))
    return output


@router.post("/index")
def index_jobs_endpoint(jobs: list[JobIndexItem]):
    """Receive jobs from backend and add them to the vector store."""
    index_jobs([j.model_dump() for j in jobs])
    return {"indexed": len(jobs)}
