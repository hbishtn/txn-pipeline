from google import genai
import json
import time
import os

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def classify_transactions(transactions_list):
    """
    Transactions ki list lo, categories return karo
    Batch mein kaam karta hai - ek call mein sab
    """
    if not transactions_list:
        return {}

    # Prompt banao
    txn_text = "\n".join([
        f"{i+1}. Merchant: {t['merchant']}, Amount: {t['amount']}, Notes: {t.get('notes', '')}"
        for i, t in enumerate(transactions_list)
    ])

    prompt = f"""
    Classify each transaction into ONE of these categories:
    Food, Shopping, Travel, Transport, Utilities, Cash Withdrawal, Entertainment, Other
    
    Transactions:
    {txn_text}
    
    Respond ONLY in JSON format like this:
    {{"1": "Food", "2": "Shopping", "3": "Travel"}}
    
    No extra text, only JSON.
    """

    # Retry logic - 3 baar try karo
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text.strip()

            # JSON clean karo
            text = text.replace('```json', '').replace('```', '').strip()
            result = json.loads(text)       
            return result

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s wait
            else:
                return {}  # Sab fail ho gaye toh empty return karo


def generate_summary(transactions_list, anomaly_count):
    """
    Poori transaction list ka narrative summary banao
    """
    total_inr = sum(t['amount'] for t in transactions_list if t['currency'] == 'INR')
    total_usd = sum(t['amount'] for t in transactions_list if t['currency'] == 'USD')

    # Top merchants
    merchant_spend = {}
    for t in transactions_list:
        m = t['merchant']
        merchant_spend[m] = merchant_spend.get(m, 0) + t['amount']
    top_merchants = sorted(merchant_spend, key=merchant_spend.get, reverse=True)[:3]

    prompt = f"""
    Analyze these financial transactions and give a JSON summary:
    
    - Total INR spend: {total_inr}
    - Total USD spend: {total_usd}
    - Top 3 merchants: {top_merchants}
    - Anomaly count: {anomaly_count}
    - Total transactions: {len(transactions_list)}
    
    Respond ONLY in this JSON format:
    {{
        "total_spend_inr": {total_inr},
        "total_spend_usd": {total_usd},
        "top_merchants": {top_merchants},
        "anomaly_count": {anomaly_count},
        "narrative": "2-3 sentence spending summary here",
        "risk_level": "low/medium/high"
    }}
    
    Only JSON, no extra text.
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
                )
            text = response.text.strip()
            text = text.replace('```json', '').replace('```', '').strip()
            result = json.loads(text)
            return result

        except Exception as e:
            print(f"ATTEMPT {attempt} FAILED: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return {
                    "total_spend_inr": total_inr,
                    "total_spend_usd": total_usd,
                    "top_merchants": top_merchants,
                    "anomaly_count": anomaly_count,
                    "narrative": "Summary generation failed.",
                    "risk_level": "low"
                }