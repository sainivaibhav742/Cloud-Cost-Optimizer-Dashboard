'use client';

import { useEffect, useState } from 'react';
import { costAPI, monitoringAPI, CostSummary, SystemHealth } from '@/lib/api';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export default function DashboardPage() {
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    loadData();
  }, [period]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryData, healthData] = await Promise.all([
        costAPI.getSummary(period),
        monitoringAPI.getHealth(),
      ]);
      setSummary(summaryData);
      setHealth(healthData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  const serviceBreakdownData = summary ? {
    labels: Object.keys(summary.service_breakdown),
    datasets: [{
      label: 'Cost by Service ($)',
      data: Object.values(summary.service_breakdown),
      backgroundColor: [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16',
      ],
    }],
  } : null;

  const barChartData = summary ? {
    labels: Object.keys(summary.service_breakdown),
    datasets: [{
      label: 'Cost ($)',
      data: Object.values(summary.service_breakdown),
      backgroundColor: '#3b82f6',
    }],
  } : null;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Cost Dashboard</h1>
        <div>
          <label style={{ marginRight: '0.5rem', color: 'var(--text-secondary)' }}>Period:</label>
          <select 
            value={period} 
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="input"
            style={{ width: 'auto', display: 'inline-block' }}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={60}>Last 60 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-3">
        <div className="stat-card">
          <div className="stat-label">Total Cost</div>
          <div className="stat-value">${summary?.total_cost.toFixed(2)}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Last {period} days
          </div>
        </div>

        <div className="stat-card" style={{ borderLeftColor: 'var(--success-color)' }}>
          <div className="stat-label">Daily Average</div>
          <div className="stat-value">${summary?.daily_average.toFixed(2)}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Per day
          </div>
        </div>

        <div className="stat-card" style={{ borderLeftColor: 'var(--warning-color)' }}>
          <div className="stat-label">Records</div>
          <div className="stat-value">{summary?.total_records}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Cost entries
          </div>
        </div>
      </div>

      {/* System Health */}
      {health && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>System Health</h3>
          <div className="grid grid-3">
            <div>
              <span className={`badge ${health.database_healthy ? 'badge-success' : 'badge-danger'}`}>
                {health.database_healthy ? 'Healthy' : 'Unhealthy'}
              </span>
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Database Status
              </div>
            </div>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
                ${health.recent_costs_7d.toFixed(2)}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Last 7 days cost
              </div>
            </div>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
                ${health.avg_daily_cost_7d.toFixed(2)}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Avg daily cost (7d)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-2" style={{ marginTop: '2rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Cost Distribution</h3>
          {serviceBreakdownData && (
            <div style={{ maxWidth: '400px', margin: '0 auto' }}>
              <Pie data={serviceBreakdownData} />
            </div>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Cost by Service</h3>
          {barChartData && (
            <Bar 
              data={barChartData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: (value) => '$' + value,
                    },
                  },
                },
              }}
            />
          )}
        </div>
      </div>

      {/* Service Breakdown Table */}
      <div className="card" style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Service Breakdown</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Cost</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {summary && Object.entries(summary.service_breakdown).map(([service, cost]) => (
              <tr key={service}>
                <td>{service}</td>
                <td>${cost.toFixed(2)}</td>
                <td>{((cost / summary.total_cost) * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
