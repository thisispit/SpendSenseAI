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
      setStatusMessage("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">SpendSense AI</h1>
            <p className="text-gray-600 mt-1 font-medium">Financial Insights Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            {/* Status Messages */}
            {uploadStatus !== "idle" && (
              <span className={`flex items-center gap-2 text-sm font-medium animate-in fade-in slide-in-from-right-2 px-3 py-1 rounded-full ${uploadStatus === 'success' ? 'bg-green-100 text-green-700' :
                  uploadStatus === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                }`}>
                {uploadStatus === 'success' && <CheckCircle className="w-4 h-4" />}
                {uploadStatus === 'warning' && <AlertCircle className="w-4 h-4" />}
                {uploadStatus === 'error' && <AlertCircle className="w-4 h-4" />}
                {statusMessage}
              </span>
            )}

            <button
              onClick={handleReset}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
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
              className="flex items-center gap-2 bg-gray-900 text-white px-5 py-2.5 rounded-xl hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
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

        {transactions.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">No transactions yet</h3>
            <p className="text-gray-500 mt-2 max-w-md mx-auto">Upload a bank statement (PDF or CSV) to see your financial insights instantly.</p>
            <button
              onClick={handleUploadClick}
              className="mt-6 text-blue-600 font-medium hover:underline"
            >
              Upload now
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

            {/* File Management Section */}
            {files.length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-gray-500" /> Uploaded Sources
                </h3>
                <div className="flex flex-wrap gap-4">
                  {files.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 min-w-[200px]">
                      <div>
                        <p className="font-medium text-sm text-gray-800 truncate max-w-[150px]" title={file.name}>{file.name}</p>
                        <p className="text-xs text-gray-500">{file.count} transactions</p>
                      </div>
                      <button
                        onClick={() => handleDeleteFile(file.name)}
                        className="ml-3 p-1 text-gray-400 hover:text-red-500 transition-colors"
                        title="Delete file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CategoryChart transactions={transactions} />
              <TrendChart transactions={transactions} />
            </div>

            {/* Recent Transactions */}
            <TransactionTable transactions={transactions} />
          </>
        )}
      </div>
    </div>
  );
}