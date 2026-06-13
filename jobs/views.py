from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Job
from transactions.models import Transaction, JobSummary
from transactions.serializers import TransactionSerializer
from .tasks import process_csv_task
import os
from django.conf import settings

class UploadCSVView(APIView):
    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "CSV file required"}, status=400)

        if not file.name.endswith('.csv'):
            return Response({"error": "Only CSV files allowed"}, status=400)

        # for file save
        
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)


        job = Job.objects.create(
            filename=file.name,
            status="pending"
        )

        # Celery task
        process_csv_task.delay(job.id)

        return Response({
            "job_id": job.id,
            "filename": job.filename,
            "status": job.status
        }, status=201)


class JobStatusView(APIView):
    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        response = {
            "job_id": job.id,
            "status": job.status,
            "filename": job.filename,
            "created_at": job.created_at,
        }

        # Agar completed hai toh summary bhi do
        if job.status == "completed":
            try:
                summary = job.summary
                response["summary"] = {
                    "total_spend_inr": summary.total_spend_inr,
                    "total_spend_usd": summary.total_spend_usd,
                    "anomaly_count": summary.anomaly_count,
                    "risk_level": summary.risk_level,
                    "row_count_clean": job.row_count_clean,
                }
            except JobSummary.DoesNotExist:
                pass

        return Response(response)


class JobResultsView(APIView):
    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        if job.status != "completed":
            return Response({
                "error": f"Job abhi {job.status} hai, completed nahi hua"
            }, status=400)

        transactions = Transaction.objects.filter(job=job)
        anomalies = transactions.filter(is_anomaly=True)

        # Category wise spend
        category_spend = {}
        for txn in transactions:
            cat = txn.category or "Uncategorised"
            category_spend[cat] = category_spend.get(cat, 0) + float(txn.amount)

        try:
            summary = job.summary
            narrative_data = {
                "total_spend_inr": summary.total_spend_inr,
                "total_spend_usd": summary.total_spend_usd,
                "top_merchants": summary.top_merchants,
                "anomaly_count": summary.anomaly_count,
                "narrative": summary.narrative,
                "risk_level": summary.risk_level,
            }
        except JobSummary.DoesNotExist:
            narrative_data = {}

        return Response({
            "job_id": job.id,
            "transactions": TransactionSerializer(transactions, many=True).data,
            "anomalies": TransactionSerializer(anomalies, many=True).data,
            "category_spend": category_spend,
            "summary": narrative_data,
        })


class JobListView(APIView):
    def get(self, request):
        status_filter = request.query_params.get("status")

        jobs = Job.objects.all().order_by("-created_at")

        if status_filter:
            jobs = jobs.filter(status=status_filter)

        return Response([{
            "job_id": job.id,
            "filename": job.filename,
            "status": job.status,
            "row_count": job.row_count_raw,
            "created_at": job.created_at,
        } for job in jobs])