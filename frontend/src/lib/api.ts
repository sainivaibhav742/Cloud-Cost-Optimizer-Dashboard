import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        // Use window.location.replace to avoid adding to history
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface CostData {
  id: number;
  date: string;
  service: string;
  cost: number;
  usage: number;
  account_id: string;
}

export interface CostSummary {
  total_cost: number;
  daily_average: number;
  service_breakdown: Record<string, number>;
  period_days: number;
  total_records: number;
}

export interface Recommendation {
  type: string;
  service?: string;
  date?: string;
  cost?: number;
  usage?: number;
  suggestion: string;
  potential_savings?: number;
  title?: string;
  description?: string;
  priority?: string;
}

export interface SystemHealth {
  database_healthy: boolean;
  total_cost_records: number;
  recent_costs_7d: number;
  avg_daily_cost_7d: number;
  timestamp: string;
}

// Auth APIs
export const authAPI = {
  login: async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
};

// Cost APIs
export const costAPI = {
  getDailyCosts: async (): Promise<CostData[]> => {
    const response = await api.get('/costs/daily');
    return response.data;
  },
  
  getSummary: async (days: number = 30): Promise<CostSummary> => {
    const response = await api.get(`/costs/summary?days=${days}`);
    return response.data;
  },
  
  fetchCosts: async () => {
    const response = await api.post('/costs/fetch');
    return response.data;
  },
};

// Recommendation APIs
export const recommendationAPI = {
  getRecommendations: async () => {
    const response = await api.get('/recommendations');
    return response.data;
  },
  
  getAIRecommendations: async () => {
    const response = await api.get('/ai-recommendations');
    return response.data;
  },
};

// Budget APIs
export const budgetAPI = {
  simulate: async (budgetAmount: number, months: number = 12) => {
    const response = await api.post(`/budget/simulate?budget_amount=${budgetAmount}&months=${months}`);
    return response.data;
  },
};

// Monitoring APIs
export const monitoringAPI = {
  getHealth: async (): Promise<SystemHealth> => {
    const response = await api.get('/monitoring/health');
    return response.data;
  },
  
  getPerformance: async () => {
    const response = await api.get('/monitoring/performance');
    return response.data;
  },
  
  getSavings: async (days: number = 30) => {
    const response = await api.get(`/monitoring/savings?days=${days}`);
    return response.data;
  },
};

// Demo API
export const demoAPI = {
  seedData: async () => {
    const response = await api.post('/demo/seed');
    return response.data;
  },
};

export default api;
