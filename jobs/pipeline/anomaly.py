import numpy as np

# Ye merchants sirf India mein hain — USD mein nahi hone chahiye
DOMESTIC_MERCHANTS = ['swiggy', 'ola', 'irctc', 'zomato', 'flipkart', 'bigbasket']


def detect_anomalies(df):
    reasons = []

    for idx, row in df.iterrows():
        reason = []

        # Check 1 - Amount 3x median se zyada hai account ka
        account_txns = df[df['account_id'] == row['account_id']]['amount']
        median_amount = account_txns.median()

        if row['amount'] > 3 * median_amount:
            reason.append(f"Amount {row['amount']} is 3x account median {round(median_amount, 2)}")

        # Check 2 - USD currency but domestic merchant
        if row['currency'] == 'USD':
            merchant_lower = str(row['merchant']).lower()
            for domestic in DOMESTIC_MERCHANTS:
                if domestic in merchant_lower:
                    reason.append(f"USD currency with domestic merchant {row['merchant']}")
                    break

        reasons.append(", ".join(reason) if reason else "")

    df['is_anomaly'] = [bool(r) for r in reasons]
    df['anomaly_reason'] = reasons

    return df