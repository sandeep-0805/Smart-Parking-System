import api from './client';

export const getAutoBookingRules = async () => {
  const { data } = await api.get('/auto-booking/rules');
  return data;
};

export const createAutoBookingRule = async (ruleData) => {
  const { data } = await api.post('/auto-booking/rules', ruleData);
  return data;
};

export const updateAutoBookingRule = async (id, ruleData) => {
  const { data } = await api.patch(`/auto-booking/rules/${id}`, ruleData);
  return data;
};

export const deleteAutoBookingRule = async (id) => {
  const { data } = await api.delete(`/auto-booking/rules/${id}`);
  return data;
};

export const getAutoBookingAudit = async () => {
  const { data } = await api.get('/auto-booking/audit');
  return data;
};
