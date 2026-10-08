import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { Token } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokenData = localStorage.getItem('baraka_tokens');
    if (tokenData) {
      try {
        const tokens: Token = JSON.parse(tokenData);
        if (tokens.access_token) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
      } catch {
        // Invalid token data, continue without auth
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const tokenData = localStorage.getItem('baraka_tokens');
        if (tokenData) {
          const tokens: Token = JSON.parse(tokenData);
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: tokens.refresh_token,
          });

          const newTokens = refreshResponse.data;
          localStorage.setItem('baraka_tokens', JSON.stringify(newTokens));

          originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
          return api(originalRequest);
        }
      } catch {
        // Refresh failed, logout
        localStorage.removeItem('baraka_tokens');
        localStorage.removeItem('baraka_user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  refresh: (data: { refresh_token: string }) =>
    api.post('/auth/refresh', data),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

// Markets API
export const marketsApi = {
  getMarkets: () => api.get('/markets'),
  getMarket: (symbol: string) => api.get(`/markets/${symbol}`),
  getCandles: (symbol: string, timeframe: string, limit: number = 100) =>
    api.get(`/markets/${symbol}/candles`, { params: { timeframe, limit } }),
};

// Signals API
export const signalsApi = {
  getSignals: (params?: { signal?: string; symbol?: string; strategy?: string; min_confidence?: number }) =>
    api.get('/signals', { params }),
  getSignal: (id: string) => api.get(`/signals/${id}`),
};

// Portfolio API
export const portfolioApi = {
  getPortfolio: () => api.get('/portfolio'),
  getPerformance: () => api.get('/portfolio/performance'),
};

// Risk API
export const riskApi = {
  getRiskConfig: () => api.get('/risk'),
  updateRiskConfig: (data: Record<string, number>) => api.put('/risk', data),
};

// Strategies API
export const strategiesApi = {
  getStrategies: () => api.get('/strategies'),
  getStrategy: (id: string) => api.get(`/strategies/${id}`),
  createStrategy: (data: Record<string, unknown>) => api.post('/strategies', data),
  updateStrategy: (id: string, data: Record<string, unknown>) => api.put(`/strategies/${id}`, data),
  deleteStrategy: (id: string) => api.delete(`/strategies/${id}`),
  enableStrategy: (id: string) => api.post(`/strategies/${id}/enable`),
  disableStrategy: (id: string) => api.post(`/strategies/${id}/disable`),
  backtestStrategy: (id: string, data: Record<string, unknown>) => api.post(`/strategies/${id}/backtest`, data),
};

// AI Models API
export const modelsApi = {
  getModels: () => api.get('/models'),
  getModel: (id: string) => api.get(`/models/${id}`),
  trainModel: (data: Record<string, unknown>) => api.post('/models/train', data),
  approveModel: (id: string) => api.post(`/models/${id}/approve`),
  retireModel: (id: string) => api.post(`/models/${id}/retire`),
  compareModels: (ids: string[]) => api.post('/models/compare', { model_ids: ids }),
};

// Orders API
export const ordersApi = {
  getOrders: () => api.get('/orders'),
  createOrder: (data: Record<string, unknown>) => api.post('/orders', data),
  cancelOrder: (id: string) => api.delete(`/orders/${id}`),
};

// Positions API
export const positionsApi = {
  getPositions: () => api.get('/positions'),
  closePosition: (id: string) => api.post(`/positions/${id}/close`),
};

// Trades API
export const tradesApi = {
  getTrades: (params?: Record<string, string>) => api.get('/trades', { params }),
};

// Backtests API
export const backtestsApi = {
  createBacktest: (data: Record<string, unknown>) => api.post('/backtests', data),
  getBacktest: (id: string) => api.get(`/backtests/${id}`),
  getBacktests: () => api.get('/backtests'),
};

// Paper Trading API
export const paperApi = {
  start: () => api.post('/paper/start'),
  stop: () => api.post('/paper/stop'),
  getStatus: () => api.get('/paper/status'),
};

// Kill Switch API
export const killSwitchApi = {
  activate: () => api.post('/kill-switch/activate'),
  deactivate: () => api.post('/kill-switch/deactivate'),
  getStatus: () => api.get('/kill-switch/status'),
};

// System API
export const systemApi = {
  getHealth: () => api.get('/system/health'),
  getAuditLogs: () => api.get('/system/audit-logs'),
};

// Alerts API
export const alertsApi = {
  getAlerts: () => api.get('/alerts'),
  markRead: (id: string) => api.post(`/alerts/${id}/read`),
  markAllRead: () => api.post('/alerts/read-all'),
};
