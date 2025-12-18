import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { Transaction } from "../data/mockData";

interface TrendChartProps {
    transactions: Transaction[];
}

export function TrendChart({ transactions }: TrendChartProps) {
    // Group by month (simplified for now, assuming all in same year or just showing raw date)
    // For a real app, we'd use date-fns or similar to group by month properly.
    // Here we'll just show the last 7 days for the demo as the mock data is recent.

    const data = transactions.reduce((acc, curr) => {
        const date = curr.date;
        const existing = acc.find((item) => item.date === date);

        if (existing) {
            if (curr.type === "CREDIT") {
                existing.income += curr.amount;
            } else {
                existing.expense += curr.amount;
            }
        } else {
            acc.push({
                date,
                income: curr.type === "CREDIT" ? curr.amount : 0,
                expense: curr.type === "DEBIT" ? curr.amount : 0,
            });
        }
        return acc;
    }, [] as { date: string; income: number; expense: number }[]).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-[400px]">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Trend</h3>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value: number | undefined) => `₹${(value || 0).toLocaleString()}`} />
                    <Legend />
                    <Bar dataKey="income" fill="#82ca9d" name="Income" />
                    <Bar dataKey="expense" fill="#ff8042" name="Expense" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
