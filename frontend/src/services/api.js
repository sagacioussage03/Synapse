import axios from 'axios';

// ── API Base URL ────────────────────────────────────────
// Since the frontend and backend both run on the phone,
// we derive the backend URL from the browser's current
// hostname. This works whether you access the app from
// localhost (on the phone) or from your desktop via the
// phone's IP address — no .env file needed.
const API_BASE = import.meta.env.VITE_API_BASE
  || `http://${window.location.hostname}:8000`;

console.log('📡 Synapse API →', API_BASE);

export const hardwareApi = {
  toggleTorch: (state) => axios.post(`${API_BASE}/hardware/torch/${state}`),
  speak: (text) => axios.post(`${API_BASE}/hardware/speak?text=${encodeURIComponent(text)}`),
  vibrate: () => axios.post(`${API_BASE}/hardware/vibrate`),
};

export const systemApi = {
  getProcesses: () => axios.get(`${API_BASE}/system/processes`),
  getHealth: () => axios.get(`${API_BASE}/system/health`),
  getBattery: () => axios.get(`${API_BASE}/system/battery`),
  getNetwork: () => axios.get(`${API_BASE}/system/network`),
};

export const configApi = {
  getServices: () => axios.get(`${API_BASE}/config/services`),
};