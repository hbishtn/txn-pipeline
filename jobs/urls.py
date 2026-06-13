from django.urls import path
from .views import UploadCSVView, JobStatusView, JobResultsView, JobListView

urlpatterns = [
    path('upload', UploadCSVView.as_view()),       # POST /jobs/upload
    path('<int:job_id>/status', JobStatusView.as_view()),  # GET /jobs/1/status
    path('<int:job_id>/results', JobResultsView.as_view()), # GET /jobs/1/results
    path('', JobListView.as_view()),               # GET /jobs
]