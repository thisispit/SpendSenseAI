import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { Transaction } from "../types/transaction";

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export function CategoryChart({ transactions }: { transactions: Transaction[] }) {
    // Extract unique categories from transactions
    const categories = Array.from(new Set(transactions.map(t => t.category)));

    const data = categories.map(cat => ({
        name: cat,
        value: transactions
            .filter(t => t.category === cat && t.type === 'DEBIT')
            .reduce((acc, curr) => acc + curr.amount, 0)
    })).filter(d => d.value > 0);

    return (
        <div className="w-full h-[300px] flex items-center justify-center">
            {data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            fill="#8884d8"
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="transparent" />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            itemStyle={{ color: '#1e293b', fontWeight: 600 }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            ) : (
                <div className="text-slate-400 text-sm italic">No expense data available</div>
            )}
        </div>
    );
}
