import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMe, login as apiLogin, register as apiRegister, logout as apiLogout } from '../api/auth';
import api, { setAccessToken } from '../api/client';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);

  const initAuth = async () => {
    try {
      // Attempt silent refresh first
      const { data } = await api.post('/auth/refresh', {}, { withCredentials: true });
      if (data?.access_token) {
        setAccessToken(data.access_token);
        const profile = await getMe();
        setUser(profile.user);
        setPreferences(profile.preferences);
      }
    } catch {
      // User is not logged in / session expired
      setAccessToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const data = await apiLogin(credentials);
      const profile = await getMe();
      setUser(profile.user);
      setPreferences(profile.preferences);
      toast.success(`Welcome back, ${profile.user.full_name}!`);
      return profile.user;
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Login failed. Please check your credentials.';
      toast.error(msg);
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      await apiRegister(userData);
      toast.success('Registration successful! Please log in.');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Registration failed.';
      toast.error(msg);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch {
      // Ignore network errors on logout
    } finally {
      setUser(null);
      setPreferences(null);
      toast.success('Logged out successfully');
    }
  };

  const refreshUser = async () => {
    try {
      const profile = await getMe();
      setUser(profile.user);
      setPreferences(profile.preferences);
    } catch {
      // Handled silently
    }
  };

  const value = {
    user,
    preferences,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
    isDriver: user?.role === 'DRIVER',
    isOperator: user?.role === 'OPERATOR',
    isAdmin: user?.role === 'ADMIN',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
