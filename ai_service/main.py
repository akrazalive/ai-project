from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import match, resume

app = FastAPI(title="AI Job Search - AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match.router, prefix="/match", tags=["Job Matching"])
app.include_router(resume.router, prefix="/resume", tags=["Resume"])


@app.get("/health")
def health():
    return {"status": "ok"}
