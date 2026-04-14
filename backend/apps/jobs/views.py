from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Job, SavedJob
from .serializers import JobSerializer, SavedJobSerializer
from .tasks import fetch_remotive_jobs


class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'company', 'location', 'description']


class SavedJobListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedJobDeleteView(generics.DestroyAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)


class FetchJobsView(APIView):
    """Trigger a Celery task to fetch and index jobs."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = request.data.get('role', 'developer')
        fetch_remotive_jobs.delay(role)
        return Response({'message': f'Job fetch started for role: {role}'})
