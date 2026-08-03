"""
config.py
---------
Shared constants for the synthetic pharma data generator.

Centralizes all domain values (countries, product families, zones, etc.)
so scale and mix changes touch one file, not eight.
"""

from datetime import date

# -----------------------------------------------------------------------------
# SCALE — controls how many rows each generator produces.
# Medium scale: production-realistic without burning trial credits.
# -----------------------------------------------------------------------------
SCALE = {
    "products": 200,           # SAP.MATERIAL_MASTER rows
    "accounts": 500,           # SALESFORCE.ACCOUNT rows (hospitals + distributors)
    "users": 150,              # SALESFORCE.USER rows (sales reps + field engineers)
    "distributors": 50,        # SAP.DISTRIBUTOR rows (subset of accounts flagged as distributors)
    "spare_parts": 300,        # SAP.SPARE_PARTS catalog
    "opportunities": 100_000,  # SALESFORCE.OPPORTUNITY — sales fact source
    "cases": 50_000,           # SALESFORCE.CASE — service ticket fact source
    # case_parts is derived (avg ~1.6 parts per case) — computed at generation time, not fixed here
}

# -----------------------------------------------------------------------------
# DATE RANGE — the historical window synthetic data spans.
# 2 years of activity gives enough history for SCD2 changes and incremental logic.
# -----------------------------------------------------------------------------
DATA_START_DATE = date(2023, 1, 1)
DATA_END_DATE = date(2025, 6, 30)

# -----------------------------------------------------------------------------
# APAC COUNTRIES — the 14 markets this pipeline serves
# Mirrors the real Accenture pharma footprint.
# -----------------------------------------------------------------------------
COUNTRIES = [
    "Thailand", "Vietnam", "Malaysia", "Singapore", "Indonesia",
    "Philippines", "India", "Japan", "South Korea", "Taiwan",
    "Hong Kong", "Australia", "New Zealand", "China",
]

# Two-letter country code for building zone identifiers (APAC-TH-01, APAC-VN-02, etc.)
COUNTRY_CODES = {
    "Thailand": "TH", "Vietnam": "VN", "Malaysia": "MY", "Singapore": "SG",
    "Indonesia": "ID", "Philippines": "PH", "India": "IN", "Japan": "JP",
    "South Korea": "KR", "Taiwan": "TW", "Hong Kong": "HK", "Australia": "AU",
    "New Zealand": "NZ", "China": "CN",
}

# -----------------------------------------------------------------------------
# PRODUCT HIERARCHY — 4 levels: business unit -> therapy area -> family -> line
# Each product line ends up mapped to one disease category for launch targeting.
# -----------------------------------------------------------------------------
PRODUCT_HIERARCHY = {
    "Medical Devices": {
        "Diabetes Care": {
            "Glucose Monitoring": ["GlucoCheck Home Series", "GlucoCheck Pro Series"],
            "Insulin Delivery": ["InsuPen Basic", "InsuPen Smart"],
        },
        "Respiratory Care": {
            "Ventilators": ["VentiFlow ICU", "VentiFlow Portable"],
            "CPAP": ["BreathEase Home", "BreathEase Travel"],
        },
        "Cardiac Care": {
            "ECG Systems": ["CardioTrace Bedside", "CardioTrace Holter"],
            "Defibrillators": ["ShockGuard AED", "ShockGuard Manual"],
        },
        "Renal Care": {
            "Dialysis Machines": ["RenalPure Hemo", "RenalPure Peritoneal"],
        },
        "Oncology Support": {
            "Infusion Pumps": ["OncoFlow Ambulatory", "OncoFlow Stationary"],
        },
    },
}

# Product line -> disease category mapping (for the launch-targeting join)
PRODUCT_LINE_TO_DISEASE = {
    "GlucoCheck Home Series": "Diabetes",
    "GlucoCheck Pro Series": "Diabetes",
    "InsuPen Basic": "Diabetes",
    "InsuPen Smart": "Diabetes",
    "VentiFlow ICU": "Respiratory",
    "VentiFlow Portable": "Respiratory",
    "BreathEase Home": "Respiratory",
    "BreathEase Travel": "Respiratory",
    "CardioTrace Bedside": "Cardiac",
    "CardioTrace Holter": "Cardiac",
    "ShockGuard AED": "Cardiac",
    "ShockGuard Manual": "Cardiac",
    "RenalPure Hemo": "Renal",
    "RenalPure Peritoneal": "Renal",
    "OncoFlow Ambulatory": "Oncology",
    "OncoFlow Stationary": "Oncology",
}

DISEASE_CATEGORIES = ["Diabetes", "Respiratory", "Cardiac", "Renal", "Oncology"]

# -----------------------------------------------------------------------------
# ACCOUNT TYPES — mirrors Salesforce Account Type field values
# -----------------------------------------------------------------------------
ACCOUNT_TYPES = ["Hospital", "Hospital Chain", "Independent Distributor", "Clinic"]
ACCOUNT_TIERS = ["Tier 1", "Tier 2", "Tier 3"]

# -----------------------------------------------------------------------------
# USER ROLES — persona split for the SALESFORCE.USER table
# -----------------------------------------------------------------------------
USER_ROLES = ["Sales Rep", "Field Engineer", "Sales Manager", "Regional Service Manager"]

# Approximate share of headcount per role. Sales-heavy, as commercial orgs are.
USER_ROLE_WEIGHTS = {
    "Sales Rep": 0.55,
    "Field Engineer": 0.30,
    "Sales Manager": 0.08,
    "Regional Service Manager": 0.07,
}

# -----------------------------------------------------------------------------
# OUTPUT PATH — where generated CSVs land
# -----------------------------------------------------------------------------
OUTPUT_DIR = "data_generation/output"

# -----------------------------------------------------------------------------
# RANDOM SEED — reproducibility. Same seed = same synthetic data every run.
# Critical for debugging: if your dbt tests fail, you can re-run generation
# and hit the exact same rows.
# -----------------------------------------------------------------------------
RANDOM_SEED = 42