from celery import shared_task
from django.utils import timezone
import os
from django.conf import settings

from .models import Job
from transactions.models import Transaction, JobSummary
from .pipeline.cleaner import clean_csv
from .pipeline.anomaly import detect_anomalies
from .pipeline.llm import classify_transactions, generate_summary


@shared_task
def process_csv_task(job_id):
    try:
        job = Job.objects.get(id=job_id)
        job.status = "processing"
        job.save()

        # File path
        file_path = os.path.join(settings.MEDIA_ROOT, job.filename)

        # ── Step 1: Data Clean ──────────────────────
        df = clean_csv(file_path)
        job.row_count_raw = len(df) 

        # ── Step 2: Anomaly Detection ───────────────
        df = detect_anomalies(df)

        # ── Step 3: DB mein save karo ───────────────
        Transaction.objects.filter(job=job).delete()

        transactions_to_create = []
        for _, row in df.iterrows():
            transactions_to_create.append(Transaction(
                job=job,
                txn_id=row.get('txn_id') or '',
                date=row['date'],
                merchant=row['merchant'],
                amount=row['amount'],
                currency=row['currency'],
                status=row['status'],
                category=row.get('category') or 'Uncategorised',
                account_id=row.get('account_id') or '',
                is_anomaly=row['is_anomaly'],
                anomaly_reason=row['anomaly_reason'],
            ))

        Transaction.objects.bulk_create(transactions_to_create)
        job.row_count_clean = len(transactions_to_create)

        # ── Step 4: LLM Classification ──────────────
        # Sirf wo transactions jinki category nahi hai
        uncategorised = df[
            df['category'].isin(['Uncategorised', '', 'uncategorised'])
        ]

        if not uncategorised.empty:
            txn_list = uncategorised[['merchant', 'amount', 'notes']].to_dict('records') \
                if 'notes' in uncategorised.columns \
                else uncategorised[['merchant', 'amount']].to_dict('records')

            categories = classify_transactions(txn_list)

            # LLM categories save karo
            for i, (db_idx, row) in enumerate(uncategorised.iterrows()):
                llm_cat = categories.get(str(i + 1), '')
                if llm_cat:
                    Transaction.objects.filter(
                        job=job,
                        txn_id=row.get('txn_id') or ''
                    ).update(
                        llm_category=llm_cat,
                        category=llm_cat
                    )

        # ── Step 5: LLM Summary ─────────────────────
        all_txns = Transaction.objects.filter(job=job)
        txn_data = [{
            'merchant': t.merchant,
            'amount': float(t.amount),
            'currency': t.currency,
        } for t in all_txns]

        anomaly_count = all_txns.filter(is_anomaly=True).count()
        summary_data = generate_summary(txn_data, anomaly_count)

        # Summary save karo
        JobSummary.objects.update_or_create(
            job=job,
            defaults={
                'total_spend_inr': summary_data.get('total_spend_inr', 0),
                'total_spend_usd': summary_data.get('total_spend_usd', 0),
                'top_merchants': summary_data.get('top_merchants', []),
                'anomaly_count': anomaly_count,
                'narrative': summary_data.get('narrative', ''),
                'risk_level': summary_data.get('risk_level', 'low'),
            }
        )

        # ── Done ────────────────────────────────────
        job.status = "completed"
        job.completed_at = timezone.now()
        job.save()

    except Exception as e:
        job = Job.objects.get(id=job_id)
        job.status = "failed"
        job.error_message = str(e)
        job.save()
        raise e