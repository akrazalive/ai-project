from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .scraper import search_jobs, COUNTRY_KEYWORDS


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "is_admin": request.user.is_staff or request.user.is_superuser,
        })


class JobSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"countries": list(COUNTRY_KEYWORDS.keys())})

    def post(self, request):
        role = request.data.get("role", "").strip()
        countries = request.data.get("countries", [])

        if not role:
            return Response({"error": "role is required"}, status=400)

        data = search_jobs(role, countries)
        return Response({
            "query": data.get("query", ""),
            "count": len(data.get("results", [])),
            "jobs": data.get("results", []),
        })
