import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiKey, setApiKey] = useState(null);

  useEffect(() => {
    // Check for stored auth data on app load
    const storedApiKey = localStorage.getItem('gpuoptimizer_api_key');
    const storedUser = localStorage.getItem('gpuoptimizer_user');
    
    if (storedApiKey && storedUser) {
      try {
        setApiKey(storedApiKey);
        setUser(JSON.parse(storedUser));
        // Verify the API key is still valid
        verifyApiKey(storedApiKey);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        logout();
      }
    }
    
    setLoading(false);
  }, []);

  const verifyApiKey = async (key) => {
    try {
      const response = await apiService.verifyApiKey(key);
      if (!response.valid) {
        logout();
        toast.error('Session expired. Please log in again.');
      }
    } catch (error) {
      console.error('API key verification failed:', error);
      logout();
    }
  };

  const signup = async (email) => {
    try {
      setLoading(true);
      const response = await apiService.signup(email);
      
      if (response.status === 'success') {
        const userData = {
          email,
          tier: 'free',
          createdAt: new Date().toISOString(),
        };
        
        setUser(userData);
        setApiKey(response.api_key);
        
        // Store in localStorage
        localStorage.setItem('gpuoptimizer_api_key', response.api_key);
        localStorage.setItem('gpuoptimizer_user', JSON.stringify(userData));
        
        toast.success('Account created successfully!');
        return { success: true, data: response };
      } else {
        toast.error(response.message || 'Signup failed');
        return { success: false, error: response.message };
      }
    } catch (error) {
      console.error('Signup error:', error);
      toast.error('Signup failed. Please try again.');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, apiKeyInput) => {
    try {
      setLoading(true);
      
      // If API key is provided, use it directly
      if (apiKeyInput) {
        const isValid = await verifyApiKey(apiKeyInput);
        if (isValid) {
          const userData = {
            email,
            tier: 'unknown', // Will be fetched from backend
            createdAt: new Date().toISOString(),
          };
          
          setUser(userData);
          setApiKey(apiKeyInput);
          
          localStorage.setItem('gpuoptimizer_api_key', apiKeyInput);
          localStorage.setItem('gpuoptimizer_user', JSON.stringify(userData));
          
          toast.success('Logged in successfully!');
          return { success: true };
        } else {
          toast.error('Invalid API key');
          return { success: false, error: 'Invalid API key' };
        }
      }
      
      // Otherwise, try to find user by email (if implemented)
      toast.error('Please provide your API key to log in');
      return { success: false, error: 'API key required' };
      
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Login failed. Please try again.');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setApiKey(null);
    localStorage.removeItem('gpuoptimizer_api_key');
    localStorage.removeItem('gpuoptimizer_user');
    toast.success('Logged out successfully');
  };

  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('gpuoptimizer_user', JSON.stringify(updatedUser));
  };

  const upgradeAccount = async (tier, paymentMethod = 'flutterwave') => {
    try {
      setLoading(true);
      const response = await apiService.upgradeAccount(user.email, tier, paymentMethod);
      
      if (response.status === 'success') {
        updateUser({ tier });
        toast.success(`Successfully upgraded to ${tier} plan!`);
        return { success: true, data: response };
      } else {
        toast.error(response.message || 'Upgrade failed');
        return { success: false, error: response.message };
      }
    } catch (error) {
      console.error('Upgrade error:', error);
      toast.error('Upgrade failed. Please try again.');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const trackGpuUsage = async (gpuData) => {
    try {
      if (!apiKey) {
        throw new Error('No API key available');
      }
      
      const response = await apiService.trackGpuUsage(apiKey, gpuData);
      
      if (response.status === 'success') {
        return { success: true, data: response };
      } else {
        toast.error(response.error || 'Failed to track GPU usage');
        return { success: false, error: response.error };
      }
    } catch (error) {
      console.error('GPU tracking error:', error);
      toast.error('Failed to track GPU usage');
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    apiKey,
    loading,
    signup,
    login,
    logout,
    updateUser,
    upgradeAccount,
    trackGpuUsage,
    isAuthenticated: !!user && !!apiKey,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
