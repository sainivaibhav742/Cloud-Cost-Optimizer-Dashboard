'use client';

import { useEffect, useState } from 'react';
import { recommendationAPI, Recommendation } from '@/lib/api';

interface RecommendationGroup {
  idle_instances: Recommendation[];
  underused_rds: Recommendation[];
  cost_spikes: Recommendation[];
}

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<RecommendationGroup | null>(null);
  const [aiRecommendations, setAIRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAI, setShowAI] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const data = await recommendationAPI.getRecommendations();
      setRecommendations(data);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAIRecommendations = async () => {
    try {
      const data = await recommendationAPI.getAIRecommendations();
      setAIRecommendations(data.recommendations || []);
      setShowAI(true);
    } catch (error) {
      console.error('Failed to load AI recommendations:', error);
      alert('Failed to load AI recommendations. Make sure OpenAI API key is configured.');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  const totalRecommendations = recommendations 
    ? recommendations.idle_instances.length + recommendations.underused_rds.length + recommendations.cost_spikes.length
    : 0;

  const totalPotentialSavings = recommendations
    ? [
        ...recommendations.idle_instances,
        ...recommendations.underused_rds,
        ...recommendations.cost_spikes,
      ].reduce((sum, rec) => sum + (rec.potential_savings || 0), 0)
    : 0;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Cost Optimization Recommendations</h1>
        <button onClick={loadAIRecommendations} className="btn btn-primary">
          🤖 Get AI Recommendations
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-2">
        <div className="stat-card">
          <div className="stat-label">Total Recommendations</div>
          <div className="stat-value">{totalRecommendations}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Optimization opportunities found
          </div>
        </div>

        <div className="stat-card" style={{ borderLeftColor: 'var(--success-color)' }}>
          <div className="stat-label">Potential Savings</div>
          <div className="stat-value">${totalPotentialSavings.toFixed(2)}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Monthly estimated savings
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      {showAI && aiRecommendations.length > 0 && (
        <div className="card" style={{ marginTop: '2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <h2 style={{ marginBottom: '1rem', color: 'white' }}>🤖 AI-Powered Recommendations</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {aiRecommendations.map((rec, idx) => (
              <div key={idx} style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '6px' }}>
                <h4 style={{ marginBottom: '0.5rem', color: 'white' }}>{rec.title || `Recommendation ${idx + 1}`}</h4>
                <p style={{ color: 'rgba(255,255,255,0.9)' }}>{rec.description}</p>
                {rec.priority && (
                  <span className="badge badge-warning" style={{ marginTop: '0.5rem' }}>
                    Priority: {rec.priority}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Idle EC2 Instances */}
      {recommendations && recommendations.idle_instances.length > 0 && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            💤 Idle EC2 Instances
            <span className="badge badge-warning">{recommendations.idle_instances.length}</span>
          </h2>
          <table className="table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Date</th>
                <th>Usage</th>
                <th>Current Cost</th>
                <th>Potential Savings</th>
                <th>Suggestion</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.idle_instances.map((rec, idx) => (
                <tr key={idx}>
                  <td>{rec.service}</td>
                  <td>{rec.date}</td>
                  <td>{rec.usage?.toFixed(2)}%</td>
                  <td>${rec.cost?.toFixed(2)}</td>
                  <td>
                    <span style={{ color: 'var(--success-color)', fontWeight: 'bold' }}>
                      ${rec.potential_savings?.toFixed(2)}
                    </span>
                  </td>
                  <td>{rec.suggestion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Underused RDS */}
      {recommendations && recommendations.underused_rds.length > 0 && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📊 Underused RDS Databases
            <span className="badge badge-info">{recommendations.underused_rds.length}</span>
          </h2>
          <table className="table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Date</th>
                <th>Usage</th>
                <th>Current Cost</th>
                <th>Potential Savings</th>
                <th>Suggestion</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.underused_rds.map((rec, idx) => (
                <tr key={idx}>
                  <td>{rec.service}</td>
                  <td>{rec.date}</td>
                  <td>{rec.usage?.toFixed(2)}%</td>
                  <td>${rec.cost?.toFixed(2)}</td>
                  <td>
                    <span style={{ color: 'var(--success-color)', fontWeight: 'bold' }}>
                      ${rec.potential_savings?.toFixed(2)}
                    </span>
                  </td>
                  <td>{rec.suggestion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Cost Spikes */}
      {recommendations && recommendations.cost_spikes.length > 0 && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📈 Cost Spikes Detected
            <span className="badge badge-danger">{recommendations.cost_spikes.length}</span>
          </h2>
          <table className="table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Recent Cost</th>
                <th>Previous Cost</th>
                <th>Increase</th>
                <th>Suggestion</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.cost_spikes.map((rec: Recommendation & { recent_cost?: number; previous_cost?: number; increase_percent?: number }, idx: number) => (
                <tr key={idx}>
                  <td>{rec.service}</td>
                  <td>${rec.recent_cost?.toFixed(2)}</td>
                  <td>${rec.previous_cost?.toFixed(2)}</td>
                  <td>
                    <span className="badge badge-danger">
                      +{rec.increase_percent?.toFixed(1)}%
                    </span>
                  </td>
                  <td>{rec.suggestion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalRecommendations === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3 style={{ color: 'var(--success-color)', marginBottom: '1rem' }}>✅ Great job!</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            No cost optimization recommendations at this time. Your cloud infrastructure is well optimized!
          </p>
        </div>
      )}
    </div>
  );
}
