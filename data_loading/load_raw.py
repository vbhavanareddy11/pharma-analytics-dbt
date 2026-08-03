"""
load_raw.py
-----------
Loads the 8 raw CSVs from data_generation/output/ into Snowflake's RAW database.

For each CSV:
  1. PUT the file to the internal stage RAW.PUBLIC.RAW_STAGE
  2. COPY INTO the target table using the CSV_FORMAT file format
  3. Verify row count

Credentials read from environment variables:
  SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT,
  SNOWFLAKE_WAREHOUSE, SNOWFLAKE_ROLE

Usage:
    python data_loading/load_raw.py

Idempotent: TRUNCATE before load ensures clean, repeatable runs.
"""

import os
import sys
import time
from pathlib import Path

import snowflake.connector


# Map: CSV filename -> fully qualified target table
LOAD_PLAN = [
    ("raw_sap_material_master.csv",       "RAW.SAP.MATERIAL_MASTER"),
    ("raw_sap_distributor.csv",           "RAW.SAP.DISTRIBUTOR"),
    ("raw_sap_spare_parts.csv",           "RAW.SAP.SPARE_PARTS"),
    ("raw_salesforce_account.csv",        "RAW.SALESFORCE.ACCOUNT"),
    ("raw_salesforce_user.csv",           "RAW.SALESFORCE.USER"),
    ("raw_salesforce_opportunity.csv",    "RAW.SALESFORCE.OPPORTUNITY"),
    ("raw_salesforce_case.csv",           "RAW.SALESFORCE.CASE"),
    ("raw_salesforce_case_part_usage.csv","RAW.SALESFORCE.CASE_PART_USAGE"),
]

CSV_DIR = Path("data_generation/output")
STAGE = "RAW.PUBLIC.RAW_STAGE"
FILE_FORMAT = "RAW.PUBLIC.CSV_FORMAT"


def get_connection():
    """Connect to Snowflake using credentials from environment variables."""
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing env vars: {missing}")
        print("Set them with: export SNOWFLAKE_USER=... etc.")
        sys.exit(1)

    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )


def load_one(cursor, csv_filename, target_table):
    """PUT a single CSV to the stage, then COPY INTO the target table."""
    csv_path = CSV_DIR / csv_filename
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found on disk")
        return 0

    abs_path = csv_path.resolve()

    # Truncate first for clean re-runs
    cursor.execute(f"TRUNCATE TABLE {target_table}")

    # PUT file to stage
    put_sql = f"PUT 'file://{abs_path}' @{STAGE} OVERWRITE = TRUE AUTO_COMPRESS = TRUE"
    cursor.execute(put_sql)

    # COPY INTO target table
    copy_sql = f"""
        COPY INTO {target_table}
        FROM @{STAGE}/{csv_filename}
        FILE_FORMAT = (FORMAT_NAME = {FILE_FORMAT})
        ON_ERROR = 'ABORT_STATEMENT'
    """
    cursor.execute(copy_sql)

    # Confirm row count
    cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
    row_count = cursor.fetchone()[0]
    return row_count


def main():
    print("=" * 70)
    print("Snowflake RAW loader")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    total_start = time.time()
    total_rows = 0

    for csv_filename, target_table in LOAD_PLAN:
        print(f"\n--- {target_table} ---")
        step_start = time.time()
        row_count = load_one(cursor, csv_filename, target_table)
        elapsed = time.time() - step_start
        print(f"  Loaded {row_count:,} rows in {elapsed:.1f}s")
        total_rows += row_count

    cursor.close()
    conn.close()

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"Total: {total_rows:,} rows loaded in {total_elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()