import pdfplumber
import traceback

print("Testing protected.pdf without password...")
try:
    with pdfplumber.open("protected.pdf") as pdf:
        print(f"Opened successfully. Metadata: {pdf.metadata}")
        print(f"Pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text()
                print(f"Page {i} text: {text}")
                table = page.extract_table()
                print(f"Page {i} table: {table}")
            except Exception as e:
                print(f"Page {i} extraction error: {e}")
except Exception as e:
    print(f"Top level error: {e}")
    traceback.print_exc()
