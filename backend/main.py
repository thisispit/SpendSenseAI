from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pandas as pd
import sqlite3
import pdfplumber
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

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

        # Clean amount if it's string
        if df['amount'].dtype == 'object':
             df['amount'] = df['amount'].astype(str).str.replace(r'[$,]', '', regex=True)
             df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
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
                table = page.extract_table()
                if table:
                    # Assume first row is header
                    headers = [h.lower() if h else f"col_{i}" for i, h in enumerate(table[0])]
                    for row in table[1:]:
                        if len(row) == len(headers):
                            transactions.append(dict(zip(headers, row)))
        
        df = pd.DataFrame(transactions)
        
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
            
        required = ['date', 'description', 'amount']
        # Filter valid rows
        if all(col in df.columns for col in required):
            return df[required + ['category']].dropna(subset=['amount'])
            
        return pd.DataFrame() # Fallback empty
        
    except Exception as e:
        print(f"PDF Parse Error: {e}")
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
