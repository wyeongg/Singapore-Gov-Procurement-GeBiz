'use client';

import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { formatCompactCurrency } from '../lib/format';
import styles from './SpendChart.module.css';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className={styles.tooltip}>
      <p className={styles.tooltipLabel}>{label}</p>
      {payload.map((entry) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.dataKey === 'total_awarded'
            ? `Spend: ${formatCompactCurrency(entry.value)}`
            : `Tenders: ${entry.value}`}
        </p>
      ))}
    </div>
  );
}

export default function SpendChart({ data, loading }) {
  if (loading) {
    return (
      <div className={styles.wrapper}>
        <h3>Spend Over Time</h3>
        <div className="skeleton" style={{ width: '100%', height: 300 }} />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={styles.wrapper}>
        <h3>Spend Over Time</h3>
        <p className={styles.empty}>No data for current filters</p>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <h3>Spend Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="period"
            tick={{ fontSize: 11, fill: '#86868b' }}
            tickLine={false}
            axisLine={{ stroke: '#d2d2d7' }}
          />
          <YAxis
            yAxisId="spend"
            tick={{ fontSize: 11, fill: '#86868b' }}
            tickFormatter={formatCompactCurrency}
            tickLine={false}
            axisLine={false}
            width={60}
          />
          <YAxis
            yAxisId="count"
            orientation="right"
            tick={{ fontSize: 11, fill: '#86868b' }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            yAxisId="spend"
            dataKey="total_awarded"
            fill="var(--color-chart-bar)"
            radius={[4, 4, 0, 0]}
            barSize={20}
          />
          <Line
            yAxisId="count"
            dataKey="num_tenders"
            stroke="var(--color-chart-line)"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
