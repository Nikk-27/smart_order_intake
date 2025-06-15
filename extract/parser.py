import os
import re
from datetime import datetime
import json

EMAIL_DIR = "../data/"
OUTPUT_DIR = "../output/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_address(email_text):
    # Match the keyword and grab up to 3 relevant lines after it
    pattern = re.search(r"(Send to|Ship to|Ship them to|Do deliver to|Delivery address)[:\-]?\s*((?:.+\n?)+)", email_text, re.IGNORECASE)
    if pattern:
        address_lines = pattern.group(2).strip().splitlines()
        cleaned = []
        for line in address_lines:
            lower_line = line.lower().strip()
            if not line.strip():
                break
            if any(word in lower_line for word in ["cheers", "thanks", "regards", "sincerely", "warm", "before", "deadline", "requested"]):
                break
            if re.search(r"\b\d{1,2},\s+\d{4}\b", lower_line):  # matches parts of a date
                break
            cleaned.append(line.strip())
        return ", ".join(cleaned[:3])
    return "Unknown"

def extract_email_data(email_text):
    # --- Extract customer name ---
    name_match = re.findall(r"(Thanks|Warm regards|Sincerely|Cheers)[^\n]*,\s*([^\n]+)", email_text, re.IGNORECASE)
    customer = name_match[-1][1].strip() if name_match else "Unknown"

    # --- Extract delivery address ---
    address = extract_address(email_text)

    # --- Extract delivery date ---
    date_match = re.search(r"(Before|Deadline|Requested delivery date)[:\-]?\s*(\w+\s+\d{1,2},\s+\d{4})", email_text, re.IGNORECASE)
    try:
        delivery_date = datetime.strptime(date_match.group(2), "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        delivery_date = "Unknown"

    # --- Extract product lines safely ---
    product_lines = []
    line_patterns = [
        (r"(?m)^\s*[-*]?\s*(\d+)\s+pieces?:\s+(.+)", 1, 2),
        (r"(?m)^\s*[-*]?\s*(\d+)\s*[xX]\s+(.+)", 1, 2),
        (r"(?m)^\s*[-*]?\s*(.+?)\s*[-–]\s*need\s*(\d+)\s*pcs", 2, 1),
        (r"(?m)^\s*[-*]?\s*(.+?)\s*[-–]\s*Qty:\s*(\d+)", 2, 1),
        (r"(?m)^\s*(\d+)\s+units\s+of\s+(.+)", 1, 2)
    ]

    for pattern, qty_idx, name_idx in line_patterns:
        matches = re.findall(pattern, email_text)
        for m in matches:
            try:
                qty = int(m[qty_idx - 1])
                name = m[name_idx - 1].strip().rstrip(".")
                if name:
                    product_lines.append({"name": name, "quantity": qty})
            except:
                continue

    return {
        "customer": customer,
        "delivery_date": delivery_date,
        "address": address,
        "items": product_lines
    }

def process_all_emails(email_dir):
    extracted_orders = {}
    for filename in os.listdir(email_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(email_dir, filename), "r", encoding="utf-8") as f:
                email_text = f.read()
                order_data = extract_email_data(email_text)
                extracted_orders[filename] = order_data
    return extracted_orders

if __name__ == "__main__":
    orders = process_all_emails(EMAIL_DIR)

    # Save results
    output_path = os.path.join(OUTPUT_DIR, "extracted_orders.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)

    print(f"Extracted orders saved to: {output_path}")
