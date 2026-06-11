from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job


class UploadCSVView(APIView):

    def post(self, request):

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "CSV file required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        job = Job.objects.create(
            filename=file.name,
            status="pending"
        )

        return Response(
            {
                "job_id": job.id,
                "filename": file.name,
                "status": job.status
            }
        )