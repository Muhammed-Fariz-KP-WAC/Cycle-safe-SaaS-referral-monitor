import { useEffect, useState } from "react";

import {
  claimReferral,
  createEventStream,
  createUser,
  fetchActivities,
  fetchFraudFlags,
  fetchMetrics,
  fetchRewardConfig,
  fetchUserGraph,
  fetchUsers,
  patchRewardConfig,
  simulateRewards,
} from "../api/client";
import ActivityFeed from "../components/ActivityFeed";
import ClaimReferralForm from "../components/ClaimReferralForm";
import CreateUserForm from "../components/CreateUserForm";
import FraudPanel from "../components/FraudPanel";
import GraphView from "../components/GraphView";
import MetricsPanel from "../components/MetricsPanel";
import RewardConfigPanel from "../components/RewardConfigPanel";
import SimulationTool from "../components/SimulationTool";

const THEME_STORAGE_KEY = "dashboard-theme";
const TABS = [
  { id: "overview", label: "Overview" },
  { id: "network", label: "Network" },
  { id: "security", label: "Security" },
  { id: "settings", label: "Settings" },
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [users, setUsers] = useState([]);
  const [fraud, setFraud] = useState([]);
  const [activities, setActivities] = useState([]);
  const [graph, setGraph] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") {
      return "light";
    }

    return window.localStorage.getItem(THEME_STORAGE_KEY) || "light";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    async function load() {
      const [metricsData, fraudData, activityData, userData] = await Promise.all([
        fetchMetrics(),
        fetchFraudFlags(),
        fetchActivities(),
        fetchUsers(),
      ]);
      setMetrics(metricsData);
      setFraud(fraudData.flags);
      setActivities(activityData);
      setUsers(userData.users);
      if (activityData.length > 0) {
        const referralEvent = activityData.find((event) => event.payload.referrer_id);
        if (referralEvent?.payload?.referrer_id) {
          setSelectedUserId(referralEvent.payload.referrer_id);
        }
      }
    }

    load();
    const source = createEventStream((_eventName, payload) => {
      setActivities((current) => [
        ...current.slice(-24),
        {
          id: `${Date.now()}`,
          event_type: payload.type === "accepted" ? "referral_activity" : "fraud_alert",
          payload,
          created_at: new Date().toISOString(),
        },
      ]);
      fetchMetrics().then(setMetrics).catch(() => undefined);
      fetchFraudFlags().then((data) => setFraud(data.flags)).catch(() => undefined);
    });

    return () => source.close();
  }, []);

  useEffect(() => {
    if (!selectedUserId) {
      return;
    }
    fetchUserGraph(selectedUserId).then(setGraph).catch(() => undefined);
  }, [selectedUserId]);

  async function handleSimulate(payload) {
    return simulateRewards(payload);
  }

  async function refreshDashboardData() {
    const [metricsData, fraudData, activityData, userData] = await Promise.all([
      fetchMetrics(),
      fetchFraudFlags(),
      fetchActivities(),
      fetchUsers(),
    ]);
    setMetrics(metricsData);
    setFraud(fraudData.flags);
    setActivities(activityData);
    setUsers(userData.users);
  }

  async function handleClaim(payload) {
    const response = await claimReferral(payload);
    await refreshDashboardData();
    if (selectedUserId) {
      fetchUserGraph(selectedUserId).then(setGraph).catch(() => undefined);
    }
    return response;
  }

  async function handleCreateUser(payload) {
    const response = await createUser(payload);
    await refreshDashboardData();
    return response;
  }

  function handleToggleTheme() {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  }

  return (
    <main className="dashboard-shell">
      <section className="hero">
        <div className="hero-head">
          <div>
            <p className="eyebrow">Cycle-safe SaaS referral monitor</p>
            <h1>Referral Engine Dashboard</h1>
            <p className="subcopy">
              Real-time DAG integrity, fraud visibility, and reward propagation in one view.
            </p>
          </div>
          <button className="theme-toggle" type="button" onClick={handleToggleTheme}>
            <span className="theme-toggle-track">
              <span className={`theme-toggle-thumb ${theme === "dark" ? "is-dark" : ""}`} />
            </span>
            <span>{theme === "light" ? "Dark mode" : "Light mode"}</span>
          </button>
        </div>
      </section>

      <nav className="tabs-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`tab-button ${activeTab === tab.id ? "is-active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="tab-content">
        {activeTab === "overview" && (
          <>
            <MetricsPanel metrics={metrics} />
            <section className="grid">
              <ActivityFeed activities={activities} users={users} />
            </section>
          </>
        )}

        {activeTab === "network" && (
          <>
            <section className="grid">
              <CreateUserForm onSubmit={handleCreateUser} />
              <ClaimReferralForm users={users} onSubmit={handleClaim} />
            </section>
            <section className="grid">
              <GraphView
                graph={graph}
                users={users}
                selectedUserId={selectedUserId}
                onSelectUserId={setSelectedUserId}
              />
            </section>
          </>
        )}

        {activeTab === "security" && (
          <section className="grid">
            <FraudPanel fraud={fraud} users={users} />
          </section>
        )}

        {activeTab === "settings" && (
          <>
            <section className="grid">
              <RewardConfigPanel fetchConfig={fetchRewardConfig} onSave={patchRewardConfig} />
              <SimulationTool onSimulate={handleSimulate} />
            </section>
          </>
        )}
      </div>
    </main>
  );
}
