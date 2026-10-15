import api from './client';

export const getLocations = async (status) => {
  const params = status ? { status } : {};
  const { data } = await api.get('/locations', { params });
  return data;
};

export const getLocation = async (id) => {
  const { data } = await api.get(`/locations/${id}`);
  return data;
};

export const createLocation = async (locationData) => {
  const { data } = await api.post('/locations', locationData);
  return data;
};

export const updateLocation = async (id, locationData) => {
  const { data } = await api.patch(`/locations/${id}`, locationData);
  return data;
};

export const deleteLocation = async (id) => {
  const { data } = await api.delete(`/locations/${id}`);
  return data;
};

export const approveLocation = async (id) => {
  const { data } = await api.post(`/locations/${id}/approve`);
  return data;
};
