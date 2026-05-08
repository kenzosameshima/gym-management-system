import axios from "axios";

const apiUrl = import.meta.env.VITE_API_URL;
export const AUTH_TOKEN_STORAGE_KEY = "gym_management_access_token";

export const httpClient = axios.create({
  baseURL: apiUrl,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json"
  }
});

httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
  if (token !== null) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

