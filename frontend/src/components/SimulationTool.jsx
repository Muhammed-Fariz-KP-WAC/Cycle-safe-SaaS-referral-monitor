import { useState } from "react";

export default function SimulationTool({ onSimulate }) {
  const [form, setForm] = useState({
    depth: 3,
    reward_type: "fixed",
    values: [100, 50, 25],
    expected_users: 100,
    avg_referrals_per_user: 1.5,
  });
  const [result, setResult] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const next = await onSimulate({
      ...form,
      depth: Number(form.depth),
      expected_users: Number(form.expected_users),
      avg_referrals_per_user: Number(form.avg_referrals_per_user),
      values: form.values.map(Number),
    });
    setResult(next);
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Reward Simulator</h2>
      </div>
      <form className="sim-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Depth</span>
          <input
            type="number"
            value={form.depth}
            onChange={(event) => setForm({ ...form, depth: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Expected users</span>
          <input
            type="number"
            value={form.expected_users}
            onChange={(event) => setForm({ ...form, expected_users: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Average referrals per user</span>
          <input
            type="number"
            step="0.1"
            value={form.avg_referrals_per_user}
            onChange={(event) => setForm({ ...form, avg_referrals_per_user: event.target.value })}
          />
        </label>
        <button type="submit">Run simulation</button>
      </form>
      {result && (
        <div className="sim-result">
          <p>Total projected payout: Rs {result.projected_total_payout}</p>
          <p>Cost per acquisition: Rs {result.cost_per_acquisition}</p>
        </div>
      )}
    </section>
  );
}
