"""
generate_case_parts.py
----------------------
Generates SALESFORCE.CASE_PART_USAGE — parts consumed per service ticket.

Only Closed tickets consume parts. Number of parts per ticket varies by case
type (Hardware Failure uses more, Software Issue uses none-to-few). Parts are
matched to the device's product line — a ventilator ticket can only use
ventilator-compatible parts.

Cost is captured at time of use (snapshot, not looked up later). If the
underlying ticket is out-of-warranty, the customer is charged unit_price;
otherwise the company eats the cost and charge is 0.

Output: data_generation/output/raw_salesforce_case_part_usage.csv
"""

import csv
import json
import random
import string
from pathlib import Path

from config import OUTPUT_DIR, RANDOM_SEED


# Distribution of parts-per-ticket by case type
# Values are (min_parts, max_parts). Software/Training tickets rarely need parts.
PARTS_PER_CASE_TYPE = {
    "Hardware Failure":       (1, 4),
    "Software Issue":         (0, 1),
    "Calibration":            (0, 2),
    "Preventive Maintenance": (1, 3),
    "User Training":          (0, 1),
}

# Probability that a ticket of this type uses ANY parts at all
PARTS_PROBABILITY = {
    "Hardware Failure":       0.95,
    "Software Issue":         0.15,
    "Calibration":            0.60,
    "Preventive Maintenance": 0.85,
    "User Training":          0.05,
}


def _sf_id():
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=15))
    return f"a01{suffix}"   # custom-object-style prefix


def generate_case_parts():
    random.seed(RANDOM_SEED)

    # Load cases manifest
    with (Path(OUTPUT_DIR) / "_manifest_cases.json").open() as f:
        cases_manifest = json.load(f)
    case_ids = cases_manifest["case_ids"]
    case_lookup = cases_manifest["case_lookup"]

    # Load spare parts manifest — need to pick parts compatible with each device's product line
    with (Path(OUTPUT_DIR) / "_manifest_spare_parts.json").open() as f:
        parts_manifest = json.load(f)
    parts_by_line = parts_manifest["parts_by_product_line"]

    # Load spare parts CSV to get unit costs/prices
    parts_lookup = {}
    with (Path(OUTPUT_DIR) / "raw_sap_spare_parts.csv").open() as f:
        for row in csv.DictReader(f):
            parts_lookup[int(row["PART_ID"])] = {
                "unit_cost": float(row["UNIT_COST_USD"]),
                "unit_price": float(row["UNIT_PRICE_USD"]),
            }

    # Load opportunities CSV to look up product line by device serial
    serial_to_line = {}
    with (Path(OUTPUT_DIR) / "raw_salesforce_opportunity.csv").open() as f:
        # Need to resolve MATERIAL_ID -> PRODUCT_LINE, so also load products
        pass

    products_by_id = {}
    with (Path(OUTPUT_DIR) / "raw_sap_material_master.csv").open() as f:
        for row in csv.DictReader(f):
            products_by_id[int(row["MATERIAL_ID"])] = row["PRODUCT_LINE"]

    with (Path(OUTPUT_DIR) / "raw_salesforce_opportunity.csv").open() as f:
        for row in csv.DictReader(f):
            serial_to_line[row["DEVICE_SERIAL_NUMBER"]] = products_by_id[int(row["MATERIAL_ID"])]

    # We need case type per case — load from cases CSV
    case_type_lookup = {}
    with (Path(OUTPUT_DIR) / "raw_salesforce_case.csv").open() as f:
        for row in csv.DictReader(f):
            case_type_lookup[row["ID"]] = row["CASE_TYPE"]

    part_usages = []
    for case_id in case_ids:
        case_type = case_type_lookup[case_id]
        # Roll for whether this ticket uses any parts at all
        if random.random() > PARTS_PROBABILITY[case_type]:
            continue

        info = case_lookup[case_id]
        device_serial = info["device_serial"]
        is_in_warranty = info["is_in_warranty"]
        product_line = serial_to_line[device_serial]

        # Compatible parts for this device's product line
        compatible_parts = parts_by_line.get(product_line, [])
        if not compatible_parts:
            continue

        min_p, max_p = PARTS_PER_CASE_TYPE[case_type]
        num_parts = random.randint(max(1, min_p), max_p)

        # Sample distinct parts (no double-use of same part on one ticket)
        num_parts = min(num_parts, len(compatible_parts))
        chosen_parts = random.sample(compatible_parts, num_parts)

        for part_id in chosen_parts:
            part_info = parts_lookup[part_id]
            quantity = random.choices([1, 2, 3], weights=[0.80, 0.15, 0.05])[0]
            unit_price_charged = 0.0 if is_in_warranty else part_info["unit_price"]

            part_usages.append({
                "ID": _sf_id(),
                "CASE_ID": case_id,
                "PART_ID": part_id,
                "QUANTITY": quantity,
                "UNIT_COST_AT_TIME_OF_USE_USD": part_info["unit_cost"],
                "UNIT_PRICE_CHARGED_TO_CUSTOMER_USD": unit_price_charged,
                "CREATED_DATE": info["opened_date"],
                "LAST_MODIFIED_DATE": info["opened_date"],
                "IS_DELETED": False,
            })

    output_path = Path(OUTPUT_DIR) / "raw_salesforce_case_part_usage.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(part_usages[0].keys()))
        writer.writeheader()
        writer.writerows(part_usages)

    total_charged = sum(1 for u in part_usages if u["UNIT_PRICE_CHARGED_TO_CUSTOMER_USD"] > 0)
    print(f"Generated {len(part_usages)} part usage rows → {output_path}")
    print(f"  Billable to customer: {total_charged}")
    print(f"  Absorbed by company: {len(part_usages) - total_charged}")


if __name__ == "__main__":
    generate_case_parts()