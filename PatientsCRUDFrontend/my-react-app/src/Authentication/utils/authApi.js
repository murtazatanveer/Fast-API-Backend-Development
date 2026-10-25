import API_URL from "../../Configuration/API_URL";

export const authRequest = async (endpoint, formData, errorMessage) => {
  const response = await fetch(`${API_URL}/auth/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(formData),
  });

  const data = await response.json();

  if (!response.ok) {
    const error = new Error(data.message || errorMessage);

    error.displayUi = data.displayUi ?? false;

    throw error;
  }

  return data;
};
