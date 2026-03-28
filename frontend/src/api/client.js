const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function readJson(response) {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Request failed");
  }
  return response.json();
}

export async function fetchMetrics() {
  return readJson(await fetch(`${API_BASE}/dashboard/metrics`));
}

export async function fetchActivities() {
  return readJson(await fetch(`${API_BASE}/dashboard/activities`));
}

export async function fetchFraudFlags() {
  return readJson(await fetch(`${API_BASE}/fraud/flags`));
}

export async function fetchUserGraph(userId) {
  return readJson(await fetch(`${API_BASE}/user/${userId}/graph`));
}

export async function fetchUsers() {
  return readJson(await fetch(`${API_BASE}/user`));
}

export async function createUser(payload) {
  return readJson(
    await fetch(`${API_BASE}/user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function claimReferral(payload) {
  return readJson(
    await fetch(`${API_BASE}/referral/claim`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function simulateRewards(payload) {
  return readJson(
    await fetch(`${API_BASE}/dashboard/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function fetchRewardConfig() {
  return readJson(await fetch(`${API_BASE}/admin/reward-config`));
}

export async function patchRewardConfig(payload) {
  return readJson(
    await fetch(`${API_BASE}/admin/reward-config`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
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
