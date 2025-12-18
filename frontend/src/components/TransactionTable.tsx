import { useState } from "react";
import { type Transaction, categories } from "../data/mockData";
import { cn } from "../lib/utils";
import { Search } from "lucide-react";

interface TransactionTableProps {
  transactions: Transaction[];
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  const [filterCategory, setFilterCategory] = useState<string>("All");

  const filteredTransactions = filterCategory === "All"
    ? transactions
    : transactions.filter(t => t.category === filterCategory);

  return (
    <div className="overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search transactions..."
            className="pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all w-64"
          />
        </div>
        <select
          className="bg-slate-50 border border-slate-200 text-slate-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer hover:bg-slate-100"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="All">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50/50 text-slate-500 font-semibold border-b border-slate-200">
            <tr>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Description</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4 text-right">Amount</th>
              <th className="px-6 py-4 text-center">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {filteredTransactions.map((t) => (
              <tr key={t.id} className="hover:bg-slate-50/80 transition-colors group">
                <td className="px-6 py-4 text-slate-500 font-medium whitespace-nowrap">{t.date}</td>
                <td className="px-6 py-4 font-medium text-slate-800">
                  {t.description}
                  <div className="text-xs text-slate-400 font-normal mt-0.5">{t.account}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={cn(
                    "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border",
                    t.category === 'Food & Dining' ? "bg-orange-50 text-orange-700 border-orange-100" :
                      t.category === 'Transportation' ? "bg-blue-50 text-blue-700 border-blue-100" :
                        t.category === 'Shopping' ? "bg-purple-50 text-purple-700 border-purple-100" :
                          "bg-slate-50 text-slate-700 border-slate-100"
                  )}>
                    {t.category}
                  </span>
                </td>
                <td className={cn("px-6 py-4 text-right font-bold text-base", t.type === "CREDIT" ? "text-emerald-600" : "text-slate-800")}>
                  {t.type === "CREDIT" ? "+" : ""}₹{t.amount.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-center">
                  <div className="flex items-center justify-center gap-2" title={`${Math.round(t.confidence * 100)}% Match`}>
                    <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full transition-all duration-500",
                          t.confidence > 0.9 ? "bg-emerald-500" :
                            t.confidence > 0.7 ? "bg-amber-500" : "bg-rose-500"
                        )}
                        style={{ width: `${t.confidence * 100}%` }}
                      />
                    </div>
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
