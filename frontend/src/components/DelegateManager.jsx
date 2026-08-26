import { AlertCircle, CheckCircle, Trash2, UserCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { assignDelegate, fetchDelegations, fetchUsers, removeDelegate } from "../api";

export default function DelegateManager() {
  const [managers, setManagers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [managerId, setManagerId] = useState("");
  const [delegateId, setDelegateId] = useState("");
  const [state, setState] = useState("idle");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const [mgrs, users, dels] = await Promise.all([
        fetchUsers("TEAM_MANAGER"),
        fetchUsers(),
        fetchDelegations(),
      ]);
      setManagers(mgrs);
      setAllUsers(users);
      setDelegations(dels);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAssign(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setState("submitting");
    try {
      await assignDelegate(managerId, delegateId);
      const mgr = managers.find((m) => m.id === managerId);
      const del = allUsers.find((u) => u.id === delegateId);
      setMessage(
        `${del?.username ?? "User"} is now the active delegate for ${mgr?.username ?? "the manager"}.`
      );
      setManagerId("");
      setDelegateId("");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setState("idle");
    }
  }

  async function handleRemove(mgrId, mgrUsername) {
    setMessage("");
    setError("");
    try {
      await removeDelegate(mgrId);
      setMessage(`Delegate removed for ${mgrUsername}.`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  const roleLabel = {
    APP_ADMIN: "App Admin",
    DU_HEAD: "DU Head",
    TEAM_MANAGER: "Team Manager",
    TEAM_LEAD: "Team Lead",
  };

  return (
    <section className="ssg-reports" aria-labelledby="delegate-heading">
      <div className="ssg-reports__heading">
        <div>
          <p className="ssg-eyebrow">Administration</p>
          <h2 id="delegate-heading">Assign Manager Delegate</h2>
        </div>
      </div>

      <div style={{ maxWidth: "520px" }}>
        <p style={{ marginBottom: "1.5rem", color: "#6b7280", lineHeight: 1.6 }}>
          When a Team Manager is unavailable or absent, assign another user to review
          and approve reports on their behalf. Only one active delegate per manager is
          allowed — assigning a new one automatically replaces the previous.
        </p>

        {error && (
          <div className="ssg-summary" role="alert" style={{ marginBottom: "1rem" }}>
            <AlertCircle size={20} aria-hidden="true" />
            <div><strong>Error.</strong> <span>{error}</span></div>
          </div>
        )}

        {message && (
          <div
            className="ssg-summary"
            role="status"
            style={{ background: "#d1fae5", borderColor: "#065f46", marginBottom: "1rem" }}
          >
            <CheckCircle size={20} aria-hidden="true" style={{ color: "#065f46" }} />
            <div><strong style={{ color: "#065f46" }}>{message}</strong></div>
          </div>
        )}

        <form onSubmit={handleAssign} noValidate>
          <div className="ssg-field">
            <label htmlFor="absent-manager">
              Absent Team Manager <span aria-hidden="true">*</span>
            </label>
            <select
              id="absent-manager"
              value={managerId}
              onChange={(e) => { setManagerId(e.target.value); setDelegateId(""); }}
              required
              disabled={state === "submitting"}
              aria-required="true"
            >
              <option value="">Select a Team Manager</option>
              {managers.map((m) => (
                <option key={m.id} value={m.id}>{m.username}</option>
              ))}
            </select>
          </div>

          <div className="ssg-field">
            <label htmlFor="delegate-user">
              Acting Delegate <span aria-hidden="true">*</span>
            </label>
            <select
              id="delegate-user"
              value={delegateId}
              onChange={(e) => setDelegateId(e.target.value)}
              required
              disabled={state === "submitting" || !managerId}
              aria-required="true"
            >
              <option value="">Select a user</option>
              {allUsers
                .filter((u) => u.id !== managerId)
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.username} — {roleLabel[u.role] ?? u.role}
                  </option>
                ))}
            </select>
            {managerId && (
              <small style={{ color: "#6b7280" }}>
                The selected user will be able to review and approve reports until the
                delegate is changed or removed.
              </small>
            )}
          </div>

          <div style={{ marginTop: "1.5rem" }}>
            <button
              type="submit"
              className="ssg-button ssg-button--primary"
              disabled={state === "submitting" || !managerId || !delegateId}
            >
              <UserCheck size={18} aria-hidden="true" />
              {state === "submitting" ? "Assigning…" : "Assign Delegate"}
            </button>
          </div>
        </form>

        {delegations.length > 0 && (
          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.75rem" }}>Active Delegates</h3>
            <table className="ssg-data-table" style={{ width: "100%" }}>
              <thead>
                <tr>
                  <th scope="col">Manager</th>
                  <th scope="col">Delegate</th>
                  <th scope="col"><span className="ssg-visually-hidden">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {delegations.map((d) => (
                  <tr key={d.manager_id}>
                    <td>{d.manager_username}</td>
                    <td>{d.delegate_username}</td>
                    <td className="ssg-table-actions">
                      <button
                        type="button"
                        className="ssg-icon-button"
                        onClick={() => handleRemove(d.manager_id, d.manager_username)}
                        aria-label={`Remove delegate for ${d.manager_username}`}
                        title="Remove delegate"
                        style={{ color: "#dc2626" }}
                      >
                        <Trash2 size={18} aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
