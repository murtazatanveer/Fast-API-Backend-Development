let accessToken = null;
const listeners = new Set();

export const getAccessToken = () => accessToken;

export const setAccessToken = (token) => {
  accessToken = token || null;

  listeners.forEach((listener) => {
    listener();
  });
};

export const clearAccessToken = () => {
  setAccessToken(null);
};

export const subscribeToAccessToken = (listener) => {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
};
