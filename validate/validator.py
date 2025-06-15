import pandas as pd
import json
import os
from difflib import get_close_matches

INPUT_FILE = "../output/extracted_orders.json"
CATALOG_FILE = "../data/Product Catalog.csv"
OUTPUT_FILE = "../output/validated_orders.json"

def load_orders(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def suggest_replacement(name, catalog_df):
    name = name.lower().strip()
    matches = get_close_matches(name, catalog_df["Normalized"].tolist(), n=1, cutoff=0.7)
    if matches:
        close_name = matches[0]
        row = catalog_df[catalog_df["Normalized"] == close_name].iloc[0]
        return {
            "suggested_name": row["Product_Name"],
            "sku": row["Product_Code"],
            "price": row["Price"],
            "moq": row["Min_Order_Quantity"],
            "available": row["Available_in_Stock"]
        }
    return None

def validate_all_orders(extracted_orders, catalog_df):
# Clean all column names to avoid invisible issues
    catalog_df.columns = catalog_df.columns.str.strip()

# Now safely normalize Product_Name
    catalog_df["Normalized"] = catalog_df["Product_Name"].str.lower().str.strip()
    validated = {}

    for filename, order in extracted_orders.items():
        items = []
        for entry in order["items"]:
            name = entry["name"].lower().strip()
            quantity = entry["quantity"]
            match = catalog_df[catalog_df["Normalized"] == name]

            if match.empty:
                suggestion = suggest_replacement(name, catalog_df)
                items.append({
                    **entry,
                    "valid": False,
                    "issue": "Product not found in catalog",
                    "suggested_alternative": suggestion
                })
            else:
                product = match.iloc[0]
                moq = product["Min_Order_Quantity"]
                stock = product["Available_in_Stock"]
                valid_qty = quantity >= moq and quantity <= stock

                issue = None
                suggestion = None

                if quantity < moq:
                    issue = f"Quantity below MOQ ({moq})"
                    suggestion = {"suggested_qty": moq}
                elif quantity > stock:
                    issue = f"Quantity exceeds stock ({stock})"
                    suggestion = {"suggested_qty": stock}

                items.append({
                    "sku": product["Product_Code"],
                    "product_name": product["Product_Name"],
                    "quantity": quantity,
                    "price": product["Price"],
                    "total": round(product["Price"] * quantity, 2),
                    "valid": valid_qty,
                    "issue": issue,
                    "suggested_alternative": suggestion
                })

        validated[filename] = {
            "customer": order["customer"],
            "address": order["address"],
            "delivery_date": order["delivery_date"],
            "items": items
        }

    return validated

def convert_to_serializable(data):
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean(i) for i in obj]
        elif hasattr(obj, "item"):
            return obj.item()  # numpy types
        return obj

    return {filename: {
        "customer": order["customer"],
        "address": order["address"],
        "delivery_date": order["delivery_date"],
        "items": [clean(item) for item in order["items"]]
    } for filename, order in data.items()}


if __name__ == "__main__":
    extracted_orders = load_orders(INPUT_FILE)
    catalog_df = pd.read_csv(CATALOG_FILE)

    validated_data = validate_all_orders(extracted_orders, catalog_df)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(convert_to_serializable(validated_data), f, indent=4, ensure_ascii=False)

    print(f"Validated orders saved to: {OUTPUT_FILE}")
