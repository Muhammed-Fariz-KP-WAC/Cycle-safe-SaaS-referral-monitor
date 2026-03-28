function shortenId(value) {
  if (!value) {
    return "Unknown";
  }

  if (value.length <= 12) {
    return value;
  }

  return `${value.slice(0, 8)}...${value.slice(-4)}`;
}

function resolveUserLabel(userId, fallbackName, userById) {
  if (fallbackName) {
    return fallbackName;
  }

  const user = userById.get(userId);

  if (user?.name) {
    return user.name;
  }

  return shortenId(userId);
}

function formatMoney(value) {
  return `Rs ${Number(value || 0).toLocaleString()}`;
}

function formatRewardSummary(rewards, userById) {
  if (!Array.isArray(rewards) || rewards.length === 0) {
    return "No reward distributed";
  }

  return rewards
    .map((reward) => {
      const beneficiary = resolveUserLabel(reward.user_id, reward.user_name, userById);
      return `${beneficiary}: ${formatMoney(reward.amount)} (L${reward.depth})`;
    })
    .join(" • ");
}

function formatCyclePath(path, userById) {
  if (!Array.isArray(path) || path.length === 0) {
    return "No cycle path";
  }

  return path.map((nodeId) => resolveUserLabel(nodeId, null, userById)).join(" -> ");
}

function getFraudTitle(payload, userById) {
  const actor = resolveUserLabel(payload.new_user_id, payload.new_user_name, userById);
  const referrer = resolveUserLabel(payload.referrer_id, payload.referrer_name, userById);

  switch (payload.type) {
    case "cycle":
      return `Cycle prevented: ${actor} -> ${referrer}`;
    case "velocity":
      return `Velocity blocked: ${actor} -> ${referrer}`;
    case "new_account_velocity":
      return `Fresh account flagged: ${actor} -> ${referrer}`;
    case "duplicate":
      return `Duplicate referral blocked: ${actor} -> ${referrer}`;
    case "self_referral":
      return `Self-referral blocked: ${actor}`;
    default:
      return `Fraud alert: ${actor} -> ${referrer}`;
  }
}

function describeActivity(activity, userById) {
  const payload = activity.payload || {};

  if (activity.event_type === "referral_activity" && payload.type === "accepted") {
    const referrer = resolveUserLabel(payload.referrer_id, payload.referrer_name, userById);
    const newUser = resolveUserLabel(payload.new_user_id, payload.new_user_name, userById);

    return {
      badge: "Referral",
      badgeClassName: "is-referral",
      title: `${referrer} referred ${newUser}`,
      summary: `Reward chain: ${formatRewardSummary(payload.rewards, userById)}`,
      meta: `Cycle check: ${payload.cycle_check_ms ?? 0} ms`,
    };
  }

  if (activity.event_type === "fraud_alert") {
    return {
      badge: "Fraud",
      badgeClassName: "is-fraud",
      title: getFraudTitle(payload, userById),
      summary:
        payload.type === "cycle"
          ? `Cycle path: ${formatCyclePath(payload.cycle_path, userById)}`
          : `Reason: ${(payload.type || "unknown").replaceAll("_", " ")}`,
      meta:
        payload.type === "cycle" && payload.cycle_path?.length
          ? `${payload.cycle_path.length} nodes involved`
          : "Blocked before reward distribution",
    };
  }

  return {
    badge: "Event",
    badgeClassName: "is-generic",
    title: activity.event_type.replaceAll("_", " "),
    summary: JSON.stringify(payload),
    meta: "Recorded activity",
  };
}

export default function ActivityFeed({ activities, users }) {
  const userById = new Map(users.map((user) => [user.id, user]));

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Activity Feed</h2>
      </div>
      <div className="feed">
        {activities.length === 0 && <p className="empty-state">No activity captured yet.</p>}
        {activities.map((activity) => {
          const event = describeActivity(activity, userById);

          return (
            <article className="feed-item" key={activity.id}>
              <div className="feed-item-head">
                <span className={`feed-badge ${event.badgeClassName}`}>{event.badge}</span>
                <small>{new Date(activity.created_at).toLocaleString()}</small>
              </div>
              <strong>{event.title}</strong>
              <p>{event.summary}</p>
              <small>{event.meta}</small>
            </article>
          );
        })}
      </div>
    </section>
  );
}
