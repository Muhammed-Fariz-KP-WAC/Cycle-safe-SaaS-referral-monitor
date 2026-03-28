import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function fetchMetrics() {
  const response = await apiClient.get('/dashboard/metrics');
  return response.data;
}

export async function fetchActivities() {
  const response = await apiClient.get('/dashboard/activities');
  return response.data;
}

export async function fetchFraudFlags() {
  const response = await apiClient.get('/fraud/flags');
  return response.data;
}

export async function fetchUserGraph(userId) {
  const response = await apiClient.get(`/user/${userId}/graph`);
  return response.data;
}

export async function fetchUsers() {
  const response = await apiClient.get('/user');
  return response.data;
}

export async function createUser(payload) {
  const response = await apiClient.post('/user', payload);
  return response.data;
}

export async function claimReferral(payload) {
  const response = await apiClient.post('/referral/claim', payload);
  return response.data;
}

export async function simulateRewards(payload) {
  const response = await apiClient.post('/dashboard/simulate', payload);
  return response.data;
}

export async function fetchRewardConfig() {
  const response = await apiClient.get('/admin/reward-config');
  return response.data;
}

export async function patchRewardConfig(payload) {
  const response = await apiClient.patch('/admin/reward-config', payload);
  return response.data;
}

export function createEventStream(onEvent) {
  const source = new EventSource(`${API_BASE}/dashboard/stream`);
  ["referral_activity", "fraud_alert"].forEach((eventName) => {
    source.addEventListener(eventName, (event) => {
      onEvent(eventName, JSON.parse(event.data));
    });
  });
  return source;
}
