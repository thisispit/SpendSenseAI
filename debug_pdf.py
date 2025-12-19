import pdfplumber
import pandas as pd
import traceback

file_path = "sample_statement.pdf"

print(f"Testing PDF: {file_path}")

try:
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            print(f"--- Page {page.page_number} ---")
            
            # Strategy 1
            table = page.extract_table()
            print(f"Strategy 1 (Default): {table}")
            
            if not table:
                print("Trying Strategy 2 (Text)...")
                table = page.extract_table({
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                })
                print(f"Strategy 2 Result: {table}")
            
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                print("Extracted DataFrame:")
                print(df)
            else:
                print("No table found.")

except Exception:
    traceback.print_exc()
