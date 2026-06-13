from rest_framework import serializers
from .models import Transaction, JobSummary


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class JobSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSummary
        fields = '__all__'