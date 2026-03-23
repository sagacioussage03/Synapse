import axios from 'axios';

// Read from Vite env – update .env when your phone's IP changes
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
console.log('🔗 Synapse Environment Info:', {
  VITE_API_BASE: import.meta.env.VITE_API_BASE,
  MODE: import.meta.env.MODE,
  DEV: import.meta.env.DEV,
  FINAL_BASE: API_BASE
});

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