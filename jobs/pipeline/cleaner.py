import pandas as pd
from datetime import datetime


def clean_csv(file_path):
    df = pd.read_csv(file_path)

    # Step 1 - Duplicate rows hatao
    df = df.drop_duplicates()

    # Step 2 - Date normalize karo (DD-MM-YYYY aur YYYY/MM/DD dono handle)
    def parse_date(val):
        for fmt in ("%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(val), fmt).date().isoformat()
            except:
                pass
        return None

    df['date'] = df['date'].apply(parse_date)

    # Step 3 - Amount se $ hatao
    df['amount'] = df['amount'].astype(str).str.replace('$', '', regex=False).str.strip()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Step 4 - Currency uppercase karo
    df['currency'] = df['currency'].str.upper().str.strip()

    # Step 5 - Status uppercase karo
    df['status'] = df['status'].str.upper().str.strip()

    # Step 6 - Missing category fill karo
    df['category'] = df['category'].fillna('Uncategorised').str.strip()
    df['category'] = df['category'].replace('', 'Uncategorised')

    # Step 7 - txn_id missing rows ko handle karo
    df['txn_id'] = df['txn_id'].fillna('').str.strip()

    # Step 8 - Invalid rows hatao (amount NaN ya date None)
    df = df.dropna(subset=['amount', 'date'])

    return df