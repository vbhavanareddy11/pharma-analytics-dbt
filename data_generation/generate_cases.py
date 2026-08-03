"""
generate_cases.py
-----------------
Generates SALESFORCE.CASE — service tickets.

Each ticket is on a specific sold device (DEVICE_SERIAL_NUMBER). Only devices
that have been sold can have tickets. IS_IN_WARRANTY is computed at ticket time
using the sale's warranty window, NOT the current date — realistic and
enables billable vs non-billable analysis downstream.

Business rules encoded:
  - Tickets can only be opened AFTER the device was sold
  - IS_IN_WARRANTY = did ticket open before the sale's warranty end date?
  - IS_BILLABLE_TO_CUSTOMER = out of warranty (customer pays)
  - Device pool pre-partitioned by warranty status to hit realistic 65/35 mix
  - Engineer hours and travel hours vary by case type and priority
  - Some tickets are still open (RESOLVED_DATE/CLOSED_DATE null)

Output: data_generation/output/raw_salesforce_case.csv
        data_generation/output/_manifest_cases.json
"""

import csv
import json
import random
import string
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

from config import (
    SCALE,
    OUTPUT_DIR,
    RANDOM_SEED,
    DATA_END_DATE,
)


CASE_TYPES = [
    "Hardware Failure", "Software Issue", "Calibration",
    "Preventive Maintenance", "User Training",
]
CASE_TYPE_WEIGHTS = [0.30, 0.20, 0.15, 0.25, 0.10]

PRIORITIES = ["Critical", "High", "Medium", "Low"]
PRIORITY_WEIGHTS = [0.08, 0.22, 0.45, 0.25]

RESOLUTION_CODES = [
    "Repaired", "Replaced", "No Fault Found", "Software Update", "Escalated",
]
RESOLUTION_WEIGHTS = [0.45, 0.15, 0.15, 0.20, 0.05]

TICKET_CHANNELS = ["On-Site", "Remote", "Phone Support"]
CHANNEL_WEIGHTS = [0.55, 0.25, 0.20]

# Engineer hours by case type — realistic effort
HOURS_BY_CASE_TYPE = {
    "Hardware Failure":       (2, 12),
    "Software Issue":         (0.5, 4),
    "Calibration":            (1, 3),
    "Preventive Maintenance": (2, 5),
    "User Training":          (1, 4),
}


def _sf_id():
    """Salesforce-style 18-char ID, '500' prefix for Case."""
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=15))
    return f"500{suffix}"


