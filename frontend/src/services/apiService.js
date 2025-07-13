import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('gpuoptimizer_api_key');
    if (apiKey) {
      config.headers.Authorization = `Bearer ${apiKey}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth data
      localStorage.removeItem('gpuoptimizer_api_key');
      localStorage.removeItem('gpuoptimizer_user');
      window.location.href = '/login';
    }
    
    return Promise.reject(error.response?.data || error.message);
  }
);

export const apiService = {
  // Authentication
  signup: async (email) => {
    return await api.post('/signup', { email });
  },

  verifyApiKey: async (apiKey) => {
    try {
      const response = await api.get('/verify', {
        headers: { Authorization: `Bearer ${apiKey}` }
      });
      return { valid: true, data: response };
    } catch (error) {
      return { valid: false, error };
    }
  },

  // GPU Tracking
  trackGpuUsage: async (apiKey, gpuData) => {
    return await api.post('/track-usage', {
      api_key: apiKey,
      gpu_data: gpuData
    });
  },

  // Account Management
  upgradeAccount: async (email, tier, paymentMethod) => {
    return await api.post('/upgrade', {
      customer_email: email,
      tier,
      payment_method: paymentMethod
    });
  },

  // Analytics
  getStats: async () => {
    return await api.get('/stats');
  },

  getUserAnalytics: async (apiKey, timeRange = '7d') => {
    return await api.get(`/analytics?api_key=${apiKey}&range=${timeRange}`);
  },

  // Payment Webhooks (for frontend confirmation)
  confirmPayment: async (paymentId, gateway) => {
    return await api.post('/payment/confirm', {
      payment_id: paymentId,
      gateway
    });
  },

  // Lead Generation
  submitLead: async (leadData) => {
    return await api.post('/leads/submit', leadData);
  },

  subscribeNewsletter: async (email) => {
    return await api.post('/newsletter/subscribe', { email });
  },

  // Contact
  submitContact: async (contactData) => {
    return await api.post('/contact', contactData);
  },

  // Pricing
  getPricing: async () => {
    return await api.get('/pricing');
  },

  // Real-time data (if WebSocket is not available)
  getRealtimeData: async (apiKey) => {
    return await api.get(`/realtime?api_key=${apiKey}`);
  },

  // System Health
  getHealth: async () => {
    return await api.get('/health');
  },

  // User Profile
  updateProfile: async (profileData) => {
    return await api.put('/profile', profileData);
  },

  getProfile: async (apiKey) => {
    return await api.get(`/profile?api_key=${apiKey}`);
  },

  // Billing
  getBillingHistory: async (apiKey) => {
    return await api.get(`/billing/history?api_key=${apiKey}`);
  },

  downloadInvoice: async (invoiceId) => {
    return await api.get(`/billing/invoice/${invoiceId}`, {
      responseType: 'blob'
    });
  },

  // API Keys Management
  regenerateApiKey: async (currentApiKey) => {
    return await api.post('/api-key/regenerate', {
      current_api_key: currentApiKey
    });
  },

  // Usage Reports
  getUsageReport: async (apiKey, startDate, endDate) => {
    return await api.get(`/reports/usage?api_key=${apiKey}&start=${startDate}&end=${endDate}`);
  },

  exportUsageData: async (apiKey, format = 'csv') => {
    return await api.get(`/export/usage?api_key=${apiKey}&format=${format}`, {
      responseType: 'blob'
    });
  },

  // Notifications
  getNotifications: async (apiKey) => {
    return await api.get(`/notifications?api_key=${apiKey}`);
  },

  markNotificationRead: async (notificationId) => {
    return await api.put(`/notifications/${notificationId}/read`);
  },

  // Settings
  updateSettings: async (apiKey, settings) => {
    return await api.put('/settings', {
      api_key: apiKey,
      settings
    });
  },

  getSettings: async (apiKey) => {
    return await api.get(`/settings?api_key=${apiKey}`);
  },

  // Integrations
  getIntegrations: async () => {
    return await api.get('/integrations');
  },

  setupIntegration: async (apiKey, integrationType, config) => {
    return await api.post('/integrations/setup', {
      api_key: apiKey,
      type: integrationType,
      config
    });
  },

  // Support
  submitTicket: async (ticketData) => {
    return await api.post('/support/ticket', ticketData);
  },

  getTickets: async (apiKey) => {
    return await api.get(`/support/tickets?api_key=${apiKey}`);
  },
};

// WebSocket service for real-time updates
export class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(apiKey) {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:5000/ws';
    this.ws = new WebSocket(`${wsUrl}?api_key=${apiKey}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notifyListeners(data.type, data.payload);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(apiKey);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  attemptReconnect(apiKey) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect(apiKey);
      }, 1000 * this.reconnectAttempts);
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  unsubscribe(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  notifyListeners(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket listener:', error);
        }
      });
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

export const wsService = new WebSocketService();
