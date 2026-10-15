import api from './client';

export const getSlots = async (locationId) => {
  const { data } = await api.get(`/locations/${locationId}/slots`);
  return data;
};

export const createSlot = async (locationId, slotData) => {
  const { data } = await api.post(`/locations/${locationId}/slots`, slotData);
  return data;
};

export const bulkCreateSlots = async (locationId, bulkData) => {
  const { data } = await api.post(`/locations/${locationId}/slots/bulk`, bulkData);
  return data;
};

export const updateSlot = async (id, slotData) => {
  const { data } = await api.patch(`/slots/${id}`, slotData);
  return data;
};

export const blockSlot = async (id) => {
  const { data } = await api.post(`/slots/${id}/block`);
  return data;
};

export const unblockSlot = async (id) => {
  const { data } = await api.post(`/slots/${id}/unblock`);
  return data;
};
