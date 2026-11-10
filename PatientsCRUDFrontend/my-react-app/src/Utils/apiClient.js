import API_URL from "../Configuration/API_URL";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
  subscribeToAccessToken,
} from "./authTokenStore";

let refreshPromise = null;
let sessionExpiryHandled = false;

subscribeToAccessToken(() => {
  if (getAccessToken()) {
    sessionExpiryHandled = false;
  }
});

const handleSessionExpired = () => {
  if (sessionExpiryHandled) return;

  sessionExpiryHandled = true;
  clearAccessToken();

  setTimeout(() => {
    window.location.href = "/login";
  }, 2000);
};

export const refreshAccessToken = async () => {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    })
      .then(async (refreshResponse) => {
        if (!refreshResponse.ok) {
          throw new Error("Refresh Failed");
        }

        const refreshData = await refreshResponse.json();
        const newToken = refreshData?.data?.accessToken;

        if (!newToken) {
          throw new Error("Refresh Failed");
        }

        setAccessToken(newToken);
        return newToken;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
};

export const fetchApi = async (
  endpoint,
  options = {},
  withCredentials = false,
) => {
  let token = getAccessToken();

  const requestConfig = {
    ...options,
    headers: {
      ...options.headers,
      ...(token && { authToken: `Bearer_${token}` }),
    },
    ...(withCredentials && { credentials: "include" }),
  };

  let response = await fetch(`${API_URL}${endpoint}`, requestConfig);

  if (response.status === 401) {
    try {
      const latestToken = getAccessToken();
      const newToken =
        latestToken && latestToken !== token
          ? latestToken
          : await refreshAccessToken();

      requestConfig.headers.authToken = `Bearer_${newToken}`;

      response = await fetch(`${API_URL}${endpoint}`, requestConfig);

      if (response.status === 401) {
        throw new Error("Refresh Request Again Failed");
      }
    } catch {
      handleSessionExpired();

      const sessionError = new Error("Session expired. Please log in again.");

      sessionError.displayUi = true;

      throw sessionError;
    }
  }

  return response;
};