def generate_cases():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    # Load manifests
    with (Path(OUTPUT_DIR) / "_manifest_users.json").open() as f:
        users_manifest = json.load(f)
    field_engineer_ids = users_manifest["field_engineer_ids"]

    with (Path(OUTPUT_DIR) / "_manifest_opportunities.json").open() as f:
        opps_manifest = json.load(f)
    device_serials = opps_manifest["device_serials"]

    target_rows = SCALE["cases"]
    cases = []
    today = DATA_END_DATE

    # Pre-partition devices by warranty status relative to today.
    # Out-of-warranty tickets can only exist for devices whose warranty has expired.
    expired_warranty_devices = [
        d for d in device_serials
        if date.fromisoformat(d["warranty_end_date"]) < today
    ]
    print(f"Device pool: {len(device_serials)} total, {len(expired_warranty_devices)} expired warranty")

    for case_num in range(1, target_rows + 1):
        # Target 65/35 in-warranty vs billable. Pick device first based on target.
        want_billable = random.random() < 0.35 and expired_warranty_devices

        if want_billable:
            # Pick from devices with expired warranties, place ticket after expiry
            device = random.choice(expired_warranty_devices)
            sold_date = date.fromisoformat(device["close_date"])
            warranty_end = date.fromisoformat(device["warranty_end_date"])
            days_after_expiry = (today - warranty_end).days
            opened_date = warranty_end + timedelta(days=random.randint(0, days_after_expiry))
        else:
            # Pick any device, place ticket during warranty window if possible
            device = random.choice(device_serials)
            sold_date = date.fromisoformat(device["close_date"])
            warranty_end = date.fromisoformat(device["warranty_end_date"])
            latest_in_warranty = min(warranty_end, today)
            earliest = sold_date + timedelta(days=30)
            if earliest > latest_in_warranty:
                opened_date = latest_in_warranty
            else:
                span_days = (latest_in_warranty - earliest).days
                opened_date = earliest + timedelta(days=random.randint(0, span_days))

        # Warranty check at ticket time
        is_in_warranty = opened_date <= warranty_end
        is_billable = not is_in_warranty

        case_type = random.choices(CASE_TYPES, weights=CASE_TYPE_WEIGHTS)[0]
        priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]

        # Resolution: 92% resolved, 8% still open
        is_resolved = random.random() < 0.92
        resolved_date = None
        closed_date = None
        resolution_code = None
        status = "Open"
        if is_resolved:
            max_resolution_days = {"Critical": 5, "High": 10, "Medium": 20, "Low": 30}[priority]
            resolved_date = opened_date + timedelta(days=random.randint(1, max_resolution_days))
            if resolved_date > today:
                resolved_date = today
            closed_date = resolved_date + timedelta(days=random.randint(0, 5))
            if closed_date > today:
                closed_date = today
            resolution_code = random.choices(RESOLUTION_CODES, weights=RESOLUTION_WEIGHTS)[0]
            status = "Closed"

        engineer_hours = round(random.uniform(*HOURS_BY_CASE_TYPE[case_type]), 2)
        channel = random.choices(TICKET_CHANNELS, weights=CHANNEL_WEIGHTS)[0]
        travel_hours = round(random.uniform(1, 4), 2) if channel == "On-Site" else 0.0

        cases.append({
            "ID": _sf_id(),
            "CASE_NUMBER": f"CASE-{opened_date.year}-{case_num:07d}",
            "SUBJECT": f"{case_type} - {device['serial']}",
            "ACCOUNT_ID": device["account_id"],
            "DEVICE_SERIAL_NUMBER": device["serial"],
            "OWNER_ID": random.choice(field_engineer_ids),
            "CASE_TYPE": case_type,
            "PRIORITY": priority,
            "STATUS": status,
            "RESOLUTION_CODE": resolution_code,
            "IS_IN_WARRANTY": is_in_warranty,
            "IS_BILLABLE_TO_CUSTOMER": is_billable,
            "ENGINEER_HOURS_LOGGED": engineer_hours,
            "TRAVEL_HOURS_LOGGED": travel_hours,
            "TICKET_CHANNEL": channel,
            "OPENED_DATE": datetime.combine(opened_date, datetime.min.time()).isoformat(),
            "RESOLVED_DATE": datetime.combine(resolved_date, datetime.min.time()).isoformat() if resolved_date else None,
            "CLOSED_DATE": datetime.combine(closed_date, datetime.min.time()).isoformat() if closed_date else None,
            "CREATED_DATE": datetime.combine(opened_date, datetime.min.time()).isoformat(),
            "LAST_MODIFIED_DATE": fake.date_time_between(start_date="-6m", end_date="now").isoformat(),
            "IS_DELETED": False,
        })

    output_path = Path(OUTPUT_DIR) / "raw_salesforce_case.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(cases[0].keys()))
        writer.writeheader()
        writer.writerows(cases)

    # Manifest for case_parts — parts get consumed on specific tickets
    manifest = {
        "case_ids": [c["ID"] for c in cases if c["STATUS"] == "Closed"],
        "case_lookup": {
            c["ID"]: {
                "device_serial": c["DEVICE_SERIAL_NUMBER"],
                "is_in_warranty": c["IS_IN_WARRANTY"],
                "opened_date": c["OPENED_DATE"],
            }
            for c in cases if c["STATUS"] == "Closed"
        },
        "count": len(cases),
    }
    manifest_path = Path(OUTPUT_DIR) / "_manifest_cases.json"
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    in_warranty_count = sum(1 for c in cases if c["IS_IN_WARRANTY"])
    print(f"Generated {len(cases)} cases → {output_path}")
    print(f"  In-warranty: {in_warranty_count}")
    print(f"  Out-of-warranty (billable): {len(cases) - in_warranty_count}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    generate_cases()