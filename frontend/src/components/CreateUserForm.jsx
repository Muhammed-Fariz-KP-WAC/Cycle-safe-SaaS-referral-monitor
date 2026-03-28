import { useState } from "react";

export default function CreateUserForm({ onSubmit }) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    referral_code: "",
    status: "active",
    is_root: false,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const user = await onSubmit(form);
      setMessage(`Created user: ${user.name} (${user.referral_code})`);
      setForm({
        ...form,
        name: "",
        email: "",
        referral_code: "",
      });
    } catch (submitError) {
      setError(submitError.message || "Could not create user");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Create User</h2>
      </div>
      <form className="sim-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Name</span>
          <input
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            placeholder="New user name"
            required
          />
        </label>
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            placeholder="new.user@example.com"
            required
          />
        </label>
        <label className="field">
          <span>Referral Code</span>
          <input
            value={form.referral_code}
            onChange={(event) => setForm({ ...form, referral_code: event.target.value.toUpperCase() })}
            placeholder="USR-NEW001"
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create user"}
        </button>
      </form>
      {message && <p className="success-text">{message}</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
