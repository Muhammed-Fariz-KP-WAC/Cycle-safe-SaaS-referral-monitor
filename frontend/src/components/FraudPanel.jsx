function shortenId(value) {
  if (!value) {
    return "Unknown";
  }

  if (value.length <= 12) {
    return value;
  }

  return `${value.slice(0, 8)}...${value.slice(-4)}`;
}

function formatCycleNode(nodeId, userById) {
  const user = userById.get(nodeId);

  if (!user) {
    return shortenId(nodeId);
  }

  return `${user.name} (${shortenId(nodeId)})`;
}

export default function FraudPanel({ fraud, users }) {
  const userById = new Map(users.map((user) => [user.id, user]));

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Fraud Monitoring</h2>
      </div>
      <div className="list-table">
        {fraud.length === 0 && <p className="empty-state">No fraud attempts logged yet.</p>}
        {fraud.map((item) => (
          <article className="list-row" key={item.id}>
            <div>
              <strong>{item.fraud_type}</strong>
              <p>
                {item.attempted_by || "Unknown"} to {item.attempted_referrer || "Unknown"}
              </p>
            </div>
            <div>
              <p>
                {item.cycle_path?.length
                  ? item.cycle_path.map((nodeId) => formatCycleNode(nodeId, userById)).join(" -> ")
                  : "No cycle path"}
              </p>
              <small>{new Date(item.created_at).toLocaleString()}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
