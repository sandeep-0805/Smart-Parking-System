import api from './client';

export const getAdminUsers = async (params) => {
  const { data } = await api.get('/admin/users', { params });
  return data;
};

export const updateUserRole = async (userId, role) => {
  const { data } = await api.patch(`/admin/users/${userId}/role`, { role });
  return data;
};

export const updateUserStatus = async (userId, status) => {
  const { data } = await api.patch(`/admin/users/${userId}/status`, { status });
  return data;
};

export const getSystemConfig = async () => {
  const { data } = await api.get('/admin/config');
  return data;
};

export const updateSystemConfig = async (key, value) => {
  const { data } = await api.patch(`/admin/config/${key}`, { config_value: value });
  return data;
};

export const getAdminAuditLog = async (limit = 50) => {
  const { data } = await api.get('/admin/audit-log', { params: { limit } });
  return data;
};

export const getAllLocationsAdmin = async () => {
  const { data } = await api.get('/admin/locations');
  return data;
};
