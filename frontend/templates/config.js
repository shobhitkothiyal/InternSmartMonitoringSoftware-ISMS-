const configuredApiBaseUrl = import.meta.env?.VITE_API_BASE_URL?.trim();
const browserHost = typeof window !== "undefined" ? window.location.hostname : "";
const isLocalHost = browserHost === "localhost" || browserHost === "127.0.0.1";

const getLocalAlignedApiBaseUrl = (baseUrl) => {
  if (!baseUrl || typeof window === "undefined" || !isLocalHost) return baseUrl;

  try {
    const url = new URL(baseUrl);
    const apiHostIsLocal = url.hostname === "localhost" || url.hostname === "127.0.0.1";
    if (apiHostIsLocal && url.hostname !== browserHost) {
      url.hostname = browserHost;
      return url.toString().replace(/\/$/, "");
    }
  } catch (error) {
    console.warn("Invalid VITE_API_BASE_URL:", error);
  }

  return baseUrl;
};

const inferredApiBaseUrl =
  typeof window !== "undefined"
    ? isLocalHost
      ? `http://${browserHost}:5000`
      : window.location.origin
    : "http://localhost:5000";

export const API_BASE_URL = getLocalAlignedApiBaseUrl(
  configuredApiBaseUrl || inferredApiBaseUrl
).replace(/\/$/, "");

export const getApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}`;
 
