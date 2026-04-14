import asyncio
import httpx
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="AI Job Search - Job Fetcher", version="1.0.0")


class JobItem(BaseModel):
    title: str
    company: str
    location: str
    description: str
    tags: list[str]
    url: str
    source: str


async def fetch_remotive(role: str, client: httpx.AsyncClient) -> list[JobItem]:
    url = f"https://remotive.com/api/remote-jobs?search={role}&limit=50"
    resp = await client.get(url, timeout=15)
    resp.raise_for_status()
    jobs = []
    for j in resp.json().get("jobs", []):
        jobs.append(JobItem(
            title=j["title"],
            company=j["company_name"],
            location=j.get("candidate_required_location", "Remote"),
            description=j.get("description", "")[:500],
            tags=j.get("tags", []),
            url=j["url"],
            source="remotive",
        ))
    return jobs


@app.get("/jobs", response_model=list[JobItem])
async def get_jobs(role: str = Query("developer"), location: str = Query("")):
    async with httpx.AsyncClient() as client:
        results = await fetch_remotive(role, client)
    if location:
        loc = location.lower()
        results = [j for j in results if loc in j.location.lower() or "remote" in j.location.lower()]
    return results


@app.get("/health")
def health():
    return {"status": "ok"}
