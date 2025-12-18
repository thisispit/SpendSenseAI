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
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-500">{title}</p>
                    <h3 className={cn("text-2xl font-bold mt-2", isIncome ? "text-green-600" : "text-red-600")}>
                        {isIncome ? "+" : "-"}₹{Math.abs(amount).toLocaleString()}
                    </h3>
                </div>
                <div className={cn("p-3 rounded-full", isIncome ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600")}>
                    {isIncome ? <ArrowUpIcon className="w-6 h-6" /> : <ArrowDownIcon className="w-6 h-6" />}
                </div>
            </div>
        </div>
    );
}
