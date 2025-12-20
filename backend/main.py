from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pandas as pd
import sqlite3
import pdfplumber
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from services.categorization import Categorizer

app = FastAPI(title="SpendSense AI API")

# Initialize AI Service
categorizer = Categorizer()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_PATH = "transactions.db"

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Reset on startup
    cursor.execute("DROP TABLE IF EXISTS transactions")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            source_file TEXT,
            UNIQUE(date, description, amount)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Models
class Transaction(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    category: str
    source_file: str

# Helper: Parse CSV
def parse_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        # Basic normalization - simplistic assumption of column names
        # In a real app, we'd need smarter column mapping
        df.columns = [c.lower().strip() for c in df.columns]
        print(f"DEBUG: Found CSV columns: {df.columns.tolist()}")
        
        # Map common names to our schema
        rename_map = {
            'date': 'date',
            'transaction date': 'date',
            'description': 'description',
            'details': 'description',
            'merchant': 'description',
            'amount': 'amount',
            'debit': 'amount', # Logic needed for debit/credit
            'category': 'category'
        }
        df = df.rename(columns=rename_map)
        
        # Ensure required columns exist
        required = ['date', 'description', 'amount']
        for col in required:
            if col not in df.columns:
                 # Fallback for amount if debit/credit exist
                 if col == 'amount' and 'credit' in df.columns:
                     df['amount'] = df.apply(lambda x: x['credit'] if pd.notnull(x.get('credit')) else -x.get('debit', 0), axis=1)
                 else:
                    raise ValueError(f"Missing required column: {col}")

        if 'category' not in df.columns:
            df['category'] = 'Uncategorized'

        df['amount'] = df['amount'].astype(str).str.replace(r'[$,]', '', regex=True)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # KEYWORD AI: Predict category if missing/uncategorized
        df['category'] = df.apply(
            lambda row: categorizer.predict(row['description']) if (pd.isna(row.get('category')) or row.get('category') == 'Uncategorized') else row['category'], 
            axis=1
        )
            
        return df[['date', 'description', 'amount', 'category']].dropna(subset=['amount', 'date'])
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CSV Parse Error: {e}")
        return pd.DataFrame()

# Helper: Parse PDF
def parse_pdf(file_path, password=None):
    transactions = []
    try:
        # Handling the Password
        # pdfplumber passes kwargs to pdfminer.pdfdocument.PDFDocument
        # We try to open. If it raises error about password, we catch it.
        try:
            pdf = pdfplumber.open(file_path, password=password or "")
        except Exception as e:
            # pdfminer usually raises PDFPasswordIncorrect or similar.
            # We check the message since importing the exact exception can be brittle.
            err_msg = str(e).lower()
            if "password" in err_msg or "initialized" in err_msg: # 'PDFPasswordIncorrect' or 'not initialized'
                 raise ValueError("PASSWORD_REQUIRED")
            raise e

        with pdf:
            for page in pdf.pages:
                # Helper to check if a row looks like data (SBI format)
                def is_data_row(row):
                    # SBI: 7 cols. Date, ValDate, Desc, Ref, Debit, Credit, Bal
                    if len(row) < 5: return False
                    
                    # Check Date (Col 0)
                    date_str = str(row[0]).strip()
                    # Simple Regex for DD-Mon-YYYY or DD/MM/YYYY
                    import re
                    if not re.search(r'\d{1,2}[-\s/][A-Za-z0-9]{3,}[-\s/]\d{2,4}', date_str):
                        return False
                        
                    # Check for Number in Debit(4) or Credit(5) or Balance(-1)
                    # We look for at least one number-like string in the last few columns
                    found_number = False
                    for cell in row[4:]: # Check from Col 4 onwards
                        clean_cell = str(cell).replace(',','').strip()
                        if re.match(r'^\d+(\.\d+)?$', clean_cell):
                            found_number = True
                            break
                    
                    return found_number

                # Try each strategy
                strategies = [
                    ("Default", {}),
                    ("Fuzzy Lines", {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 5, "join_tolerance": 5}),
                    ("Text", {"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 3}),
                ]
                
                table = None
                header_row_idx = -1
                found_via_heuristic = False

                for name, settings in strategies:
                    print(f"DEBUG: Trying Strategy: {name}")
                    try:
                        extracted = page.extract_table(settings)
                        if not extracted: continue

                        # 1. Try Header Match
                        idx = find_header(extracted)
                        if idx != -1:
                             print(f"DEBUG: Header found with strategy {name} at row {idx}")
                             table = extracted
                             header_row_idx = idx
                             found_via_heuristic = False
                             break
                        
                        # 2. Try Heuristic Data Match (Fallback)
                        print(f"DEBUG: Header search failed for {name}. Checking for data content match...")
                        for i, row in enumerate(extracted[:50]):
                             if is_data_row(row):
                                 print(f"DEBUG: Heuristic Data Match found at row {i} with strategy {name}")
                                 table = extracted
                                 header_row_idx = i - 1 # Assume header is row before, or just start data here
                                 found_via_heuristic = True
                                 # Force standard SBI headers
                                 # We need to inject a header row if we are starting at data
                                 break
                        
                        if found_via_heuristic:
                            break
                            
                    except Exception as e:
                         print(f"DEBUG: Strategy {name} failed: {e}")
                
                # ... (strategies loop end)
                
                # FINAL FALLBACK: Simple Text Line Parsing
                # If table extraction failed for THIS page, try reading text line by line.
                # This runs PER PAGE, not just once globally.
                if not table: # Try fallback if no table found on this specific page
                    print(f"DEBUG: Table extraction failed on this page. Attempting raw text parsing...")
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        import re
                        for line_num, line in enumerate(lines):
                            # Skip empty or very short lines
                            if not line or len(line.strip()) < 10:
                                continue
                            
                            # Match date patterns (DD-Mon-YYYY, DD/MM/YYYY, DD-MM-YYYY)
                            date_match = re.search(r'(\d{1,2}[-\s/][A-Za-z]{3}[-\s/]\d{2,4})', line)
                            if not date_match:
                                # Try numeric date format DD/MM/YYYY or DD-MM-YYYY
                                date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', line)
                            
                            # Match amounts - look for numbers with optional decimals and commas
                            amount_matches = list(re.finditer(r'(-?[\d,]+\.?\d*)', line))
                            # Filter to keep only valid amounts
                            amount_matches = [m for m in amount_matches if '.' in m.group() or len(m.group().replace(',','')) > 1]
                            
                            if date_match and amount_matches:
                                date_val = date_match.group(1).strip()
                                # Take the last number as amount
                                amount_val = amount_matches[-1].group(1).replace(',', '').strip()
                                
                                # Description is everything between date and amount
                                start_desc = date_match.end()
                                end_desc = amount_matches[-1].start()
                                desc_val = line[start_desc:end_desc].strip()
                                
                                # Only add if we have a meaningful description
                                if desc_val and len(desc_val) > 2:
                                    print(f"DEBUG: Text Fallback Line {line_num}: {date_val} | {desc_val} | {amount_val}")
                                    transactions.append({
                                        'date': date_val,
                                        'description': desc_val,
                                        'amount': amount_val,
                                        'category': 'Uncategorized'
                                    })

                if table:
                    # If we found via heuristic, we might not have the header row index pointing to a header.
                    # It points to the pre-data row.
                    
                    raw_headers = []
                    if found_via_heuristic:
                         print("DEBUG: Using Hardcoded SBI Headers due to Heuristic Match")
                         # SBI Standard Map
                         # Note: `zip` will cut off extra columns if we provide fewer headers, 
                         # or drop data if we provide too many. 
                         # We try to align with the detected table width.
                         if len(table[0]) >= 7:
                             headers = ['date', 'value_date', 'description', 'ref', 'debit', 'credit', 'balance']
                         else:
                             headers = ['date', 'description', 'ref', 'debit', 'credit', 'balance'] # Fallback
                         
                         # Since header_row_idx points to the row *before* data (or arbitrary),
                         # we process rows starting from header_row_idx + 1.
                         # If header_row_idx was set to i matching data, we should treat i as data.
                         # Let's adjust: if found_via_heuristic, header_row_idx is the *first data row index*.
                         pass 
                    elif header_row_idx != -1:
                        raw_headers = table[header_row_idx]
                        print(f"DEBUG: Using header row {header_row_idx}: {raw_headers}")
                        headers = [str(h).lower().strip() if h else f"col_{i}" for i, h in enumerate(raw_headers)]
                    else:
                        continue # Skip page if no header and no heuristic found
                        
                    start_row = header_row_idx if found_via_heuristic else header_row_idx + 1
                    
                    for row in table[start_row:]:
                            # Skip empty rows or rows with completely different length
                            # Relax length check: match if at least 3 cols match (date/desc/amount)
                            # But for now, let's just zip what we can
                            clean_row = [cell if cell else "" for cell in row]
                            # Pad row if shorter
                            if len(clean_row) < len(headers):
                                clean_row += [""] * (len(headers) - len(clean_row))
                            
                            # Truncate if longer
                            clean_row = clean_row[:len(headers)]
                            
                            transactions.append(dict(zip(headers, clean_row)))
        
        print(f"DEBUG: Extracted {len(transactions)} raw rows from PDF")
        df = pd.DataFrame(transactions)
        
        if not df.empty:
             print(f"DEBUG: PDF Columns: {df.columns.tolist()}")

        # Normalize Columns
        rename_map = {
            'date': 'date',
            'txn date': 'date',
            'transaction date': 'date',
            'description': 'description',
            'details': 'description',
            'narration': 'description',
            'particulars': 'description',
            'ref no': 'description',
            'cheque': 'description',
            'reference': 'description',
            'amount': 'amount',
            'debit': 'debit',
            'credit': 'credit',
            'dr': 'debit',
            'cr': 'credit',
            'withdrawal': 'debit',
            'deposit': 'credit',
            'category': 'category'
        }
        
        # Fuzzy match rename
        new_cols = {}
        for col in df.columns:
            for key in rename_map:
                if key in col:
                    new_cols[col] = rename_map[key]
                    break
        df = df.rename(columns=new_cols)
        
        # Calculate Amount from Debit/Credit if missing
        if 'amount' not in df.columns:
             # Try stricter Debit/Credit matching first
             if 'debit' in df.columns and 'credit' in df.columns:
                 print("DEBUG: Calculating amount from Debit/Credit columns")
                 # Clean and convert both columns
                 df['debit'] = df['debit'].astype(str).str.replace(r'[$,]', '', regex=True)
                 df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
                 df['credit'] = df['credit'].astype(str).str.replace(r'[$,]', '', regex=True)
                 df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
                 
                 # For each row: if debit has value, amount is -debit; if credit has value, amount is +credit
                 # This properly handles cases where one column is empty
                 df['amount'] = df.apply(lambda row: 
                     -row['debit'] if row['debit'] != 0 else row['credit'], 
                     axis=1)
                 
                 print(f"DEBUG: Sample amounts - Debits: {df[df['debit'] > 0]['amount'].head().tolist()}, Credits: {df[df['credit'] > 0]['amount'].head().tolist()}")
                 
             # Fallback: if only one exists (e.g. only withdrawals on page)
             elif 'debit' in df.columns:
                 print("DEBUG: Calculating amount from Debit only")
                 df['debit'] = df['debit'].astype(str).str.replace(r'[$,]', '', regex=True)
                 df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
                 df['amount'] = -df['debit']
             elif 'credit' in df.columns:
                 print("DEBUG: Calculating amount from Credit only")
                 df['credit'] = df['credit'].astype(str).str.replace(r'[$,]', '', regex=True)
                 df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
                 df['amount'] = df['credit']

        # Clean amount (remove currency symbols)
        if 'amount' in df.columns and df['amount'].dtype == 'object':
            df['amount'] = df['amount'].astype(str).str.replace(r'[$,]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Drop rows with invalid amount
        if 'amount' in df.columns:
             df = df.dropna(subset=['amount'])

        # Fix Dates
        if 'date' in df.columns:
             # Attempt to parse common bank formats
             df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
             df = df.dropna(subset=['date'])
             df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        if 'category' not in df.columns:
            df['category'] = 'Uncategorized'
            
        # KEYWORD AI: Predict category if missing/uncategorized
        df['category'] = df.apply(
            lambda row: categorizer.predict(row['description']) if (pd.isna(row.get('category')) or row.get('category') == 'Uncategorized') else row['category'], 
            axis=1
        )
            
        required = ['date', 'description', 'amount']
        
        # Check if columns exist
        missing = [col for col in required if col not in df.columns]
        if missing:
             print(f"DEBUG: PDF Missing required columns: {missing}")

        # Filter valid rows
        if all(col in df.columns for col in required):
            return df[required + ['category']].dropna(subset=['amount'])
            
        return pd.DataFrame() # Fallback empty
        
    except Exception as e:
        # Check if it was a password error raised during processing
        err_msg = repr(e).lower()
        if "password" in err_msg or "initialized" in err_msg:
             raise ValueError("PASSWORD_REQUIRED")
        
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

@app.get("/")
def read_root():
    return {"message": "SpendSense AI Backend is running"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), password: Optional[str] = Form(None)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process logic
        df = pd.DataFrame()
        if file.filename.endswith('.csv'):
            df = parse_csv(file_location)
        elif file.filename.endswith('.pdf'):
            try:
                df = parse_pdf(file_location, password=password)
            except ValueError as e:
                if str(e) == "PASSWORD_REQUIRED":
                     return {"status": "error", "code": "PASSWORD_REQUIRED", "message": "This PDF is password protected."}
                raise e
        else:
             return {"status": "error", "message": "Unsupported file format"}
             
        if not df.empty:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            rows_inserted = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT INTO transactions (date, description, amount, category, source_file)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (row['date'], row['description'], row['amount'], row['category'], file.filename))
                    rows_inserted += 1
                except sqlite3.IntegrityError:
                    pass # Skip duplicate
            
            conn.commit()
            conn.close()
            
            if rows_inserted == 0 and len(df) > 0:
                 return {"status": "warning", "message": "No new transactions. Duplicates skipped."}
            
            return {"status": "success", "message": f"Processed {rows_inserted} new transactions"}
        else:
            return {"status": "warning", "message": "File uploaded but no transactions found"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions")
def get_transactions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.delete("/api/transactions")
def clear_transactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()
    return {"message": "All transactions cleared"}

@app.get("/api/files")
def get_files():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT source_file, COUNT(*) as count FROM transactions GROUP BY source_file")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row["source_file"], "count": row["count"]} for row in rows]

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE source_file = ?", (filename,))
    conn.commit()
    conn.close()
    return {"message": f"Deleted transactions from {filename}"}
