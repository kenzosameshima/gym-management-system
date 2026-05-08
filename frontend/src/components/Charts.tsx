import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type React from "react";

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

function ChartCard({ title, children }: ChartCardProps): JSX.Element {
  return (
    <section className="chart-card">
      <h2>{title}</h2>
      <div className="chart-frame">{children}</div>
    </section>
  );
}

export function RevenueChart({ received, overdue, pending }: { received: number; overdue: number; pending: number }): JSX.Element {
  return (
    <ChartCard title="Revenue">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={[{ name: "Revenue", received, overdue, pending }]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="received" fill="#16a34a" />
          <Bar dataKey="overdue" fill="#dc2626" />
          <Bar dataKey="pending" fill="#f59e0b" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function DailyAccessChart({ data }: { data: { date: string; allowed: number; blocked: number }[] }): JSX.Element {
  return (
    <ChartCard title="Daily Access">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="allowed" fill="#2563eb" />
          <Bar dataKey="blocked" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function PlanUsageChart({ data }: { data: { name: string; enrollments: number }[] }): JSX.Element {
  return (
    <ChartCard title="Plan Usage">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="enrollments" fill="#7c3aed" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function WorkoutActivityChart({
  active,
  inactive,
  progress
}: {
  active: number;
  inactive: number;
  progress: number;
}): JSX.Element {
  return (
    <ChartCard title="Workout Activity">
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Tooltip />
          <Legend />
          <Pie
            data={[
              { name: "Active plans", value: active, fill: "#16a34a" },
              { name: "Inactive plans", value: inactive, fill: "#64748b" },
              { name: "Progress records", value: progress, fill: "#2563eb" }
            ]}
            dataKey="value"
            nameKey="name"
            outerRadius={80}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
