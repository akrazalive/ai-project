import httpx
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status


AI_SERVICE_URL = getattr(settings, 'AI_SERVICE_URL', 'http://ai_service:8002')


class AIMatchView(APIView):
    """Proxy to AI service: semantic job matching."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payload = {
            "query": request.data.get("query", ""),
            "skills": request.data.get("skills", []),
            "top_k": request.data.get("top_k", 10),
        }
        try:
            resp = httpx.post(f"{AI_SERVICE_URL}/match/", json=payload, timeout=15)
            resp.raise_for_status()
            return Response(resp.json())
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class ResumeAnalyzeView(APIView):
    """Proxy to AI service: resume vs job description analysis."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payload = {
            "resume_text": request.data.get("resume_text", ""),
            "job_description": request.data.get("job_description", ""),
        }
        try:
            resp = httpx.post(f"{AI_SERVICE_URL}/resume/analyze", json=payload, timeout=15)
            resp.raise_for_status()
            return Response(resp.json())
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
