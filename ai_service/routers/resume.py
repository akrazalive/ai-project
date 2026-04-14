from fastapi import APIRouter
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str


class ResumeAnalyzeResponse(BaseModel):
    match_score: float          # 0-100
    missing_keywords: list[str]
    suggestions: list[str]


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
def analyze_resume(req: ResumeAnalyzeRequest):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([req.resume_text, req.job_description])
    score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100

    # Find keywords in JD missing from resume
    jd_words = set(req.job_description.lower().split())
    resume_words = set(req.resume_text.lower().split())
    missing = list(jd_words - resume_words)[:15]

    suggestions = []
    if score < 40:
        suggestions.append("Your resume has low overlap with this job. Consider tailoring it.")
    if missing:
        suggestions.append(f"Consider adding these keywords: {', '.join(missing[:8])}")
    if score >= 70:
        suggestions.append("Strong match! Make sure your experience section highlights relevant projects.")

    return ResumeAnalyzeResponse(
        match_score=round(score, 2),
        missing_keywords=missing,
        suggestions=suggestions,
    )
