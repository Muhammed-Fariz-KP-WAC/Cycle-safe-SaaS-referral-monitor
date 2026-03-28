import { useState } from "react";

export default function ClaimReferralForm({ users, onSubmit }) {
  const [form, setForm] = useState({
    new_user_id: "",
    referrer_code: "",
    edge_type: "primary",
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await onSubmit(form);
      setResult(response);
    } catch (submitError) {
      setError(submitError.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Create Referral Claim</h2>
      </div>
      <form className="sim-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Select user</span>
          <select
            value={form.new_user_id}
            onChange={(event) => setForm({ ...form, new_user_id: event.target.value })}
            required
          >
            <option value="">Choose user</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} ({user.referral_code})
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>New user ID</span>
          <input
            value={form.new_user_id}
            onChange={(event) => setForm({ ...form, new_user_id: event.target.value })}
            placeholder="UUID of child user"
            required
          />
        </label>
        <label className="field">
          <span>Select referrer</span>
          <select
            value={form.referrer_code}
            onChange={(event) => setForm({ ...form, referrer_code: event.target.value })}
            required
          >
            <option value="">Choose referrer</option>
            {users.map((user) => (
              <option key={user.id} value={user.referral_code}>
                {user.name} ({user.referral_code})
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Referrer code</span>
          <input
            value={form.referrer_code}
            onChange={(event) => setForm({ ...form, referrer_code: event.target.value })}
            placeholder="ALICE-001"
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit claim"}
        </button>
      </form>
      {error && <p className="error-text">{error}</p>}
      {result && (
        <div className="sim-result">
          <p>Status: {result.status}</p>
          <p>Message: {result.message}</p>
          <p>Cycle check: {result.cycle_check_ms} ms</p>
        </div>
      )}
    </section>
  );
}
