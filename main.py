import os
import json
import pandas as pd
import numpy as np
from extract.parser import process_all_emails
from validate.validator import validate_all_orders
from format.formatter import format_final_orders

# Paths
DATA_DIR = "data/"
OUTPUT_DIR = "output/"
EXTRACTED_PATH = os.path.join(OUTPUT_DIR, "extracted_orders.json")
VALIDATED_PATH = os.path.join(OUTPUT_DIR, "validated_orders.json")
FINAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "final_orders.json")
CATALOG_PATH = os.path.join(DATA_DIR, "Product Catalog.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# STEP 1 — Extract Orders
print("Extracting orders from email...")
extracted_orders = process_all_emails(DATA_DIR)

with open(EXTRACTED_PATH, "w", encoding="utf-8") as f:
    json.dump(extracted_orders, f, indent=4, ensure_ascii=False)
print(f"Extracted orders saved to {EXTRACTED_PATH}")

# STEP 2 — Validate Against Product Catalog
print("Validating orders using product catalog...")
catalog_df = pd.read_csv(CATALOG_PATH)
catalog_df.columns = catalog_df.columns.str.strip()

validated_orders = validate_all_orders(extracted_orders, catalog_df)

# Helper to safely convert NumPy types
def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

# Write validated orders
with open(VALIDATED_PATH, "w", encoding="utf-8") as f:
    json.dump(to_serializable(validated_orders), f, indent=4, ensure_ascii=False)
print(f"Validated orders saved to {VALIDATED_PATH}")

# STEP 3 — Format Final JSON
print("Formatting final clean order output...")
final_orders = format_final_orders(validated_orders)

with open(FINAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(to_serializable(final_orders), f, indent=4, ensure_ascii=False)
print(f"Final structured orders saved to {FINAL_OUTPUT_PATH}")
