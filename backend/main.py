from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pandas as pd
import sqlite3
import pdfplumber
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from services.categorization import categorizer

app = FastAPI(title="SpendSense AI API")

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
def parse_pdf(file_path):
    transactions = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Strategy 1: Default (Lines)
                table = page.extract_table()
                
                # Strategy 2: Text-based (Whitespace)
                if not table:
                    print(f"DEBUG: Default extraction failed. Trying text strategy...")
                    table = page.extract_table({
                        "vertical_strategy": "text", 
                        "horizontal_strategy": "text",
                        "snap_tolerance": 3,
                    })
                
                if table:
                    print(f"DEBUG: PDF Page {page.page_number} extracted table with {len(table)} rows")
                    
                    # Search for header row
                    header_row_idx = -1
                    for i, row in enumerate(table[:5]): # Check first 5 rows
                        # Clean row for check
                        row_str = [str(cell).lower().strip() for cell in row if cell]
                        if any('date' in c for c in row_str) and any('amount' in c for c in row_str):
                            header_row_idx = i
                            break
                    
                    if header_row_idx == -1:
                        print("DEBUG: Could not find header row (Date/Amount) in first 5 rows")
                        if len(table) > 0:
                             # Fallback: Use first row if it looks reasonable
                             header_row_idx = 0
                    
                    if header_row_idx != -1:
                        raw_headers = table[header_row_idx]
                        print(f"DEBUG: Using header row {header_row_idx}: {raw_headers}")
                        headers = [str(h).lower().strip() if h else f"col_{i}" for i, h in enumerate(raw_headers)]
                        
                        for row in table[header_row_idx + 1:]:
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

        # Similar normalization as CSV
        rename_map = {
            'date': 'date',
            'transaction date': 'date',
            'description': 'description',
            'details': 'description',
            'amount': 'amount',
            'category': 'category'
        }
        df = df.rename(columns=rename_map)
         
        # Clean amount (remove currency symbols)
        if 'amount' in df.columns:
            df['amount'] = df['amount'].astype(str).str.replace(r'[$,]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
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
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

@app.get("/")
def read_root():
    return {"message": "SpendSense AI Backend is running"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process logic
        df = pd.DataFrame()
        if file.filename.endswith('.csv'):
            df = parse_csv(file_location)
        elif file.filename.endswith('.pdf'):
            df = parse_pdf(file_location)
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
