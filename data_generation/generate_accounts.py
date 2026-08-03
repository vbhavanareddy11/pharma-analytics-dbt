"""
generate_accounts.py
--------------------
Generates SALESFORCE.ACCOUNT — hospitals, hospital chains, independent
distributors, and clinics across the 14 APAC countries.

Handles the customer/distributor overlap explicitly:
  - Hospital Chains have children via PARENT_ID (self-ref)
  - Some accounts are flagged IS_DISTRIBUTOR (subset become SAP.DISTRIBUTOR)
  - Every account is assigned a Sales Rep from the users manifest

Output: data_generation/output/raw_salesforce_account.csv
        data_generation/output/_manifest_accounts.json
"""

import csv
import json
import random
import string
from pathlib import Path

from faker import Faker

from config import (
    SCALE,
    OUTPUT_DIR,
    RANDOM_SEED,
    COUNTRIES,
    COUNTRY_CODES,
    ACCOUNT_TYPES,
    ACCOUNT_TIERS,
)


# Realistic account type mix — most accounts are hospitals/clinics, few are chains
ACCOUNT_TYPE_WEIGHTS = {
    "Hospital": 0.55,
    "Clinic": 0.25,
    "Independent Distributor": 0.12,
    "Hospital Chain": 0.08,
}

TIER_WEIGHTS = [0.20, 0.45, 0.35]  # Tier 1 rare, Tier 2 most common
PAYMENT_TERMS = ["Net 30", "Net 60", "Net 90"]
PAYMENT_WEIGHTS = [0.50, 0.35, 0.15]


def _sf_id():
    """Salesforce-style 18-char ID, '001' prefix for Account."""
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=15))
    return f"001{suffix}"


def generate_accounts():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    # Load users manifest — need sales rep IDs to assign accounts to
    with (Path(OUTPUT_DIR) / "_manifest_users.json").open() as f:
        users_manifest = json.load(f)
    sales_rep_ids = users_manifest["sales_rep_ids"]

    target_rows = SCALE["accounts"]
    accounts = []

    # Pre-compute counts per account type
    type_counts = {
        t: round(target_rows * w) for t, w in ACCOUNT_TYPE_WEIGHTS.items()
    }
    drift = target_rows - sum(type_counts.values())
    type_counts["Hospital"] += drift

    # Step 1: build hospital chains first (parents need to exist before children)
    chain_ids_by_country = {c: [] for c in COUNTRIES}

    account_num = 1

    def _build_account(account_type, is_child_of=None):
        nonlocal account_num
        country = random.choice(COUNTRIES)
        country_code = COUNTRY_CODES[country]

        # Naming — realistic pharma customer patterns
        if account_type == "Hospital":
            name = f"{fake.city()} {random.choice(['General', 'Medical', 'University', 'Regional'])} Hospital"
        elif account_type == "Hospital Chain":
            name = f"{fake.last_name()} Healthcare Group"
        elif account_type == "Clinic":
            name = f"{fake.last_name()} {random.choice(['Family', 'Specialty', 'Diagnostic'])} Clinic"
        else:  # Independent Distributor
            name = f"{fake.company()} Medical Supply"

        # ~30% of hospitals also act as distributors (customer/distributor overlap)
        is_distributor = (
            account_type == "Independent Distributor"
            or (account_type == "Hospital" and random.random() < 0.30)
        )

        contract_start = fake.date_between(start_date="-6y", end_date="-6m")

        acct = {
            "ID": _sf_id(),
            "ACCOUNT_NUMBER": f"ACC-{country_code}-{account_num:06d}",
            "NAME": name,
            "ACCOUNT_TYPE": account_type,
            "IS_DISTRIBUTOR": is_distributor,
            "PARENT_ID": is_child_of,
            "TIER": random.choices(ACCOUNT_TIERS, weights=TIER_WEIGHTS)[0],
            "COUNTRY": country,
            "ZONE": f"APAC-{country_code}-{random.randint(1, 5):02d}",
            "CITY": fake.city(),
            "BILLING_ADDRESS": fake.street_address(),
            "PRIMARY_CONTACT_NAME": fake.name(),
            "PRIMARY_CONTACT_EMAIL": fake.email(),
            "PRIMARY_CONTACT_PHONE": fake.phone_number(),
            "ASSIGNED_SALES_REP_ID": random.choice(sales_rep_ids),
            "CONTRACT_START_DATE": contract_start.isoformat(),
            "PAYMENT_TERMS": random.choices(PAYMENT_TERMS, weights=PAYMENT_WEIGHTS)[0],
            "IS_ACTIVE": random.choices([True, False], weights=[0.94, 0.06])[0],
            "CREATED_DATE": fake.date_time_between(
                start_date=contract_start, end_date="now"
            ).isoformat(),
            "LAST_MODIFIED_DATE": fake.date_time_between(
                start_date="-6m", end_date="now"
            ).isoformat(),
            "IS_DELETED": False,
        }
        account_num += 1
        return acct

    # Chains first
    for _ in range(type_counts["Hospital Chain"]):
        chain = _build_account("Hospital Chain")
        accounts.append(chain)
        chain_ids_by_country[chain["COUNTRY"]].append(chain["ID"])

    # Hospitals — 20% chance of being a child of a chain in the same country
    for _ in range(type_counts["Hospital"]):
        acct = _build_account("Hospital")
        country_chains = chain_ids_by_country[acct["COUNTRY"]]
        if country_chains and random.random() < 0.20:
            acct["PARENT_ID"] = random.choice(country_chains)
        accounts.append(acct)

    # Clinics and independent distributors — no parent linkage
    for _ in range(type_counts["Clinic"]):
        accounts.append(_build_account("Clinic"))
    for _ in range(type_counts["Independent Distributor"]):
        accounts.append(_build_account("Independent Distributor"))

    # Write CSV
    output_path = Path(OUTPUT_DIR) / "raw_salesforce_account.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(accounts[0].keys()))
        writer.writeheader()
        writer.writerows(accounts)

    # Manifest — distinguish customers from distributors for downstream generators
    manifest = {
        "all_account_ids": [a["ID"] for a in accounts],
        "customer_ids": [a["ID"] for a in accounts if a["ACCOUNT_TYPE"] in ("Hospital", "Hospital Chain", "Clinic")],
        "distributor_account_ids": [a["ID"] for a in accounts if a["IS_DISTRIBUTOR"]],
        "count": len(accounts),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_accounts.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(accounts)} accounts → {output_path}")
    print(f"  Customers: {len(manifest['customer_ids'])}")
    print(f"  Distributors: {len(manifest['distributor_account_ids'])}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_accounts()