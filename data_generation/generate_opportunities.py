"""
generate_opportunities.py
-------------------------
Generates SALESFORCE.OPPORTUNITY — the sales fact source.

Each row is one device sold to one customer by one sales rep. Every row has a
unique DEVICE_SERIAL_NUMBER — the join key that makes install-base and
warranty logic work downstream in the service ticket data.

Business rules encoded:
  - Sale price = list price × (1 - discount%), realistic discount distribution
  - Warranty end date derived from close date + product's warranty months
  - Install dates only populated for products where REQUIRES_HW/SW_INSTALL = True
    (with ~10% of installs pending, mirroring real ops SLA misses)
  - Only active products (IS_ACTIVE=True) appear in new sales

Output: data_generation/output/raw_salesforce_opportunity.csv
        data_generation/output/_manifest_opportunities.json
"""

import csv
import json
import random
import string
from datetime import timedelta
from pathlib import Path

from faker import Faker

from config import (
    SCALE,
    OUTPUT_DIR,
    RANDOM_SEED,
    DATA_START_DATE,
    DATA_END_DATE,
)


# Discount tiers — most sales at low discount, aggressive discounts rare
DISCOUNT_RANGES = [(0.0, 0.05), (0.05, 0.15), (0.15, 0.25), (0.25, 0.40)]
DISCOUNT_WEIGHTS = [0.35, 0.40, 0.20, 0.05]

PAYMENT_TERMS = ["Net 30", "Net 60", "Net 90"]
PAYMENT_TERMS_WEIGHTS = [0.50, 0.35, 0.15]


def _sf_id():
    """Salesforce-style 18-char ID, '006' prefix for Opportunity."""
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=15))
    return f"006{suffix}"


def generate_opportunities():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    # Load manifests
    with (Path(OUTPUT_DIR) / "_manifest_users.json").open() as f:
        users_manifest = json.load(f)
    sales_rep_ids = users_manifest["sales_rep_ids"]

    with (Path(OUTPUT_DIR) / "_manifest_accounts.json").open() as f:
        accounts_manifest = json.load(f)
    customer_ids = accounts_manifest["customer_ids"]

    # Load products CSV as lookup — need warranty, price, install flags per product
    products_by_id = {}
    with (Path(OUTPUT_DIR) / "raw_sap_material_master.csv").open() as f:
        for row in csv.DictReader(f):
            products_by_id[int(row["MATERIAL_ID"])] = {
                "list_price": float(row["LIST_PRICE_USD"]),
                "warranty_months": int(row["WARRANTY_MONTHS"]),
                "requires_hw": row["REQUIRES_HW_INSTALL"] == "True",
                "requires_sw": row["REQUIRES_SW_INSTALL"] == "True",
                "product_line": row["PRODUCT_LINE"],
                "is_active": row["IS_ACTIVE"] == "True",
            }
    active_material_ids = [mid for mid, p in products_by_id.items() if p["is_active"]]

    target_rows = SCALE["opportunities"]
    opportunities = []
    days_in_range = (DATA_END_DATE - DATA_START_DATE).days

    for opp_num in range(1, target_rows + 1):
        material_id = random.choice(active_material_ids)
        product = products_by_id[material_id]

        close_date = DATA_START_DATE + timedelta(days=random.randint(0, days_in_range))

        discount_range = random.choices(DISCOUNT_RANGES, weights=DISCOUNT_WEIGHTS)[0]
        discount_pct = round(random.uniform(*discount_range), 3)
        unit_sale_price = round(product["list_price"] * (1 - discount_pct), 2)

        quantity = random.choices([1, 2, 3], weights=[0.90, 0.08, 0.02])[0]
        total_amount = round(unit_sale_price * quantity, 2)

        warranty_start = close_date
        warranty_end = close_date + timedelta(days=product["warranty_months"] * 30)

        # Install dates: only populate if product requires them; ~10% still pending
        hw_install = None
        if product["requires_hw"] and random.random() < 0.90:
            hw_install = close_date + timedelta(days=random.randint(3, 60))

        sw_install = None
        if product["requires_sw"] and random.random() < 0.90:
            sw_install = close_date + timedelta(days=random.randint(3, 90))

        device_serial = f"DEV-{material_id:05d}-{opp_num:06d}"

        opportunities.append({
            "ID": _sf_id(),
            "OPPORTUNITY_NUMBER": f"OPP-{close_date.year}-{opp_num:07d}",
            "NAME": f"{fake.city()} - {product['product_line']}",
            "ACCOUNT_ID": random.choice(customer_ids),
            "OWNER_ID": random.choice(sales_rep_ids),
            "MATERIAL_ID": material_id,
            "DEVICE_SERIAL_NUMBER": device_serial,
            "QUANTITY": quantity,
            "UNIT_SALE_PRICE_USD": unit_sale_price,
            "TOTAL_AMOUNT_USD": total_amount,
            "DISCOUNT_PCT": discount_pct,
            "STAGE": "Closed Won",
            "CLOSE_DATE": close_date.isoformat(),
            "HARDWARE_INSTALL_DATE": hw_install.isoformat() if hw_install else None,
            "SOFTWARE_INSTALL_DATE": sw_install.isoformat() if sw_install else None,
            "WARRANTY_START_DATE": warranty_start.isoformat(),
            "WARRANTY_END_DATE": warranty_end.isoformat(),
            "PAYMENT_TERMS": random.choices(PAYMENT_TERMS, weights=PAYMENT_TERMS_WEIGHTS)[0],
            "CREATED_DATE": fake.date_time_between(start_date=close_date, end_date="now").isoformat(),
            "LAST_MODIFIED_DATE": fake.date_time_between(start_date="-6m", end_date="now").isoformat(),
            "IS_DELETED": False,
        })

    output_path = Path(OUTPUT_DIR) / "raw_salesforce_opportunity.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(opportunities[0].keys()))
        writer.writeheader()
        writer.writerows(opportunities)

    # Manifest — cases need serials + warranty info per device to determine IS_IN_WARRANTY at ticket time
    manifest = {
        "device_serials": [
            {
                "serial": o["DEVICE_SERIAL_NUMBER"],
                "account_id": o["ACCOUNT_ID"],
                "material_id": o["MATERIAL_ID"],
                "close_date": o["CLOSE_DATE"],
                "warranty_end_date": o["WARRANTY_END_DATE"],
            }
            for o in opportunities
        ],
        "count": len(opportunities),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_opportunities.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(opportunities)} opportunities → {output_path}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_opportunities()