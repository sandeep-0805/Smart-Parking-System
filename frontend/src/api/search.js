import api from './client';

export const searchParking = async (params) => {
  const { data } = await api.get('/search', { params });
  return data;
};

export const getLocationForecast = async (locationId, targetTime) => {
  const params = targetTime ? { target_time: targetTime } : {};
  const { data } = await api.get(`/locations/${locationId}/forecast`, { params });
  return data;
};
