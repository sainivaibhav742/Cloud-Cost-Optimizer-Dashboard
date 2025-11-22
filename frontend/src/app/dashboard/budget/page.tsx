'use client';

import { useState } from 'react';
import { budgetAPI } from '@/lib/api';
import { Line } from 'react-chartjs-2';

interface SimulationResult {
  month: number;
  projected_cost: number;
  remaining_budget: number;
  budget_exceeded: boolean;
}

interface BudgetSimulation {
  budget_amount: number;
  average_monthly_spend: number;
  simulation: SimulationResult[];
  months_until_depletion: number | null;
}

export default function BudgetPage() {
  const [budgetAmount, setBudgetAmount] = useState(10000);
  const [months, setMonths] = useState(12);
  const [simulation, setSimulation] = useState<BudgetSimulation | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const data = await budgetAPI.simulate(budgetAmount, months);
      setSimulation(data);
    } catch (error) {
      console.error('Failed to simulate budget:', error);
      alert('Failed to simulate budget. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const chartData = simulation ? {
    labels: simulation.simulation.map(s => `Month ${s.month}`),
    datasets: [
      {
        label: 'Remaining Budget ($)',
        data: simulation.simulation.map(s => s.remaining_budget),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Projected Cost ($)',
        data: simulation.simulation.map(s => s.projected_cost),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  } : null;

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Budget Simulation</h1>

      {/* Simulation Form */}
      <div className="card">
        <h2 style={{ marginBottom: '1.5rem' }}>Simulate Budget Impact</h2>
        
        <div className="grid grid-2">
          <div className="form-group">
            <label htmlFor="budget">Total Budget ($)</label>
            <input
              type="number"
              id="budget"
              className="input"
              value={budgetAmount}
              onChange={(e) => setBudgetAmount(Number(e.target.value))}
              min="0"
              step="1000"
            />
          </div>

          <div className="form-group">
            <label htmlFor="months">Simulation Period (months)</label>
            <input
              type="number"
              id="months"
              className="input"
              value={months}
              onChange={(e) => setMonths(Number(e.target.value))}
              min="1"
              max="24"
            />
          </div>
        </div>

        <button onClick={handleSimulate} className="btn btn-primary" disabled={loading}>
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      {/* Simulation Results */}
      {simulation && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-3" style={{ marginTop: '2rem' }}>
            <div className="stat-card">
              <div className="stat-label">Budget Amount</div>
              <div className="stat-value">${simulation.budget_amount.toFixed(2)}</div>
            </div>

            <div className="stat-card" style={{ borderLeftColor: 'var(--warning-color)' }}>
              <div className="stat-label">Avg Monthly Spend</div>
              <div className="stat-value">${simulation.average_monthly_spend.toFixed(2)}</div>
            </div>

            <div className="stat-card" style={{ 
              borderLeftColor: simulation.months_until_depletion ? 'var(--danger-color)' : 'var(--success-color)' 
            }}>
              <div className="stat-label">Budget Status</div>
              <div className="stat-value">
                {simulation.months_until_depletion 
                  ? `${simulation.months_until_depletion} mo`
                  : '✓'
                }
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {simulation.months_until_depletion 
                  ? 'Until depletion'
                  : 'Budget sufficient'
                }
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="card" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Budget Projection</h3>
            {chartData && (
              <Line 
                data={chartData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    tooltip: {
                      callbacks: {
                        label: (context) => {
                          return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                        },
                      },
                    },
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

          {/* Detailed Table */}
          <div className="card" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Month-by-Month Breakdown</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Projected Cost</th>
                  <th>Remaining Budget</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {simulation.simulation.map((month) => (
                  <tr key={month.month}>
                    <td>Month {month.month}</td>
                    <td>${month.projected_cost.toFixed(2)}</td>
                    <td>${month.remaining_budget.toFixed(2)}</td>
                    <td>
                      {month.budget_exceeded ? (
                        <span className="badge badge-danger">Exceeded</span>
                      ) : month.remaining_budget < simulation.average_monthly_spend ? (
                        <span className="badge badge-warning">Low</span>
                      ) : (
                        <span className="badge badge-success">Good</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Recommendations */}
          {simulation.months_until_depletion && (
            <div className="card" style={{ 
              marginTop: '2rem', 
              background: '#fef3c7',
              borderLeft: '4px solid var(--warning-color)' 
            }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>⚠️ Budget Warning</h3>
              <p style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>
                Your budget will be depleted in {simulation.months_until_depletion} months at the current spending rate.
              </p>
              <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-primary)' }}>
                <li>Consider implementing cost optimization recommendations</li>
                <li>Review and right-size your resources</li>
                <li>Enable budget alerts for proactive monitoring</li>
                <li>Explore reserved instances or savings plans</li>
              </ul>
            </div>
          )}
        </>
      )}

      {!simulation && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>📊 Budget Simulation</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Enter your budget amount and simulation period above, then click "Run Simulation" to see projected spending.
          </p>
        </div>
      )}
    </div>
  );
}
