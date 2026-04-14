from django.db import models
from django.conf import settings


class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.JSONField(default=list)
    experience_years = models.FloatField(default=0)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    source_url = models.URLField()
    source = models.CharField(max_length=50)  # e.g. 'remotive', 'adzuna'
    posted_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fetched_at']

    def __str__(self):
        return f"{self.title} @ {self.company}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    match_score = models.FloatField(default=0)
    match_reason = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']
