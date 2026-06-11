from django.db import models
from jobs.models import Job
# Create your models here.


class Transaction(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    txn_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    date = models.DateField()

    merchant = models.CharField(max_length=255)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(max_length=10)

    status = models.CharField(max_length=50)

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    account_id = models.CharField(max_length=100)

    is_anomaly = models.BooleanField(default=False)

    anomaly_reason = models.TextField(
        blank=True,
        null=True
    )

    llm_category = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    llm_failed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.txn_id or "No Txn ID"


class JobSummary(models.Model):

    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name="summary"
    )

    total_spend_inr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_spend_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    top_merchants = models.JSONField(
        default=list
    )

    anomaly_count = models.IntegerField(
        default=0
    )

    narrative = models.TextField()

    risk_level = models.CharField(
        max_length=20
    )

    def __str__(self):
        return f"Summary {self.job_id}"