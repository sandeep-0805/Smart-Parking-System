import api from './client';

export const sendChatMessage = async (message, sessionId) => {
  const { data } = await api.post('/chat', {
    message,
    session_id: sessionId,
  });
  return data;
};
