import axios from "axios";
import keycloak from "../auth/keycloak";

const api = axios.create({
  baseURL: "/api/v1",
});

api.interceptors.request.use((config) => {
  if (keycloak.token) {
    config.headers.Authorization = `Bearer ${keycloak.token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      keycloak.logout();
      return Promise.reject(err);
    }
    const detail = err.response?.data?.detail ?? err.message ?? "Неизвестная ошибка";
    const text = typeof detail === "string" ? detail : JSON.stringify(detail);
    const code = err.response?.status ? ` (${err.response.status})` : "";
    alert(`Ошибка запроса${code}: ${text}`);
    return Promise.reject(err);
  }
);

export default api;
