"""
generate_distributors.py
------------------------
Generates SAP.DISTRIBUTOR — the supply chain / financial view of distributors.

Each row bridges back to SALESFORCE.ACCOUNT via SALESFORCE_ACCOUNT_ID.
Realistic quirk: distributor name in SAP may not exactly match Salesforce name
(same entity, two systems, slightly different data entry). Downstream staging
must handle this reconciliation.

Output: data_generation/output/raw_sap_distributor.csv
        data_generation/output/_manifest_distributors.json
"""

import csv
import json
import random
from pathlib import Path

from faker import Faker

from config import SCALE, OUTPUT_DIR, RANDOM_SEED


CREDIT_LIMIT_RANGE = (50_000, 2_000_000)
PAYMENT_TERMS_DAYS = [30, 60, 90]
PAYMENT_TERMS_WEIGHTS = [0.50, 0.35, 0.15]
SHIPPING_COST_RANGE = (150, 1200)
QUALITY_CERTIFICATIONS = ["ISO 13485", "ISO 9001", "ISO 13485 + ISO 9001"]
CERT_WEIGHTS = [0.50, 0.15, 0.35]


def generate_distributors():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    # Load accounts manifest — every SAP distributor bridges to a Salesforce account
    with (Path(OUTPUT_DIR) / "_manifest_accounts.json").open() as f:
        accounts_manifest = json.load(f)
    distributor_account_ids = accounts_manifest["distributor_account_ids"]

    # Also load the account CSV so we can pull country + name for the bridge
    account_lookup = {}
    with (Path(OUTPUT_DIR) / "raw_salesforce_account.csv").open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ID"] in distributor_account_ids:
                account_lookup[row["ID"]] = {
                    "name": row["NAME"],
                    "country": row["COUNTRY"],
                }

    # Cap at SCALE["distributors"] — SAP only knows about the subset with vendor contracts
    target_rows = min(SCALE["distributors"], len(distributor_account_ids))
    chosen_account_ids = random.sample(distributor_account_ids, target_rows)

    distributors = []
    for i, account_id in enumerate(chosen_account_ids, start=1):
        sf_name = account_lookup[account_id]["name"]
        country = account_lookup[account_id]["country"]

        # Realistic name mismatch — SAP entry sometimes uses different casing/abbrev
        if random.random() < 0.20:
            sap_name = sf_name.upper()  # SAP-style all caps in ~20% of cases
        else:
            sap_name = sf_name

        contract_start = fake.date_between(start_date="-5y", end_date="-1y")
        contract_end = (
            fake.date_between(start_date="+6m", end_date="+3y")
            if random.random() < 0.40 else None   # 60% are open-ended contracts
        )
        license_expiry = fake.date_between(start_date="+3m", end_date="+3y")

        distributors.append({
            "DISTRIBUTOR_ID": i,
            "SAP_VENDOR_CODE": f"VN-{i:06d}",
            "SALESFORCE_ACCOUNT_ID": account_id,
            "DISTRIBUTOR_NAME": sap_name,
            "COUNTRY": country,
            "WAREHOUSE_LOCATION": fake.city(),
            "WAREHOUSE_CAPACITY_UNITS": random.randint(500, 20_000),
            "CREDIT_LIMIT_USD": round(random.uniform(*CREDIT_LIMIT_RANGE), 2),
            "PAYMENT_TERMS_DAYS": random.choices(PAYMENT_TERMS_DAYS, weights=PAYMENT_TERMS_WEIGHTS)[0],
            "SHIPPING_COST_PER_ORDER_USD": round(random.uniform(*SHIPPING_COST_RANGE), 2),
            "REGULATORY_LICENSE_NUMBER": f"MD-{country[:2].upper()}-{random.randint(100000, 999999)}",
            "LICENSE_EXPIRY_DATE": license_expiry.isoformat(),
            "QUALITY_CERTIFICATION": random.choices(QUALITY_CERTIFICATIONS, weights=CERT_WEIGHTS)[0],
            "IS_APPROVED_VENDOR": random.choices([True, False], weights=[0.95, 0.05])[0],
            "CONTRACT_START_DATE": contract_start.isoformat(),
            "CONTRACT_END_DATE": contract_end.isoformat() if contract_end else None,
            "CREATED_AT": fake.date_time_between(
                start_date=contract_start, end_date="now"
            ).isoformat(),
            "UPDATED_AT": fake.date_time_between(
                start_date="-6m", end_date="now"
            ).isoformat(),
        })

    output_path = Path(OUTPUT_DIR) / "raw_sap_distributor.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(distributors[0].keys()))
        writer.writeheader()
        writer.writerows(distributors)

    manifest = {
        "distributor_ids": [d["DISTRIBUTOR_ID"] for d in distributors],
        "salesforce_account_ids": [d["SALESFORCE_ACCOUNT_ID"] for d in distributors],
        "count": len(distributors),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_distributors.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(distributors)} distributors → {output_path}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_distributors()