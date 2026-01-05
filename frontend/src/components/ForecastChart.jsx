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
  if (!data || !data.history || !data.forecast) {
    return (
      <div style={{ 
        padding: '40px 20px', 
        textAlign: 'center', 
        color: '#94a3b8',
        fontSize: '1.1rem',
        fontFamily: 'Space Grotesk, sans-serif'
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
        day: 'numeric',
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
        day: 'numeric',
        year: 'numeric'
      }),
      date: point.week_start,
      Historical: null,
      Forecast: point.value,
      Baseline: showBaseline ? point.value * 0.9 : null // Simple baseline visualization
    }))
  ];

  // Find the split point between history and forecast
  const splitIndex = data.history.length;

  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(56, 248, 255, 0.08)" opacity={0.6} />
        <XAxis
          dataKey="week_start"
          angle={-45}
          textAnchor="end"
          height={100}
          interval="preserveStartEnd"
          stroke="var(--text-secondary)"
          style={{ fontSize: '12px', fontFamily: 'JetBrains Mono, monospace' }}
        />
        <YAxis
          label={{ value: 'Job Postings Count', angle: -90, position: 'insideLeft', style: { fill: 'var(--text-secondary)', fontSize: '14px', fontFamily: 'JetBrains Mono, monospace' } }}
          stroke="var(--text-secondary)"
          style={{ fontSize: '12px', fontFamily: 'JetBrains Mono, monospace' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(9, 14, 26, 0.95)',
            border: '1px solid rgba(56, 248, 255, 0.2)',
            borderRadius: '8px',
            color: '#e2e8f0',
            padding: '10px',
            fontFamily: 'JetBrains Mono, monospace'
          }}
          formatter={(value, name) => {
            if (value === null) return '';
            return [Math.round(value * 100) / 100, name];
          }}
          labelFormatter={(label) => `Week: ${label}`}
          labelStyle={{ color: 'var(--accent-primary)', fontWeight: 600 }}
        />
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="line"
          iconSize={16}
        />
        
        {/* Vertical line to separate history and forecast */}
        <Line
          type="monotone"
          dataKey="Historical"
          stroke="var(--accent-primary)"
          strokeWidth={3}
          dot={false}
          activeDot={{ r: 6, fill: 'var(--accent-primary)', stroke: '#070b14', strokeWidth: 2 }}
          connectNulls={false}
        />
        
        <Line
          type="monotone"
          dataKey="Forecast"
          stroke="var(--accent-secondary)"
          strokeWidth={3}
          strokeDasharray="8 4"
          dot={{ r: 5, fill: 'var(--accent-secondary)', stroke: '#070b14', strokeWidth: 2 }}
          activeDot={{ r: 7, fill: 'var(--accent-secondary)', stroke: '#070b14', strokeWidth: 2 }}
          connectNulls={false}
        />
        
        {showBaseline && (
          <Line
            type="monotone"
            dataKey="Baseline"
            stroke="var(--accent-tertiary)"
            strokeWidth={2.5}
            strokeDasharray="6 3"
            dot={false}
            connectNulls={false}
            opacity={0.8}
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
            <circle cx="5" cy="5" r="3" fill="#94a3b8" />
          </marker>
        </defs>
      </LineChart>
    </ResponsiveContainer>
  );
}
