from django.urls import path
from .views import JobListView, SavedJobListCreateView, SavedJobDeleteView

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('saved/', SavedJobListCreateView.as_view(), name='saved-jobs'),
    path('saved/<int:pk>/', SavedJobDeleteView.as_view(), name='saved-job-delete'),
]
