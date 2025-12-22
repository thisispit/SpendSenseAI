# 💰 SpendSenseAI

**AI-Powered Personal Finance Tracker** — Intelligently track, categorize, and visualize your financial transactions from bank statements.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-19.2-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-green.svg)

---

## ✨ Features

- 📤 **Upload CSV/PDF** bank statements (including password-protected PDFs)
- 🤖 **AI Auto-Categorization** of transactions
- 📊 **Interactive Dashboard** with charts and analytics
- 🔍 **Smart Filters** by date, category, and amount
- 🔒 **Privacy-First** — All data stored locally

---

## 🛠️ Tech Stack

**Frontend:** React 19 • TypeScript • TailwindCSS • Recharts • Vite  
**Backend:** FastAPI • Python 3.8+ • Pandas • PDFPlumber • SQLite

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/thisispit/SpendSenseAI.git
cd SpendSenseAI
```

---

### Step 2: Backend Setup & Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# For Windows:
.venv\Scripts\activate

# For macOS/Linux:
# source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Backend requirements.txt includes:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - File upload support
- `pandas` - Data processing
- `pdfplumber` - PDF parsing

---

### Step 3: Frontend Setup & Installation

```bash
# Navigate to frontend directory (from project root)
cd ../frontend

# Install Node.js dependencies
npm install
```

**This will install React, TypeScript, TailwindCSS, Recharts, and other dependencies.**

---

### Step 4: Run the Application

**Open 2 separate terminals:**

#### 🟢 Terminal 1: Start Backend Server

```bash
# From project root
cd backend

# Activate virtual environment
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Start FastAPI backend
uvicorn main:app --reload
```

✅ **Backend running at:** http://localhost:8000  
📚 **API Documentation:** http://localhost:8000/docs

---

#### 🔵 Terminal 2: Start Frontend Server

```bash
# From project root
cd frontend

# Start Vite dev server
npm run dev
```

✅ **Frontend running at:** http://localhost:5173

---

### Step 5: Verify & Test

1. Open **http://localhost:5173** in your browser
2. You should see the SpendSenseAI dashboard
3. Click **"Upload Statement"** and try uploading:
   - `sample_transactions.csv`
   - `sample_statement.pdf`
   - `protected.pdf` (password-protected test file)

---

## 📂 Project Structure

```
SpendSenseAI/
├── backend/
│   ├── services/
│   │   └── categorization.py    # AI categorizer
│   ├── main.py                   # FastAPI app
│   ├── requirements.txt
│   └── transactions.db
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard, Charts, Tables
│   │   └── App.tsx
│   └── package.json
├── sample_transactions.csv       # Test files
├── sample_statement.pdf
└── README.md
```

---

## 🔌 API Endpoints

```
POST   /api/upload              Upload CSV/PDF
GET    /api/transactions        Get all transactions
DELETE /api/transactions        Clear all data
GET    /api/files               List uploaded files
DELETE /api/files/{filename}    Delete specific file
```

---

## 🧠 AI Categories

💳 Bills & Utilities • 🍔 Food & Dining • 🛍️ Shopping • 🚗 Transportation  
🎬 Entertainment • 💪 Health & Fitness • ✈️ Travel • 💰 Income  
📊 Investments • 🏠 Home • 📚 Education • 🎁 Gifts & Donations

---

## 📖 Usage

1. Open **http://localhost:5173**
2. Click **Upload** and select a file:
   - CSV: `Date, Description, Debit, Credit`
   - PDF: Standard bank statement format
3. View transactions on interactive dashboard
4. Filter by date, category, or search

**Test Files Included:**
- `sample_transactions.csv`
- `sample_statement.pdf`
- `protected.pdf` (password-protected)

---

## 🗺️ Roadmap

**Completed ✅**
- CSV/PDF parsing with multi-page support
- AI categorization
- Dashboard with charts & filters
- Duplicate prevention

**Coming Soon 🚧**
- Manual recategorization
- Budget tracking & alerts
- Multi-currency support
- Dark mode
- Mobile app
- Advanced ML models

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file

---

## 👤 Author

**Pitam Sarkar** ([@thisispit](https://github.com/thisispit))

---

<div align="center">

**Built with ❤️ using React, FastAPI, and AI**

⭐ Star this repo if you find it helpful!

</div>
