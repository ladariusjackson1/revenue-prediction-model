"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type CompanyPoint = { company: string; revenueBillions: number };
type IndustryPoint = { industry: string; revenueBillions: number };

const tooltipStyle = {
  background: "#0b1f2a",
  border: "none",
  borderRadius: 8,
  color: "#fff",
  fontSize: 12,
};

export function CompanyRevenueChart({ data }: { data: CompanyPoint[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 8, right: 16, left: 8, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(11,31,42,0.08)" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={(v) => `$${v}B`}
            tick={{ fill: "#3a5563", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="company"
            width={128}
            tick={{ fill: "#0b1f2a", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            cursor={{ fill: "rgba(13,138,106,0.08)" }}
            contentStyle={tooltipStyle}
            formatter={(value: number) => [`$${value.toFixed(1)}B`, "Revenue"]}
          />
          <Bar dataKey="revenueBillions" fill="#0d8a6a" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function IndustryRevenueChart({ data }: { data: IndustryPoint[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 56 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(11,31,42,0.08)" vertical={false} />
          <XAxis
            dataKey="industry"
            interval={0}
            angle={-35}
            textAnchor="end"
            height={70}
            tick={{ fill: "#3a5563", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v) => `$${v}B`}
            tick={{ fill: "#3a5563", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(31,111,139,0.08)" }}
            contentStyle={tooltipStyle}
            formatter={(value: number) => [`$${value.toFixed(1)}B`, "Revenue"]}
          />
          <Bar dataKey="revenueBillions" fill="#1f6f8b" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
