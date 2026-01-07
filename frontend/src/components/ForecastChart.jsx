import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * Chart component for displaying historical data and forecasts.
 */
export default function ForecastChart({ data, showBaseline = false }) {
  const countFormatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });

  if (!data || !data.history || !data.forecast) {
    return (
      <div style={{ 
        padding: '40px 20px', 
        textAlign: 'center', 
        color: 'var(--text-secondary)',
        fontSize: '1.1rem',
        fontFamily: 'Chakra Petch, sans-serif'
      }}>
        No data to display
      </div>
    );
  }

  // Combine history and forecast for display
  const chartData = [
    ...data.history.map(point => ({
      week_start: new Date(point.week_start).toLocaleDateString('en-US', {
        month: 'short',
        year: 'numeric'
      }),
      date: point.week_start,
      Historical: point.value,
      Forecast: null,
      Baseline: null
    })),
    ...data.forecast.map(point => ({
      week_start: new Date(point.week_start).toLocaleDateString('en-US', {
        month: 'short',
        year: 'numeric'
      }),
      date: point.week_start,
      Historical: null,
      Forecast: point.value,
      Baseline: showBaseline ? point.value * 0.9 : null // Simple baseline visualization
    }))
  ];

  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(233, 23, 55, 0.12)" opacity={0.6} />
        <XAxis
          dataKey="week_start"
          angle={0}
          textAnchor="middle"
          height={50}
          interval="preserveStartEnd"
          stroke="var(--text-secondary)"
          style={{ fontSize: '12px', fontFamily: 'JetBrains Mono, monospace' }}
        />
        <YAxis
          label={{ value: 'Monthly postings', angle: -90, position: 'insideLeft', style: { fill: 'var(--text-secondary)', fontSize: '14px', fontFamily: 'JetBrains Mono, monospace' } }}
          stroke="var(--text-secondary)"
          style={{ fontSize: '12px', fontFamily: 'JetBrains Mono, monospace' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(233, 23, 55, 0.25)',
            borderRadius: '8px',
            color: '#1f0d0f',
            padding: '10px',
            fontFamily: 'JetBrains Mono, monospace'
          }}
          formatter={(value, name) => {
            if (value === null) return '';
            return [countFormatter.format(Math.round(value)), name];
          }}
          labelFormatter={(label) => `Month: ${label}`}
          labelStyle={{ color: 'var(--accent-primary)', fontWeight: 600 }}
        />
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="line"
          iconSize={16}
        />
        
        {data.history.length > 0 && (
          <Line
            type="monotone"
            dataKey="Historical"
            stroke="var(--text-primary)"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: 'var(--text-primary)', stroke: '#ffffff', strokeWidth: 2 }}
            connectNulls={false}
            name="Actual jobs"
          />
        )}
        
        <Line
          type="monotone"
          dataKey="Forecast"
          stroke="var(--accent-primary)"
          strokeWidth={3}
          strokeDasharray="8 4"
          dot={{ r: 5, fill: 'var(--accent-primary)', stroke: '#ffffff', strokeWidth: 2 }}
          activeDot={{ r: 7, fill: 'var(--accent-primary)', stroke: '#ffffff', strokeWidth: 2 }}
          connectNulls={false}
          name="Forecast jobs"
        />
        
        {showBaseline && (
          <Line
            type="monotone"
            dataKey="Baseline"
            stroke="var(--text-muted)"
            strokeWidth={2.5}
            strokeDasharray="6 3"
            dot={false}
            connectNulls={false}
            opacity={0.8}
            name="Baseline"
          />
        )}
        
        {/* Annotation for split point */}
        <defs>
          <marker
            id="split"
            viewBox="0 0 10 10"
            refX="5"
            refY="5"
            markerWidth="6"
            markerHeight="6"
          >
            <circle cx="5" cy="5" r="3" fill="var(--text-muted)" />
          </marker>
        </defs>
      </LineChart>
    </ResponsiveContainer>
  );
}
