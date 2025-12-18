import { useState } from "react";
import { type Transaction, categories } from "../data/mockData";
import { cn } from "../lib/utils";

interface TransactionTableProps {
  transactions: Transaction[];
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  const [filterCategory, setFilterCategory] = useState<string>("All");

  const filteredTransactions = filterCategory === "All"
    ? transactions
    : transactions.filter(t => t.category === filterCategory);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-6 border-b border-gray-100 flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Recent Transactions</h3>
        <select
          className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="All">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-100">
            <tr>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Description</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4">Account</th>
              <th className="px-6 py-4 text-right">Amount</th>
              <th className="px-6 py-4 text-center">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredTransactions.map((t) => (
              <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-gray-500">{t.date}</td>
                <td className="px-6 py-4 font-medium text-gray-900">{t.description}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {t.category}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-500">{t.account}</td>
                <td className={cn("px-6 py-4 text-right font-medium", t.type === "CREDIT" ? "text-green-600" : "text-red-600")}>
                  {t.type === "CREDIT" ? "+" : "-"}₹{t.amount.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-center">
                  <div className="flex items-center justify-center gap-1">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full", t.confidence > 0.9 ? "bg-green-500" : t.confidence > 0.7 ? "bg-yellow-500" : "bg-red-500")}
                        style={{ width: `${t.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{Math.round(t.confidence * 100)}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
