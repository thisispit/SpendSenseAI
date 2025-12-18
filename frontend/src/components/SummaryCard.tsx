import { ArrowDownIcon, ArrowUpIcon } from "lucide-react";
import { cn } from "../lib/utils";

interface SummaryCardProps {
    title: string;
    amount: number;
    type: "income" | "expense";
}

export function SummaryCard({ title, amount, type }: SummaryCardProps) {
    const isIncome = type === "income";

    return (
        <div className={cn(
            "p-6 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg",
            isIncome
                ? "bg-gradient-to-br from-white to-emerald-50 border-emerald-100 shadow-emerald-100/50"
                : "bg-gradient-to-br from-white to-rose-50 border-rose-100 shadow-rose-100/50"
        )}>
            <div className="flex items-center justify-between mb-4">
                <div className={cn("p-2.5 rounded-xl", isIncome ? "bg-emerald-100 text-emerald-600" : "bg-rose-100 text-rose-600")}>
                    {isIncome ? <ArrowUpIcon className="w-5 h-5" /> : <ArrowDownIcon className="w-5 h-5" />}
                </div>
                <span className={cn("text-xs font-semibold px-2 py-1 rounded-full", isIncome ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700")}>
                    {isIncome ? "+12% vs last month" : "-2% vs last month"}
                </span>
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-slate-800">
                    ₹{Math.abs(amount).toLocaleString()}
                </h3>
            </div>
        </div>
    );
}
