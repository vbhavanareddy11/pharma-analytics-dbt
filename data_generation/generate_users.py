"""
generate_users.py
-----------------
Generates SALESFORCE.USER — sales reps, field engineers, sales managers,
and regional service managers.

Uses config.USER_ROLE_WEIGHTS to produce a realistic commercial org shape
(sales-heavy at the base). Splits by role determine which columns are
populated: sales roles get COMMISSION_TIER, field engineers get
HOURLY_COST_RATE_USD. Both get BASE_SALARY_USD.

Output: data_generation/output/raw_salesforce_user.csv
        data_generation/output/_manifest_users.json
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
    USER_ROLES,
    USER_ROLE_WEIGHTS,
)


# -----------------------------------------------------------------------------
# Compensation ranges (USD) by role — realistic APAC pharma commercial org
# -----------------------------------------------------------------------------
BASE_SALARY_RANGE = {
    "Sales Rep": (35000, 65000),
    "Field Engineer": (30000, 55000),
    "Sales Manager": (75000, 120000),
    "Regional Service Manager": (70000, 110000),
}

# Field engineer hourly cost rate — used in profit calcs downstream
HOURLY_COST_RATE_RANGE = (25, 55)

# Sales rep commission tiers — A performs best, C is entry-level
COMMISSION_TIERS = ["Tier A", "Tier B", "Tier C"]
COMMISSION_TIER_WEIGHTS = [0.20, 0.50, 0.30]


def _sf_id():
    """Generate a Salesforce-style 18-char ID (alphanumeric, starts with '005' for User)."""
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=15))
    return f"005{suffix}"


def generate_users():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    target_rows = SCALE["users"]
    users = []

    # Pre-compute how many users of each role we need, based on the weights
    role_counts = {
        role: round(target_rows * weight)
        for role, weight in USER_ROLE_WEIGHTS.items()
    }
    # Adjust for rounding drift so total exactly matches target
    drift = target_rows - sum(role_counts.values())
    role_counts["Sales Rep"] += drift  # any leftover goes to the largest bucket

    # Managers first (so we can assign non-managers to them as reports)
    manager_ids_by_country = {c: [] for c in COUNTRIES}

    def _build_user(role, employee_id_num):
        first = fake.first_name()
        last = fake.last_name()
        country = random.choice(COUNTRIES)
        country_code = COUNTRY_CODES[country]
        assigned_zone = f"APAC-{country_code}-{random.randint(1, 5):02d}"

        base_salary = round(random.uniform(*BASE_SALARY_RANGE[role]), 2)
        hourly_rate = (
            round(random.uniform(*HOURLY_COST_RATE_RANGE), 2)
            if role == "Field Engineer" else None
        )
        commission_tier = (
            random.choices(COMMISSION_TIERS, weights=COMMISSION_TIER_WEIGHTS)[0]
            if role == "Sales Rep" else None
        )
        hire_date = fake.date_between(start_date="-8y", end_date="-6m")
        is_active = random.choices([True, False], weights=[0.92, 0.08])[0]
        termination_date = (
            fake.date_between(start_date=hire_date, end_date="today")
            if not is_active else None
        )

        return {
            "ID": _sf_id(),
            "EMPLOYEE_ID": f"EMP-{country_code}-{employee_id_num:05d}",
            "FIRST_NAME": first,
            "LAST_NAME": last,
            "EMAIL": f"{first.lower()}.{last.lower()}@pharmaco.example.com",
            "USER_ROLE": role,
            "PROFILE": "Manager" if "Manager" in role else "Standard User",
            "MANAGER_ID": None,   # filled in below for non-managers
            "ASSIGNED_ZONE": assigned_zone,
            "COUNTRY": country,
            "HIRE_DATE": hire_date.isoformat(),
            "TERMINATION_DATE": termination_date.isoformat() if termination_date else None,
            "HOURLY_COST_RATE_USD": hourly_rate,
            "COMMISSION_TIER": commission_tier,
            "BASE_SALARY_USD": base_salary,
            "IS_ACTIVE": is_active,
            "CREATED_DATE": fake.date_time_between(
                start_date=hire_date, end_date="now"
            ).isoformat(),
            "LAST_MODIFIED_DATE": fake.date_time_between(
                start_date="-6m", end_date="now"
            ).isoformat(),
            "IS_DELETED": False,
        }

    employee_id_num = 1

    # Step 1: build all managers first
    manager_roles = ["Sales Manager", "Regional Service Manager"]
    for role in manager_roles:
        for _ in range(role_counts[role]):
            u = _build_user(role, employee_id_num)
            users.append(u)
            manager_ids_by_country[u["COUNTRY"]].append(u["ID"])
            employee_id_num += 1

    # Step 2: build individual contributors, assigning them to a manager in their country
    ic_roles = ["Sales Rep", "Field Engineer"]
    for role in ic_roles:
        for _ in range(role_counts[role]):
            u = _build_user(role, employee_id_num)
            country_managers = manager_ids_by_country[u["COUNTRY"]]
            if country_managers:
                u["MANAGER_ID"] = random.choice(country_managers)
            users.append(u)
            employee_id_num += 1

    # -----------------------------------------------------------------------------
    # Write CSV
    # -----------------------------------------------------------------------------
    output_path = Path(OUTPUT_DIR) / "raw_salesforce_user.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(users[0].keys()))
        writer.writeheader()
        writer.writerows(users)

    # -----------------------------------------------------------------------------
    # Write manifest — downstream needs sales rep IDs, engineer IDs separately
    # -----------------------------------------------------------------------------
    manifest = {
        "sales_rep_ids": [u["ID"] for u in users if u["USER_ROLE"] == "Sales Rep"],
        "field_engineer_ids": [u["ID"] for u in users if u["USER_ROLE"] == "Field Engineer"],
        "manager_ids": [u["ID"] for u in users if "Manager" in u["USER_ROLE"]],
        "all_user_ids": [u["ID"] for u in users],
        "count": len(users),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_users.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(users)} users → {output_path}")
    print(f"  Sales Reps: {len(manifest['sales_rep_ids'])}")
    print(f"  Field Engineers: {len(manifest['field_engineer_ids'])}")
    print(f"  Managers: {len(manifest['manager_ids'])}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_users()