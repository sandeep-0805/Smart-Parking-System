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

export const getLocationSuggestions = async (query) => {
  if (!query || query.trim().length < 3) return [];
  const { data } = await api.get('/search/suggestions', { params: { q: query.trim() } });
  return data;
};

export const reverseGeocodeCoords = async (lat, lng) => {
  const { data } = await api.get('/search/reverse-geocode', { params: { lat, lng } });
  return data;
};
