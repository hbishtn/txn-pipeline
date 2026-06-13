from django.db import models

class Job(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    row_count_raw = models.IntegerField(default=0)   # ← "raw_count_raw" tha, typo fix
    row_count_clean = models.IntegerField(default=0) # ← ye bhi wrong tha

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # ← blank/null nahi, auto hoga
    completed_at = models.DateTimeField(blank=True, null=True)  # ← ye missing tha

    def __str__(self):
        return f"Job {self.id} - {self.status}"