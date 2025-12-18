import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { Transaction } from "../data/mockData";

interface TrendChartProps {
    transactions: Transaction[];
}

export function TrendChart({ transactions }: TrendChartProps) {
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
    }, [] as { date: string; income: number; expense: number }[])
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        .slice(-7); // Last 7 days

    return (
        <div className="w-full h-[300px]">
            {data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} barSize={20}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis
                            dataKey="date"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#64748b', fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#64748b', fontSize: 12 }}
                            tickFormatter={(value) => `₹${value}`}
                        />
                        <Tooltip
                            cursor={{ fill: '#f1f5f9' }}
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            formatter={(value: number) => [`₹${value.toLocaleString()}`, undefined]}
                        />
                        <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                        <Bar name="Income" dataKey="income" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar name="Expenses" dataKey="expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            ) : (
                <div className="flex items-center justify-center h-full text-slate-400 text-sm italic">
                    No transaction data available
                </div>
            )}
        </div>
    );
}
