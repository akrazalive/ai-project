import httpx
from celery import shared_task
from django.conf import settings
from .models import Job


@shared_task
def fetch_remotive_jobs(role: str = "developer"):
    """Fetch jobs from Remotive public API and index them in the vector store."""
    url = f"https://remotive.com/api/remote-jobs?search={role}&limit=50"
    try:
        resp = httpx.get(url, timeout=15)
        resp.raise_for_status()
        jobs_data = resp.json().get("jobs", [])
        created_jobs = []
        for j in jobs_data:
            obj, is_new = Job.objects.get_or_create(
                source_url=j["url"],
                defaults={
                    "title": j["title"],
                    "company": j["company_name"],
                    "location": j.get("candidate_required_location", "Remote"),
                    "description": j.get("description", ""),
                    "skills_required": j.get("tags", []),
                    "source": "remotive",
                }
            )
            if is_new:
                created_jobs.append(obj)

        # Push new jobs to AI service vector store
        if created_jobs:
            index_jobs_in_vector_store.delay([
                {
                    "id": str(j.id),
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "description": j.description,
                }
                for j in created_jobs
            ])

        return f"Fetched {len(jobs_data)} jobs, created {len(created_jobs)} new."
    except Exception as e:
        return f"Error: {e}"


@shared_task
def index_jobs_in_vector_store(jobs: list):
    """Send jobs to AI service for vector indexing."""
    ai_url = getattr(settings, 'AI_SERVICE_URL', 'http://ai_service:8002')
    try:
        resp = httpx.post(f"{ai_url}/match/index", json=jobs, timeout=30)
        resp.raise_for_status()
        return f"Indexed {len(jobs)} jobs in vector store."
    except Exception as e:
        return f"Vector index error: {e}"
