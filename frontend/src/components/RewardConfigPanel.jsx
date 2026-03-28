import { useEffect, useState } from "react";

export default function RewardConfigPanel({ fetchConfig, onSave }) {
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchConfig()
      .then((config) => setForm(config))
      .catch((requestError) => setError(requestError.message || "Could not load reward config"));
  }, [fetchConfig]);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!form) {
      return;
    }
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const updated = await onSave({
        max_depth: Number(form.max_depth),
        reward_type: form.reward_type,
        level_1_value: Number(form.level_1_value),
        level_2_value: Number(form.level_2_value),
        level_3_value: Number(form.level_3_value),
        velocity_limit: Number(form.velocity_limit),
        referral_expiry_days: Number(form.referral_expiry_days),
      });
      setForm(updated);
      setMessage("Reward config updated successfully.");
    } catch (saveError) {
      setError(saveError.message || "Could not update reward config");
    } finally {
      setLoading(false);
    }
  }

  if (!form) {
    return (
      <section className="panel">
        <div className="panel-head">
          <h2>Reward Config</h2>
        </div>
        <p className="empty-state">Loading reward config...</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Reward Config</h2>
      </div>
      <form className="sim-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Max depth</span>
          <input
            type="number"
            value={form.max_depth}
            onChange={(event) => setForm({ ...form, max_depth: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Reward type</span>
          <select
            value={form.reward_type}
            onChange={(event) => setForm({ ...form, reward_type: event.target.value })}
          >
            <option value="fixed">fixed</option>
            <option value="percentage">percentage</option>
          </select>
        </label>
        <label className="field">
          <span>Level 1 value</span>
          <input
            type="number"
            step="0.01"
            value={form.level_1_value}
            onChange={(event) => setForm({ ...form, level_1_value: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Level 2 value</span>
          <input
            type="number"
            step="0.01"
            value={form.level_2_value}
            onChange={(event) => setForm({ ...form, level_2_value: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Level 3 value</span>
          <input
            type="number"
            step="0.01"
            value={form.level_3_value}
            onChange={(event) => setForm({ ...form, level_3_value: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Velocity limit (per minute)</span>
          <input
            type="number"
            value={form.velocity_limit}
            onChange={(event) => setForm({ ...form, velocity_limit: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Referral expiry days</span>
          <input
            type="number"
            value={form.referral_expiry_days}
            onChange={(event) => setForm({ ...form, referral_expiry_days: event.target.value })}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save config"}
        </button>
      </form>
      {message && <p className="success-text">{message}</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
