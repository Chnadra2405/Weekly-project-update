import { AlertCircle, LogIn } from "lucide-react";
import { useState } from "react";

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("TEAM_LEAD");
  const [team, setTeam] = useState("");

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Login failed");
      }
      const token_data = await response.json();
      localStorage.setItem("auth_token", token_data.access_token);
      localStorage.setItem("user_id", token_data.user_id);
      localStorage.setItem("username", token_data.username);
      localStorage.setItem("role", token_data.role);
      onLoginSuccess(token_data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          email,
          password,
          role,
          team: team || null,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Registration failed");
      }
      const token_data = await response.json();
      localStorage.setItem("auth_token", token_data.access_token);
      localStorage.setItem("user_id", token_data.user_id);
      localStorage.setItem("username", token_data.username);
      localStorage.setItem("role", token_data.role);
      onLoginSuccess(token_data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ssg-auth-container">
      <header className="ssg-header">
        <div>
          <span className="ssg-product-mark">WPU</span>
          <h1>Weekly Project Update</h1>
        </div>
      </header>
      <main className="ssg-main">
        <div className="ssg-login-box">
          <div className="ssg-login-header">
            <LogIn size={24} aria-hidden="true" />
            <h2>{showRegister ? "Create Account" : "Sign In"}</h2>
          </div>

          {error && (
            <div className="ssg-alert" role="alert">
              <AlertCircle size={18} aria-hidden="true" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={showRegister ? handleRegister : handleLogin} noValidate>
            {showRegister && (
              <div className="ssg-field">
                <label htmlFor="email">Email <span aria-hidden="true">*</span></label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  aria-required="true"
                />
              </div>
            )}

            <div className="ssg-field">
              <label htmlFor="username">Username <span aria-hidden="true">*</span></label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
                aria-required="true"
              />
            </div>

            <div className="ssg-field">
              <label htmlFor="password">Password <span aria-hidden="true">*</span></label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                aria-required="true"
              />
            </div>

            {showRegister && (
              <>
                <div className="ssg-field">
                  <label htmlFor="role">Role <span aria-hidden="true">*</span></label>
                  <select
                    id="role"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    required
                    disabled={loading}
                    aria-required="true"
                  >
                    <option value="TEAM_LEAD">Team Lead</option>
                    <option value="TEAM_MANAGER">Team Manager</option>
                    <option value="DU_HEAD">DU Head</option>
                    <option value="APP_ADMIN">Application Admin</option>
                  </select>
                </div>

                <div className="ssg-field">
                  <label htmlFor="team">Team</label>
                  <input
                    id="team"
                    type="text"
                    value={team}
                    onChange={(e) => setTeam(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="ssg-button-primary"
            >
              {loading ? "Processing..." : showRegister ? "Create Account" : "Sign In"}
            </button>
          </form>

          <button
            type="button"
            onClick={() => {
              setShowRegister(!showRegister);
              setError("");
            }}
            className="ssg-link"
          >
            {showRegister
              ? "Already have an account? Sign In"
              : "Don't have an account? Create one"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default LoginPage;
