"""
generate_seeds.py
-----------------
Generates the two hand-maintained reference CSVs that live in dbt's seeds/ folder:

  - zone_hierarchy.csv         — country -> zone -> sub_zone geographic drill-down
  - region_disease_prevalence.csv — epidemiology reference for launch targeting

These are conceptually different from the other CSVs. The SAP/Salesforce CSVs
pretend to come from source systems. Seeds are what an analyst would maintain
in a Google Sheet — small, stable, hand-curated. dbt materializes them as
warehouse tables via `dbt seed`.

Output: seeds/zone_hierarchy.csv
        seeds/region_disease_prevalence.csv
"""

import csv
import random
from datetime import date
from pathlib import Path

from config import (
    RANDOM_SEED,
    COUNTRIES,
    COUNTRY_CODES,
    DISEASE_CATEGORIES,
)


SEEDS_DIR = "seeds"

# Disease prevalence patterns — different regions skew toward different disease burdens.
# Values roughly reflect real epidemiology (higher score = higher prevalence).
# 0.30 = baseline, 0.75 = high burden.
COUNTRY_DISEASE_SKEW = {
    "Thailand":     {"Diabetes": 0.68, "Respiratory": 0.52, "Cardiac": 0.55, "Renal": 0.45, "Oncology": 0.40},
    "Vietnam":      {"Diabetes": 0.50, "Respiratory": 0.62, "Cardiac": 0.48, "Renal": 0.42, "Oncology": 0.38},
    "Malaysia":     {"Diabetes": 0.72, "Respiratory": 0.48, "Cardiac": 0.60, "Renal": 0.50, "Oncology": 0.42},
    "Singapore":    {"Diabetes": 0.65, "Respiratory": 0.40, "Cardiac": 0.55, "Renal": 0.48, "Oncology": 0.52},
    "Indonesia":    {"Diabetes": 0.55, "Respiratory": 0.65, "Cardiac": 0.45, "Renal": 0.38, "Oncology": 0.35},
    "Philippines":  {"Diabetes": 0.58, "Respiratory": 0.68, "Cardiac": 0.50, "Renal": 0.40, "Oncology": 0.36},
    "India":        {"Diabetes": 0.75, "Respiratory": 0.60, "Cardiac": 0.62, "Renal": 0.55, "Oncology": 0.45},
    "Japan":        {"Diabetes": 0.42, "Respiratory": 0.45, "Cardiac": 0.58, "Renal": 0.50, "Oncology": 0.68},
    "South Korea":  {"Diabetes": 0.48, "Respiratory": 0.42, "Cardiac": 0.55, "Renal": 0.50, "Oncology": 0.65},
    "Taiwan":       {"Diabetes": 0.55, "Respiratory": 0.45, "Cardiac": 0.58, "Renal": 0.52, "Oncology": 0.60},
    "Hong Kong":    {"Diabetes": 0.50, "Respiratory": 0.42, "Cardiac": 0.55, "Renal": 0.48, "Oncology": 0.55},
    "Australia":    {"Diabetes": 0.45, "Respiratory": 0.40, "Cardiac": 0.52, "Renal": 0.45, "Oncology": 0.62},
    "New Zealand":  {"Diabetes": 0.48, "Respiratory": 0.42, "Cardiac": 0.55, "Renal": 0.42, "Oncology": 0.60},
    "China":        {"Diabetes": 0.65, "Respiratory": 0.68, "Cardiac": 0.55, "Renal": 0.50, "Oncology": 0.55},
}

ZONE_NAME_FORMATS = ["North", "South", "East", "West", "Central"]


def generate_seeds():
    random.seed(RANDOM_SEED)
    seeds_path = Path(SEEDS_DIR)
    seeds_path.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------------
    # Zone hierarchy — 5 zones per country, sub_zone per zone
    # -----------------------------------------------------------------------------
    zone_rows = []
    for country in COUNTRIES:
        country_code = COUNTRY_CODES[country]
        for zone_num in range(1, 6):
            zone_name = ZONE_NAME_FORMATS[zone_num - 1]
            sub_zone_name = f"{zone_name} {country} Sub-Region {zone_num}"
            zone_rows.append({
                "ZONE_CODE": f"APAC-{country_code}-{zone_num:02d}",
                "SUB_ZONE_NAME": sub_zone_name,
                "ZONE_NAME": f"{zone_name} {country}",
                "COUNTRY": country,
                "REGION": "APAC",
            })

    zone_path = seeds_path / "zone_hierarchy.csv"
    with zone_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(zone_rows[0].keys()))
        writer.writeheader()
        writer.writerows(zone_rows)
    print(f"Generated {len(zone_rows)} zone rows → {zone_path}")

    # -----------------------------------------------------------------------------
    # Region disease prevalence — one row per (zone, disease)
    # -----------------------------------------------------------------------------
    prevalence_rows = []
    today = date.today().isoformat()
    for zone_row in zone_rows:
        country = zone_row["COUNTRY"]
        for disease in DISEASE_CATEGORIES:
            base_score = COUNTRY_DISEASE_SKEW[country][disease]
            # Add small zone-level variation around the country baseline
            zone_score = round(max(0.05, min(0.95, base_score + random.uniform(-0.08, 0.08))), 3)
            prevalence_rows.append({
                "ZONE_CODE": zone_row["ZONE_CODE"],
                "DISEASE_CATEGORY": disease,
                "PREVALENCE_SCORE": zone_score,
                "SOURCE": "IQVIA-simulated",
                "UPDATED_DATE": today,
            })

    prevalence_path = seeds_path / "region_disease_prevalence.csv"
    with prevalence_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(prevalence_rows[0].keys()))
        writer.writeheader()
        writer.writerows(prevalence_rows)
    print(f"Generated {len(prevalence_rows)} prevalence rows → {prevalence_path}")


if __name__ == "__main__":
    generate_seeds()