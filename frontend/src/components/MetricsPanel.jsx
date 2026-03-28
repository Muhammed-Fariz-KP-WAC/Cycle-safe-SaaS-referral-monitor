export default function MetricsPanel({ metrics }) {
  const cards = metrics
    ? [
        ["Total Users", metrics.total_users],
        ["Total Referrals", metrics.total_referrals],
        ["Valid vs Rejected", `${metrics.valid_referrals} / ${metrics.rejected_referrals}`],
        ["Fraud Attempts", metrics.fraud_attempts],
        ["Rewards Distributed", `Rs ${metrics.total_rewards_distributed}`],
      ]
    : [];

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Key Metrics</h2>
        <span className="live-pill">Live</span>
      </div>
      <div className="metric-grid">
        {cards.map(([label, value]) => (
          <article className="metric-card" key={label}>
            <p>{label}</p>
            <strong>{value}</strong>
          </article>
        ))}
      </div>
      {metrics && (
        <p className="metric-footnote">
          Average cycle check: {metrics.avg_cycle_check_ms} ms. Fraud breakdown:{" "}
          {Object.entries(metrics.fraud_breakdown)
            .map(([type, count]) => `${type} ${count}`)
            .join(", ")}
        </p>
      )}
    </section>
  );
}
