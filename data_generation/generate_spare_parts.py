"""
generate_spare_parts.py
-----------------------
Generates SAP.SPARE_PARTS — the parts catalog.

Each part is compatible with one product line (simplification — real SAP would
model many-to-many via a PART_PRODUCT_COMPATIBILITY bridge). Cost/price varies
by part category with realistic markup.

Output: data_generation/output/raw_sap_spare_parts.csv
        data_generation/output/_manifest_spare_parts.json
"""

import csv
import json
import random
from pathlib import Path

from faker import Faker

from config import (
    SCALE,
    OUTPUT_DIR,
    RANDOM_SEED,
    PRODUCT_HIERARCHY,
)


# Cost range (USD) per part category — small, low-margin components vs. high-value
CATEGORY_COST_RANGE = {
    "Filter":       (5, 40),
    "Sensor":       (30, 200),
    "Battery":      (80, 350),
    "Cable":        (10, 60),
    "Circuit Board":(150, 800),
    "Housing":      (25, 120),
}

# Retail markup on parts sold to out-of-warranty customers
CATEGORY_MARKUP = {
    "Filter": 2.5,
    "Sensor": 2.2,
    "Battery": 2.0,
    "Cable": 2.8,
    "Circuit Board": 1.8,
    "Housing": 2.4,
}


def generate_spare_parts():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    # Load product manifest to pull compatible product lines
    with (Path(OUTPUT_DIR) / "_manifest_products.json").open() as f:
        products_manifest = json.load(f)
    product_lines = products_manifest["product_lines"]

    target_rows = SCALE["spare_parts"]
    parts = []
    categories = list(CATEGORY_COST_RANGE.keys())

    for part_id in range(1, target_rows + 1):
        category = random.choice(categories)
        compatible_line = random.choice(product_lines)
        unit_cost = round(random.uniform(*CATEGORY_COST_RANGE[category]), 2)
        unit_price = round(unit_cost * CATEGORY_MARKUP[category], 2)

        parts.append({
            "PART_ID": part_id,
            "PART_CODE": f"SP-{category[:4].upper()}-{part_id:05d}",
            "PART_NAME": f"{compatible_line} {category}",
            "PART_CATEGORY": category,
            "COMPATIBLE_PRODUCT_LINE": compatible_line,
            "UNIT_COST_USD": unit_cost,
            "UNIT_PRICE_USD": unit_price,
            "IS_ACTIVE": random.choices([True, False], weights=[0.93, 0.07])[0],
            "CREATED_AT": fake.date_time_between(
                start_date="-5y", end_date="-6m"
            ).isoformat(),
            "UPDATED_AT": fake.date_time_between(
                start_date="-6m", end_date="now"
            ).isoformat(),
        })

    output_path = Path(OUTPUT_DIR) / "raw_sap_spare_parts.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(parts[0].keys()))
        writer.writeheader()
        writer.writerows(parts)

    manifest = {
        "part_ids": [p["PART_ID"] for p in parts],
        "parts_by_product_line": {
            line: [p["PART_ID"] for p in parts if p["COMPATIBLE_PRODUCT_LINE"] == line]
            for line in product_lines
        },
        "count": len(parts),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_spare_parts.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(parts)} spare parts → {output_path}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_spare_parts()