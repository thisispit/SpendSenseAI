import { useRef, useState, useEffect } from "react";
import { SummaryCard } from "./SummaryCard";
import { CategoryChart } from "./CategoryChart";
import { TrendChart } from "./TrendChart";
import { TransactionTable } from "./TransactionTable";
import { Upload, Loader2, CheckCircle, AlertCircle, Trash2, FileText } from "lucide-react";
import { uploadFile, getTransactions, getFiles, deleteFile } from "../lib/api";
import type { Transaction } from "../types/transaction";
import axios from 'axios';

interface UploadedFile {
  name: string;
  count: number;
}

export function Dashboard() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error" | "warning">("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [txData, filesData] = await Promise.all([
        getTransactions(),
        getFiles()
      ]);

      const mapped: Transaction[] = txData.map((t: any) => ({
        id: t.id.toString(),
        date: t.date,
        description: t.description,
        amount: Math.abs(t.amount),
        category: t.category,
        confidence: 1.0,
        source: 'UPLOAD',
        account: 'Unknown',
        merchant: t.description,
        type: t.amount > 0 ? 'CREDIT' : 'DEBIT'
      }));
      setTransactions(mapped);
      setFiles(filesData);
      setLoading(false);
    } catch (e) {
      console.error("Failed to fetch data", e);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalIncome = transactions
    .filter((t) => t.type === "CREDIT")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const totalExpense = transactions
    .filter((t) => t.type === "DEBIT")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleReset = async () => {
    if (confirm("Are you sure you want to clear all data? This cannot be undone.")) {
      try {
        await axios.delete('http://localhost:8000/api/transactions');
        fetchData();
        setUploadStatus("success");
        setStatusMessage("Session reset locally");
        setTimeout(() => setUploadStatus("idle"), 3000);
      } catch (e) {
        console.error("Reset failed", e);
      }
    }
  };

  const handleDeleteFile = async (filename: string) => {
    if (confirm(`Delete all transactions from ${filename}?`)) {
      try {
        await deleteFile(filename);
        fetchData();
      } catch (e) {
        console.error("Delete failed", e);
      }
    }
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");
    setStatusMessage("");

    try {
      const response = await uploadFile(file);
      setUploadStatus(response.status === 'success' ? 'success' : 'warning');
      setStatusMessage(response.message || "Upload complete");

      fetchData();
      setTimeout(() => setUploadStatus("idle"), 5000);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("error");
      setStatusMessage(`Upload failed: ${error instanceof Error ? error.message : "Unknown error"}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 selection:bg-indigo-100 selection:text-indigo-700 font-sans">
      {/* Sticky Glass Header */}
      <header className="sticky top-0 z-50 glass-panel border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center shadow-lg shadow-slate-900/20">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">SpendSense AI</h1>
              <p className="text-xs text-slate-500 font-medium">Financial Intelligence</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Status Pill */}
            {uploadStatus !== "idle" && (
              <span className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full ring-1 ring-inset animate-in fade-in slide-in-from-top-2 ${uploadStatus === 'success' ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' :
                uploadStatus === 'warning' ? 'bg-amber-50 text-amber-700 ring-amber-200' :
                  'bg-rose-50 text-rose-700 ring-rose-200'
                }`}>
                {uploadStatus === 'success' && <CheckCircle className="w-3.5 h-3.5" />}
                {uploadStatus === 'warning' && <AlertCircle className="w-3.5 h-3.5" />}
                {uploadStatus === 'error' && <AlertCircle className="w-3.5 h-3.5" />}
                {statusMessage}
              </span>
            )}

            <button
              onClick={handleReset}
              className="p-2.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-full transition-all duration-200"
              title="Reset Session"
            >
              <Trash2 className="w-5 h-5" />
            </button>

            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png,.csv"
            />
            <button
              onClick={handleUploadClick}
              disabled={isUploading}
              className="btn-primary"
            >
              {isUploading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              {isUploading ? "Uploading..." : "Upload Statement"}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {transactions.length === 0 ? (
          <div className="text-center py-32 glass-panel rounded-3xl border border-dashed border-slate-300">
            <div className="mx-auto w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
              <Upload className="w-10 h-10 text-slate-400" />
            </div>
            <h3 className="text-2xl font-bold text-slate-900">Your Financial Journey Starts Here</h3>
            <p className="text-slate-500 mt-3 max-w-lg mx-auto text-lg">Upload your bank statement (PDF or CSV) to instantly unlock insights about your spending habits.</p>
            <button
              onClick={handleUploadClick}
              className="mt-8 text-indigo-600 font-semibold hover:text-indigo-700 hover:underline transition-all"
            >
              Browse files
            </button>
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <SummaryCard title="Total Income" amount={totalIncome} type="income" />
              <SummaryCard title="Total Expenses" amount={totalExpense} type="expense" />
              <SummaryCard title="Net Balance" amount={totalIncome - totalExpense} type={totalIncome - totalExpense >= 0 ? "income" : "expense"} />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <div className="glass-card p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Expense Distribution</h3>
                <CategoryChart transactions={transactions} />
              </div>
              <div className="glass-card p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Monthly Trends</h3>
                <TrendChart transactions={transactions} />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Transaction Table (Takes up 2/3) */}
              <div className="lg:col-span-2 space-y-6">
                <div className="glass-card p-6 rounded-2xl">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold text-slate-800">Recent Transactions</h3>
                    <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700">View All</button>
                  </div>
                  <TransactionTable transactions={transactions} />
                </div>
              </div>

              {/* Right Column: Files & Info (Takes up 1/3) */}
              <div className="space-y-6">
                {files.length > 0 && (
                  <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-md font-bold text-slate-800 mb-4 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-500" /> Data Sources
                    </h3>
                    <div className="space-y-3">
                      {files.map((file, idx) => (
                        <div key={idx} className="group flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-200 transition-all">
                          <div className="overflow-hidden">
                            <p className="font-semibold text-sm text-slate-700 truncate" title={file.name}>{file.name}</p>
                            <p className="text-xs text-slate-400 font-medium mt-0.5">{file.count} txns</p>
                          </div>
                          <button
                            onClick={() => handleDeleteFile(file.name)}
                            className="p-1.5 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                            title="Delete file"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-indigo-900 p-6 rounded-2xl text-white shadow-xl shadow-indigo-900/20">
                  <h4 className="font-bold text-lg mb-2">AI Insights</h4>
                  <p className="text-indigo-200 text-sm leading-relaxed">
                    Your dining expenses have increased by 15% this month. Consider setting a budget for next week.
                  </p>
                  <div className="mt-4 pt-4 border-t border-indigo-800">
                    <button className="text-xs font-semibold uppercase tracking-wider text-indigo-300 hover:text-white transition-colors">Generate Full Report &rarr;</button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}