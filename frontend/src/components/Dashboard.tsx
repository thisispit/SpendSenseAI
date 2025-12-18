import { useRef, useState } from "react";
import { mockTransactions } from "../data/mockData";
import { SummaryCard } from "./SummaryCard";
import { CategoryChart } from "./CategoryChart";
import { TrendChart } from "./TrendChart";
import { TransactionTable } from "./TransactionTable";
import { Upload, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { uploadFile } from "../lib/api";

export function Dashboard() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");

  const totalIncome = mockTransactions
    .filter((t) => t.type === "CREDIT")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const totalExpense = mockTransactions
    .filter((t) => t.type === "DEBIT")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");

    try {
      await uploadFile(file);
      setUploadStatus("success");
      // Reset after 3 seconds
      setTimeout(() => setUploadStatus("idle"), 3000);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("error");
    } finally {
      setIsUploading(false);
      // Reset input value to allow uploading the same file again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center backdrop-blur-sm bg-white/30 p-6 rounded-2xl border border-white/20 shadow-sm">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">SpendSense AI</h1>
            <p className="text-gray-600 mt-1 font-medium">Financial Insights Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            {uploadStatus === "success" && (
              <span className="text-green-600 flex items-center gap-1 text-sm font-medium animate-in fade-in slide-in-from-right-2">
                <CheckCircle className="w-4 h-4" /> Uploaded!
              </span>
            )}
            {uploadStatus === "error" && (
              <span className="text-red-600 flex items-center gap-1 text-sm font-medium animate-in fade-in slide-in-from-right-2">
                <AlertCircle className="w-4 h-4" /> Failed
              </span>
            )}
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

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SummaryCard title="Total Income" amount={totalIncome} type="income" />
          <SummaryCard title="Total Expenses" amount={totalExpense} type="expense" />
          <SummaryCard title="Net Balance" amount={totalIncome - totalExpense} type={totalIncome - totalExpense >= 0 ? "income" : "expense"} />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CategoryChart transactions={mockTransactions} />
          <TrendChart transactions={mockTransactions} />
        </div>

        {/* Recent Transactions */}
        <TransactionTable transactions={mockTransactions} />
      </div>
    </div>
  );
}