import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement, Filler } from 'chart.js';
import Auth from '../components/Auth';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement, Filler);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
   const [costs, setCosts] = useState([]);
   const [recommendations, setRecommendations] = useState([]);
   const [budgets, setBudgets] = useState([]);
   const [alerts, setAlerts] = useState([]);
   const [forecasts, setForecasts] = useState([]);
   const [loading, setLoading] = useState(true);
   const [error, setError] = useState(null);
   const [token, setToken] = useState('');
   const [isClient, setIsClient] = useState(false);
   const [selectedProvider, setSelectedProvider] = useState(null);
   const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    setIsClient(true);
    // Check for token in localStorage on client side
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
      } else {
        // Auto-login with test credentials for demo purposes
        autoLogin();
      }
    }
    setLoading(false);
  }, []);

  const autoLogin = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/token`, new URLSearchParams({
        username: 'testuser',
        password: 'testpass',
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
    } catch (error) {
      console.error('Auto-login failed:', error);
      // If auto-login fails, user will need to login manually
    }
  };

  const fetchData = useCallback(async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const headers = { Authorization: `Bearer ${token}` };
      const params = selectedProvider ? { provider: selectedProvider } : {};

      const requests = [
        axios.get(`${API_BASE_URL}/costs/daily`, { headers, params }),
        axios.get(`${API_BASE_URL}/recommendations`, { headers, params }),
        axios.get(`${API_BASE_URL}/budgets`, { headers, params }).catch(() => ({ data: [] })),
        axios.get(`${API_BASE_URL}/alerts`, { headers, params }).catch(() => ({ data: [] })),
        axios.get(`${API_BASE_URL}/forecast`, { headers, params }).catch(() => ({ data: [] }))
      ];

      // Suppress 404 console errors for missing data endpoints
      const originalError = console.error;
      console.error = (...args) => {
        if (args[0] && typeof args[0] === 'string' && args[0].includes('404')) {
          return; // Suppress 404 errors
        }
        originalError.apply(console, args);
      };

      const [costsResponse, recommendationsResponse, budgetsResponse, alertsResponse, forecastsResponse] = await Promise.all(requests);

      setCosts(costsResponse.data);
      setRecommendations(recommendationsResponse.data);
      setBudgets(budgetsResponse.data);
      setAlerts(alertsResponse.data);
      setForecasts(forecastsResponse.data);
    } catch (err) {
      if (err.response?.status === 401) {
        // Token is invalid, clear it and show login
        localStorage.removeItem('token');
        setToken('');
      } else {
        setError(`Failed to fetch data from backend: ${err.response?.data?.detail || err.message}`);
      }
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  }, [token, selectedProvider]);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token, fetchData]);

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const costChartData = {
    labels: [...new Set(costs.map(item => item.date))].sort(),
    datasets: [{
      label: 'Daily Costs',
      data: [...new Set(costs.map(item => item.date))].sort().map(date =>
        costs.filter(item => item.date === date).reduce((sum, item) => sum + item.cost, 0)
      ),
      borderColor: selectedProvider === 'aws' ? '#ff9900' :
                   selectedProvider === 'azure' ? '#0078d4' :
                   selectedProvider === 'gcp' ? '#4285f4' : 'rgb(75, 192, 192)',
      backgroundColor: selectedProvider === 'aws' ? 'rgba(255, 153, 0, 0.1)' :
                       selectedProvider === 'azure' ? 'rgba(0, 120, 212, 0.1)' :
                       selectedProvider === 'gcp' ? 'rgba(66, 133, 244, 0.1)' : 'rgba(75, 192, 192, 0.1)',
      tension: 0.1,
      fill: true
    }]
  };

  const serviceBreakdownData = {
    labels: [...new Set(costs.map(item => item.service))],
    datasets: [{
      label: 'Cost by Service',
      data: [...new Set(costs.map(item => item.service))].map(service =>
        costs.filter(item => item.service === service).reduce((sum, item) => sum + item.cost, 0)
      ),
      backgroundColor: [
        '#ff9900', '#0078d4', '#4285f4', '#ea4335', '#34a853',
        '#fbbc04', '#9c27b0', '#3f51b5', '#009688', '#ff5722'
      ].slice(0, [...new Set(costs.map(item => item.service))].length),
    }]
  };

  const providerDistributionData = {
    labels: ['AWS', 'Azure', 'GCP'],
    datasets: [{
      data: ['aws', 'azure', 'gcp'].map(provider =>
        costs.filter(item => item.provider === provider).reduce((sum, item) => sum + item.cost, 0)
      ),
      backgroundColor: ['#ff9900', '#0078d4', '#4285f4'],
      borderWidth: 2,
    }]
  };

  const forecastChartData = {
    labels: [...new Set(forecasts.map(item => item.forecast_date))].sort(),
    datasets: [{
      label: 'Predicted Cost',
      data: [...new Set(forecasts.map(item => item.forecast_date))].sort().map(date =>
        forecasts.filter(item => item.forecast_date === date).reduce((sum, item) => sum + item.predicted_cost, 0)
      ),
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      tension: 0.1,
      fill: true
    }]
  };

  if (!isClient) {
    return <div className="loading">Loading...</div>;
  }

  if (!token) {
    return <Auth onLogin={handleLogin} />;
  }

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  const handleProviderChange = (provider) => {
    setSelectedProvider(provider);
  };

  const markAlertRead = async (alertId) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.put(`${API_BASE_URL}/alerts/${alertId}/read`, {}, { headers });
      // Refresh alerts
      const alertsResponse = await axios.get(`${API_BASE_URL}/alerts`, { headers, params: selectedProvider ? { provider: selectedProvider } : {} });
      setAlerts(alertsResponse.data);
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const renderTabContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Spend</h3>
                <div className="value">${costs.reduce((sum, item) => sum + item.cost, 0).toFixed(2)}</div>
                <div className="subtitle">
                  {selectedProvider ? `${selectedProvider.toUpperCase()} Provider` : 'All Providers'}
                </div>
              </div>
              <div className="stat-card">
                <h3>Active Services</h3>
                <div className="value">{[...new Set(costs.map(item => item.service))].length}</div>
                <div className="subtitle">Services being monitored</div>
              </div>
              <div className="stat-card">
                <h3>Cost Efficiency</h3>
                <div className="value">
                  {recommendations.idle_instances?.length + recommendations.underused_rds?.length || 0}
                </div>
                <div className="subtitle">Optimization opportunities</div>
              </div>
            </div>

            <div className="charts-grid">
              <div className="chart-card">
                <h3>Cost Trend Over Time</h3>
                <Line data={costChartData} />
              </div>
              <div className="chart-card">
                <h3>Cost by Service</h3>
                <Bar data={serviceBreakdownData} />
              </div>
            </div>

            <div className="recommendations-card">
              <h3>💡 Cost Optimization Recommendations</h3>
              {recommendations.idle_instances?.length > 0 && (
                <div>
                  <h4>🚀 Idle Instances</h4>
                  {recommendations.idle_instances.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <h4>{rec.provider?.toUpperCase()} Instance</h4>
                      <p>{rec.suggestion}</p>
                      <div className="savings">Potential savings: ${rec.potential_savings?.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              )}
              {recommendations.underused_rds?.length > 0 && (
                <div>
                  <h4>💾 Underused Databases</h4>
                  {recommendations.underused_rds.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <h4>{rec.provider?.toUpperCase()} Database</h4>
                      <p>{rec.suggestion}</p>
                      <div className="savings">Potential savings: ${rec.potential_savings?.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              )}
              {recommendations.cost_spikes?.length > 0 && (
                <div>
                  <h4>📈 Cost Anomalies</h4>
                  {recommendations.cost_spikes.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <h4>{rec.service}</h4>
                      <p>{rec.suggestion}</p>
                      <div className="savings">Increase: {rec.increase_percent?.toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              )}
              {(!recommendations.idle_instances?.length && !recommendations.underused_rds?.length && !recommendations.cost_spikes?.length) && (
                <div className="recommendation-item" style={{borderLeftColor: '#38a169', background: '#f0fff4'}}>
                  <h4>✅ All Clear</h4>
                  <p>Your cloud infrastructure is running efficiently. No optimization opportunities detected.</p>
                </div>
              )}
            </div>
          </>
        );
      case 'budgets':
        return (
          <div className="stat-card">
            <h3>💰 Budget Management</h3>
            <div style={{textAlign: 'center', padding: '3rem'}}>
              <p style={{color: '#718096', fontSize: '1.1rem'}}>
                Budget management features coming soon. This will allow you to set spending limits and receive alerts when approaching thresholds.
              </p>
            </div>
          </div>
        );
      case 'alerts':
        return (
          <div className="stat-card">
            <h3>🚨 Alerts & Notifications</h3>
            <div style={{textAlign: 'center', padding: '3rem'}}>
              <p style={{color: '#718096', fontSize: '1.1rem'}}>
                Alert system coming soon. You'll receive notifications about cost anomalies, budget thresholds, and optimization opportunities.
              </p>
            </div>
          </div>
        );
      case 'forecast':
        return (
          <div className="stat-card">
            <h3>🔮 Cost Forecasting</h3>
            <div style={{textAlign: 'center', padding: '3rem'}}>
              <p style={{color: '#718096', fontSize: '1.1rem'}}>
                Forecasting features coming soon. Predict future cloud spending based on historical trends and usage patterns.
              </p>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>☁️ Cloud Cost Optimizer</h1>
        <button className="logout-btn" onClick={() => {
          localStorage.removeItem('token');
          setToken('');
        }}>
          Logout
        </button>
      </header>

      <nav className="nav-tabs">
        <div className="tabs">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={activeTab === 'budgets' ? 'active' : ''}
            onClick={() => setActiveTab('budgets')}
          >
            💰 Budgets
          </button>
          <button
            className={activeTab === 'alerts' ? 'active' : ''}
            onClick={() => setActiveTab('alerts')}
          >
            🚨 Alerts {alerts.length > 0 && `(${alerts.filter(a => !a.is_read).length})`}
          </button>
          <button
            className={activeTab === 'forecast' ? 'active' : ''}
            onClick={() => setActiveTab('forecast')}
          >
            🔮 Forecast
          </button>
        </div>
      </nav>

      <main className="dashboard">
        <div className="provider-selector">
          <button
            className={`provider-btn ${!selectedProvider ? 'active' : ''}`}
            onClick={() => handleProviderChange(null)}
          >
            🌐 All Providers
          </button>
          <button
            className={`provider-btn aws ${selectedProvider === 'aws' ? 'active' : ''}`}
            onClick={() => handleProviderChange('aws')}
          >
            🟠 AWS
          </button>
          <button
            className={`provider-btn azure ${selectedProvider === 'azure' ? 'active' : ''}`}
            onClick={() => handleProviderChange('azure')}
          >
            🔵 Azure
          </button>
          <button
            className={`provider-btn gcp ${selectedProvider === 'gcp' ? 'active' : ''}`}
            onClick={() => handleProviderChange('gcp')}
          >
            🔴 GCP
          </button>
        </div>

        {renderTabContent()}
      </main>
    </div>
  );
}