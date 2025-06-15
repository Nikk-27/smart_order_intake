import json
import os

INPUT_FILE = "../output/validated_orders.json"
OUTPUT_FILE = "../output/final_orders.json"

def load_validated_orders(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def summarize_order(order_data):
    items = order_data["items"]
    valid_items = [item for item in items if item.get("valid")]

    total_amount = sum(item["total"] for item in valid_items)

    return {
        "customer": order_data["customer"],
        "delivery_date": order_data["delivery_date"],
        "address": order_data["address"],
        "items": items,  # all items, even invalid ones
        "total_amount": round(total_amount, 2),
        "notes": extract_note(order_data)
    }

def extract_note(order_data):
    # Placeholder logic – could be expanded to analyze original email content
    for item in order_data["items"]:
        if not item.get("valid"):
            return "Some items did not meet MOQ or stock requirements."
    return "No issues noted."

def format_final_orders(validated_orders):
    formatted_orders = {}
    for filename, order in validated_orders.items():
        formatted_orders[filename] = summarize_order(order)
    return formatted_orders

if __name__ == "__main__":
    orders = load_validated_orders(INPUT_FILE)
    formatted_orders = {}

    for filename, order in orders.items():
        formatted_orders[filename] = summarize_order(order)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(formatted_orders, f, indent=4, ensure_ascii=False)

    print(f"Final structured orders saved to: {OUTPUT_FILE}")
