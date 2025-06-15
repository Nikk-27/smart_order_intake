#  Smart Order Intake

**Zaqathon Smart Order Intake Assessment**

This project implements a pipeline that:
-  Extracts product orders from raw customer emails (`.txt`)
-  Validates them using a product catalog (`Product Catalog.csv`)
-  Outputs structured, clean JSON for both **successful** and **problematic** orders

---

##  How It Works

###  Step 1: Email Extraction (`extract/parser.py`)
- Parses all `.txt` email files in the `data/` folder
- Uses **regex** to extract:
  -  Customer name  
  -  Delivery address  
  -  Delivery deadline  
  -  Product names and quantities  

---

###  Step 2: Order Validation (`validate/validator.py`)
- Validates each item against `Product Catalog.csv`
- Performs:
  -  **SKU existence check**
  -  **Minimum Order Quantity (MOQ) check**
  -  **Stock availability check**
-  Flags issues and (optionally) suggests replacements for failed items

---

###  Step 3: JSON Formatting (`format/formatter.py`)
- Produces structured output with:
  -  Valid items with prices and total
  -  Invalid items with issues and optional suggestions
- Saves results to:
  - `output/final_orders.json`

 ---
##  Project Run

###  1. Place Inputs:
Add .txt emails and Product Catalog.csv to data/

###  2. Run the Pipeline:
python main.py

###  3. Review Outputs:
- output/extracted_orders.json – raw parsed data
- output/validated_orders.json – item-level checks
- output/final_orders.json – final structured and cleaned order

--- 

###  Features
- Intelligent text parsing using regex
- Product validation with fallback handling
- JSON output ready for downstream use
- Modular file structure for maintainability
