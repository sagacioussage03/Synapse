import axios from 'axios';

// Point this to your FastAPI backend!
const API_BASE = 'http://192.168.1.84:8000'; 

export const hardwareApi = {
    toggleTorch: (state) => axios.post(`${API_BASE}/hardware/torch/${state}`),
    speak: (text) => axios.post(`${API_BASE}/hardware/speak?text=${encodeURIComponent(text)}`),
    vibrate: () => axios.post(`${API_BASE}/hardware/vibrate`),
  };
  
  export const systemApi = {
    getProcesses: () => axios.get(`${API_BASE}/system/processes`),
    getHealth: () => axios.get(`${API_BASE}/system/health`),
    getBattery: () => axios.get(`${API_BASE}/system/battery`),   // or /hardware/battery
    getNetwork: () => axios.get(`${API_BASE}/system/network`),
  };

  export const alarmApi = {
    getAlarm: () => axios.get(`${API_BASE}/alarm`),
    setAlarm: ({ time, active }) =>
      axios.post(`${API_BASE}/alarm`, { time, active }),
  };