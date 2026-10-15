import api from './client';

export const requestQuote = async (quoteData) => {
  const { data } = await api.post('/quotes', quoteData);
  return data;
};

export const createBooking = async (bookingData, idempotencyKey) => {
  const headers = idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {};
  const { data } = await api.post('/bookings', bookingData, { headers });
  return data;
};

export const getBookings = async (status) => {
  const params = status ? { status } : {};
  const { data } = await api.get('/bookings', { params });
  return data;
};

export const getBooking = async (id) => {
  const { data } = await api.get(`/bookings/${id}`);
  return data;
};

export const cancelBooking = async (id, reason) => {
  const { data } = await api.post(`/bookings/${id}/cancel`, { reason });
  return data;
};

export const createPaymentOrder = async (bookingId) => {
  const { data } = await api.post(`/bookings/${bookingId}/payment-order`);
  return data;
};

export const verifyPayment = async (verifyData) => {
  const { data } = await api.post('/payments/verify', verifyData);
  return data;
};
