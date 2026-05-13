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

const CHART_COLORS = {
  primary: "#2563EB",
  danger: "#DC2626",
  success: "#16A34A",
  warning: "#D97706",
  neutral: "#64748B",
  grid: "#E2E8F0"
};

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
    <ChartCard title="Recebimentos">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={[{ name: "Mensalidades", received, overdue, pending }]}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="received" fill={CHART_COLORS.success} />
          <Bar dataKey="overdue" fill={CHART_COLORS.danger} />
          <Bar dataKey="pending" fill={CHART_COLORS.warning} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function DailyAccessChart({ data }: { data: { date: string; allowed: number; blocked: number }[] }): JSX.Element {
  return (
    <ChartCard title="Acessos por dia">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="allowed" fill={CHART_COLORS.success} />
          <Bar dataKey="blocked" fill={CHART_COLORS.danger} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function PlanUsageChart({ data }: { data: { name: string; enrollments: number }[] }): JSX.Element {
  return (
    <ChartCard title="Planos mais usados">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="enrollments" fill={CHART_COLORS.primary} />
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
    <ChartCard title="Treinos">
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Tooltip />
          <Legend />
          <Pie
            data={[
              { name: "Fichas ativas", value: active, fill: CHART_COLORS.success },
              { name: "Fichas inativas", value: inactive, fill: CHART_COLORS.neutral },
              { name: "Evolucoes", value: progress, fill: CHART_COLORS.primary }
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
