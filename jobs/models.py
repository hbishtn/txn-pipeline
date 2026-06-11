from xml.parsers.expat import model

from django.db import models

# Create your models here.

class Job(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    raw_count_raw = models.IntegerField(default=0)
    raw_count_clean = models.IntegerField(default=0)

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Job {self.id}"