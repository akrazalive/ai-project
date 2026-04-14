from django.urls import path
from .views import JobListView, SavedJobListCreateView, SavedJobDeleteView, FetchJobsView
from .ai_views import AIMatchView, ResumeAnalyzeView

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('fetch/', FetchJobsView.as_view(), name='job-fetch'),
    path('saved/', SavedJobListCreateView.as_view(), name='saved-jobs'),
    path('saved/<int:pk>/', SavedJobDeleteView.as_view(), name='saved-job-delete'),
    path('ai/match/', AIMatchView.as_view(), name='ai-match'),
    path('ai/resume/', ResumeAnalyzeView.as_view(), name='ai-resume'),
]
