import api from './client';

export const getOperatorDashboard = async () => {
  const { data } = await api.get('/operator/dashboard');
  return data;
};

export const getOperatorBookings = async () => {
  const { data } = await api.get('/operator/bookings');
  return data;
};
