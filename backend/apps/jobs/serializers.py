from rest_framework import serializers
from .models import Job, SavedJob


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source='job', write_only=True
    )

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_id', 'match_score', 'match_reason', 'saved_at']
        read_only_fields = ['id', 'saved_at']
