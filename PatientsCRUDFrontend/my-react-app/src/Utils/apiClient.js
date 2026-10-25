import API_URL from "../Configuration/API_URL";

const refreshAccessToken = async () => {
  const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!refreshResponse.ok) {
    throw new Error("Refresh Failed");
  }

  const refreshData = await refreshResponse.json();
  const newToken = refreshData.data.accessToken;
  localStorage.setItem("accessToken", newToken);
  return newToken;
};

export const fetchApi = async (
  endpoint,
  options = {},
  withCredentials = false,
) => {
  let token = localStorage.getItem("accessToken");

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
    console.log("Token expired, attempting to refresh...");

    try {
      const newToken = await refreshAccessToken();
      requestConfig.headers.authToken = `Bearer_${newToken}`;

      response = await fetch(`${API_URL}${endpoint}`, requestConfig);

      if (response.status === 401) {
        throw new Error("Refresh Request Again Failed");
      }
    } catch (error) {
      localStorage.removeItem("accessToken");

      const sessionError = new Error("Session expired. Please log in again.");

      sessionError.displayUi = true;

      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);

      throw sessionError;
    }
  }

  return response;
};
