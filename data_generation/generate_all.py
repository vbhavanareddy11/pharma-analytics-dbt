"""
generate_all.py
---------------
Orchestrator — runs the full synthetic data pipeline in dependency order.

Order matters: manifests written by upstream generators are read by downstream
ones to enforce referential integrity across the raw layer.

Usage:
    python data_generation/generate_all.py

Regenerates everything from scratch. Because all generators seed their random
sources with config.RANDOM_SEED, output is deterministic — running this on
any machine produces byte-identical CSVs.
"""

import time

from generate_products import generate_products
from generate_users import generate_users
from generate_accounts import generate_accounts
from generate_distributors import generate_distributors
from generate_spare_parts import generate_spare_parts
from generate_opportunities import generate_opportunities
from generate_cases import generate_cases
from generate_case_parts import generate_case_parts
from generate_seeds import generate_seeds


PIPELINE = [
    ("Products",       generate_products),
    ("Users",          generate_users),
    ("Accounts",       generate_accounts),
    ("Distributors",   generate_distributors),
    ("Spare Parts",    generate_spare_parts),
    ("Opportunities",  generate_opportunities),
    ("Cases",          generate_cases),
    ("Case Parts",     generate_case_parts),
    ("Seeds",          generate_seeds),
]


def main():
    print("=" * 70)
    print("Synthetic Pharma Data Generation Pipeline")
    print("=" * 70)

    total_start = time.time()

    for step_name, step_fn in PIPELINE:
        print(f"\n--- {step_name} ---")
        step_start = time.time()
        step_fn()
        elapsed = time.time() - step_start
        print(f"({step_name} completed in {elapsed:.1f}s)")

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"Full pipeline completed in {total_elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()