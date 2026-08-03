"""
generate_products.py
--------------------
Generates SAP.MATERIAL_MASTER — the product master catalog.

Produces ~200 realistic pharma medical device products across the 4-level
hierarchy (business_unit → therapy_area → product_family → product_line),
with cost/price economics, warranty periods, and install requirements
that vary by product family.

Output: data_generation/output/raw_sap_material_master.csv
Also writes:  data_generation/output/_manifest_products.json
              (lookup used by downstream generators)
"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from config import (
    SCALE,
    OUTPUT_DIR,
    RANDOM_SEED,
    PRODUCT_HIERARCHY,
    PRODUCT_LINE_TO_DISEASE,
)


# -----------------------------------------------------------------------------
# Business rules — per product family, driving realistic variation
# -----------------------------------------------------------------------------

# Price range (list_price_usd) per product family — reflects real device economics.
# Ventilators are expensive capital equipment; home glucose monitors are cheap consumer devices.
FAMILY_PRICE_RANGE = {
    "Glucose Monitoring": (80, 400),
    "Insulin Delivery": (300, 900),
    "Ventilators": (15000, 45000),
    "CPAP": (600, 1800),
    "ECG Systems": (2500, 8000),
    "Defibrillators": (1500, 5000),
    "Dialysis Machines": (25000, 60000),
    "Infusion Pumps": (1200, 4500),
}

# Production cost as a fraction of list price — pharma capital equipment margins.
# Lower fraction = higher margin. Ventilators 30% cost = 70% gross margin.
FAMILY_COST_RATIO = {
    "Glucose Monitoring": 0.40,
    "Insulin Delivery": 0.35,
    "Ventilators": 0.30,
    "CPAP": 0.35,
    "ECG Systems": 0.32,
    "Defibrillators": 0.33,
    "Dialysis Machines": 0.28,
    "Infusion Pumps": 0.34,
}

# Warranty months per family — capital equipment gets longer warranties.
FAMILY_WARRANTY_MONTHS = {
    "Glucose Monitoring": 12,
    "Insulin Delivery": 24,
    "Ventilators": 36,
    "CPAP": 24,
    "ECG Systems": 36,
    "Defibrillators": 60,     # regulatory — defibs need extended coverage
    "Dialysis Machines": 60,
    "Infusion Pumps": 24,
}

# Which families require hardware install and/or software install post-delivery
FAMILY_REQUIRES_HW_INSTALL = {
    "Glucose Monitoring": False,
    "Insulin Delivery": False,
    "Ventilators": True,
    "CPAP": False,
    "ECG Systems": True,
    "Defibrillators": True,
    "Dialysis Machines": True,
    "Infusion Pumps": False,
}

FAMILY_REQUIRES_SW_INSTALL = {
    "Glucose Monitoring": False,
    "Insulin Delivery": True,      # smart pens have companion apps
    "Ventilators": True,
    "CPAP": True,                  # sleep-data cloud sync
    "ECG Systems": True,
    "Defibrillators": True,
    "Dialysis Machines": True,
    "Infusion Pumps": True,
}


# -----------------------------------------------------------------------------
# Main generation function
# -----------------------------------------------------------------------------

def generate_products():
    """Generate the product master CSV + a manifest for downstream generators."""

    # Seed both random and Faker for reproducibility
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    target_rows = SCALE["products"]
    products = []
    material_id = 1

    # Walk the 4-level hierarchy to enumerate every unique product line,
    # then create multiple SKUs per line until we hit the target row count.
    all_product_lines = []
    for business_unit, therapy_areas in PRODUCT_HIERARCHY.items():
        for therapy_area, families in therapy_areas.items():
            for family, lines in families.items():
                for line in lines:
                    all_product_lines.append((business_unit, therapy_area, family, line))

    # SKUs-per-product-line = target / (# of product lines), rounded up
    skus_per_line = -(-target_rows // len(all_product_lines))  # ceiling division idiom

    for business_unit, therapy_area, family, product_line in all_product_lines:
        for sku_index in range(1, skus_per_line + 1):
            if material_id > target_rows:
                break

            list_price = round(random.uniform(*FAMILY_PRICE_RANGE[family]), 2)
            production_cost = round(list_price * FAMILY_COST_RATIO[family], 2)

            # Launch date: sometime in the last 6 years
            days_ago = random.randint(30, 365 * 6)
            launch_date = date.today() - timedelta(days=days_ago)

            products.append({
                "MATERIAL_ID": material_id,
                "MATERIAL_CODE": f"MED-{family[:4].upper()}-{sku_index:03d}-{material_id:05d}",
                "MATERIAL_NAME": f"{product_line} v{sku_index}",
                "BUSINESS_UNIT": business_unit,
                "THERAPY_AREA": therapy_area,
                "PRODUCT_FAMILY": family,
                "PRODUCT_LINE": product_line,
                "DISEASE_CATEGORY": PRODUCT_LINE_TO_DISEASE[product_line],
                "LIST_PRICE_USD": list_price,
                "PRODUCTION_COST_USD": production_cost,
                "WARRANTY_MONTHS": FAMILY_WARRANTY_MONTHS[family],
                "SERVICE_TIER": random.choices(
                    ["Standard", "Premium"], weights=[0.75, 0.25]
                )[0],
                "REQUIRES_HW_INSTALL": FAMILY_REQUIRES_HW_INSTALL[family],
                "REQUIRES_SW_INSTALL": FAMILY_REQUIRES_SW_INSTALL[family],
                "LAUNCH_DATE": launch_date.isoformat(),
                "IS_ACTIVE": random.choices([True, False], weights=[0.90, 0.10])[0],
                "CREATED_AT": fake.date_time_between(
                    start_date="-6y", end_date="-3y"
                ).isoformat(),
                "UPDATED_AT": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
            })
            material_id += 1

    # -----------------------------------------------------------------------------
    # Write the CSV
    # -----------------------------------------------------------------------------
    output_path = Path(OUTPUT_DIR) / "raw_sap_material_master.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(products[0].keys()))
        writer.writeheader()
        writer.writerows(products)

    # -----------------------------------------------------------------------------
    # Write the manifest — downstream generators will import this
    # to pick random MATERIAL_IDs for sales, spare parts, etc.
    # -----------------------------------------------------------------------------
    manifest = {
        "material_ids": [p["MATERIAL_ID"] for p in products],
        "product_lines": list({p["PRODUCT_LINE"] for p in products}),
        "count": len(products),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_products.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(products)} products → {output_path}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_products()