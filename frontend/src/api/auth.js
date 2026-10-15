import api, { setAccessToken } from './client';

export const register = async (userData) => {
  const { data } = await api.post('/auth/register', userData);
  return data;
};

export const login = async (credentials) => {
  const { data } = await api.post('/auth/login', credentials);
  setAccessToken(data.access_token);
  return data;
};

export const logout = async () => {
  await api.post('/auth/logout');
  setAccessToken(null);
};

export const getMe = async () => {
  const { data } = await api.get('/auth/me');
  return data;
};

export const updatePreferences = async (preferences) => {
  const { data } = await api.put('/auth/preferences', preferences);
  return data;
};

export const getNotifications = async () => {
  const { data } = await api.get('/auth/notifications');
  return data;
};
