import { AlertCircle, Archive, FilePlus2, Files, LogOut, Send, UserCheck } from "lucide-react";
import { useRef, useState, useEffect, useCallback } from "react";
import { useAuth } from "./contexts/AuthContext";
import { submitProjectUpdate, checkExistingReport } from "./api";
import LoginPage from "./components/LoginPage";
import ReportsPage from "./components/ReportsPage";
import ReportEditor from "./components/ReportEditor";
import RichTextEditor from "./components/RichTextEditor";
import SubmissionResult from "./components/SubmissionResult";
import DelegateManager from "./components/DelegateManager";
import { endOfWeek, validateForm } from "./validation";

const initialValues = {
  start_of_week: "", end_of_week: "", team_project: "",
  achievements: "", initiatives: "", next_weeks_plan: "",
};

const teamProjects = ["CustAppIS", "DSI Tools", "Auroria", "Other AI Initiatives"];

function Field({ id, label, error, children }) {
  return <div className="ssg-field"><label htmlFor={id}>{label} <span aria-hidden="true">*</span></label>{children}{error && <small id={`${id}-error`} className="ssg-error">{error}</small>}</div>;
}

function reportTabForWeek(startOfWeek) {
  const date = new Date(`${startOfWeek}T00:00:00`);
  const now = new Date();
  const sameMonth = date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth();
  return sameMonth ? "current" : "old";
}

function ProjectUpdateForm() {
  const { auth, logout } = useAuth();
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [state, setState] = useState("idle");
  const [result, setResult] = useState(null);
  const [requestError, setRequestError] = useState("");
  const canCreateReports = auth?.role === "TEAM_LEAD" || auth?.role === "APP_ADMIN";
  const [view, setView] = useState(canCreateReports ? "create" : "current");
  const [existingReport, setExistingReport] = useState(null);
  const [checkingDuplicate, setCheckingDuplicate] = useState(false);
  const [filterTeam, setFilterTeam] = useState(null);
  const keyRef = useRef(crypto.randomUUID());
  const summaryRef = useRef(null);

  // Check for an existing report whenever start_of_week + team_project are both filled.
  const checkDuplicate = useCallback(async (start, team) => {
    if (!start || !team) { setExistingReport(null); return; }
    setCheckingDuplicate(true);
    try {
      const data = await checkExistingReport(start, team);
      setExistingReport(data.exists ? data.report : null);
    } catch {
      setExistingReport(null);
    } finally {
      setCheckingDuplicate(false);
    }
  }, []);

  useEffect(() => {
    checkDuplicate(values.start_of_week, values.team_project);
  }, [values.start_of_week, values.team_project, checkDuplicate]);

  const updateValue = (event) => {
    const { name, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: value,
      ...(name === "start_of_week" ? { end_of_week: endOfWeek(value) } : {}),
    }));
  };
  const inputProps = (name) => ({
    id: name, name, value: values[name], disabled: state === "submitting", onChange: updateValue,
    required: true, "aria-required": "true",
    "aria-invalid": Boolean(errors[name]), "aria-describedby": errors[name] ? `${name}-error` : undefined,
  });

  async function handleSubmit(event) {
    event.preventDefault();
    const found = validateForm(values);
    setErrors(found);
    setRequestError("");
    if (Object.keys(found).length) {
      setState("invalid");
      queueMicrotask(() => summaryRef.current?.focus());
      return;
    }
    setState("submitting");
    try {
      const payload = await submitProjectUpdate(values, keyRef.current);
      setResult(payload);
      setState("complete");
      setView(reportTabForWeek(payload.start_of_week));
      setFilterTeam(payload.team_project);
    } catch (error) {
      setRequestError(error.message);
      setState(error.status === 409 ? "conflict" : error.status === 422 ? "invalid" : "transport-error");
      queueMicrotask(() => summaryRef.current?.focus());
    }
  }

  function startNew() {
    keyRef.current = crypto.randomUUID();
    setValues(initialValues);
    setErrors({});
    setResult(null);
    setRequestError("");
    setState("idle");
    setExistingReport(null);
  }

  function handleEditSaved(saved) {
    setExistingReport(null);
    setValues(initialValues);
    setState("idle");
    setView(reportTabForWeek(saved.start_of_week));
    setFilterTeam(saved.team_project);
  }

  function clearSelection() {
    setExistingReport(null);
    setValues((current) => ({ ...current, start_of_week: "", end_of_week: "", team_project: "" }));
  }

  return (
    <>
      <header className="ssg-header">
        <div><span className="ssg-product-mark">WPU</span><h1>Weekly Project Update</h1></div>
        <div className="ssg-header-user">
          <span className="ssg-username">{auth?.username} ({auth?.role})</span>
          <button onClick={logout} className="ssg-logout-btn" title="Sign out">
            <LogOut size={18} aria-hidden="true" />
            Sign out
          </button>
        </div>
      </header>
      <nav className="ssg-view-tabs" aria-label="Project update views">
        {canCreateReports && (
          <button type="button" className={view === "create" ? "is-active" : ""} aria-current={view === "create" ? "page" : undefined} onClick={() => { startNew(); setView("create"); setFilterTeam(null); }}><FilePlus2 size={18} aria-hidden="true" />Create report</button>
        )}
        <button type="button" className={view === "current" ? "is-active" : ""} aria-current={view === "current" ? "page" : undefined} onClick={() => setView("current")}><Files size={18} aria-hidden="true" />Current Month reports</button>
        <button type="button" className={view === "old" ? "is-active" : ""} aria-current={view === "old" ? "page" : undefined} onClick={() => setView("old")}><Archive size={18} aria-hidden="true" />Old reports</button>
        {auth?.role === "APP_ADMIN" && (
          <button type="button" className={view === "delegates" ? "is-active" : ""} aria-current={view === "delegates" ? "page" : undefined} onClick={() => setView("delegates")}><UserCheck size={18} aria-hidden="true" />Delegates</button>
        )}
      </nav>
      {view === "delegates" ? <main className="ssg-main"><DelegateManager /></main> : view === "current" || view === "old" ? <main className="ssg-main"><ReportsPage auth={auth} filterTeam={filterTeam} onClearFilter={() => setFilterTeam(null)} timeFilter={view === "current" ? "current-month" : "old"} /></main> : (
      <main className="ssg-main">
        <div className="ssg-intro"><div><p className="ssg-eyebrow">Weekly reporting</p><h2>{"Capture this week's progress"}</h2></div><p>Submit one concise update for one team or project. Required fields are marked with an asterisk.</p></div>
        {result ? <SubmissionResult result={result} onNew={startNew} /> : existingReport ? (
          <>
            {existingReport.user_id === auth.id ? (
              <>
                <div className="ssg-duplicate-notice" role="status">
                  <AlertCircle size={20} aria-hidden="true" />
                  <div>
                    <strong>A report already exists for this week and team.</strong>
                    <p>Submission is disabled. Edit the existing report below.</p>
                  </div>
                </div>
                <ReportEditor
                  report={existingReport}
                  headingId="inline-edit-heading"
                  onCancel={startNew}
                  onSaved={handleEditSaved}
                />
              </>
            ) : (
              <div className="ssg-duplicate-notice ssg-duplicate-notice--locked" role="alert">
                <AlertCircle size={20} aria-hidden="true" />
                <div>
                  <strong>A report already exists for this week and team.</strong>
                  <p>
                    Submitted by <strong>{existingReport.owner_username || "another user"}</strong>.
                    Only the report owner can edit it.
                  </p>
                  <button type="button" className="ssg-button ssg-button--secondary ssg-duplicate-back" onClick={clearSelection}>
                    Change week or team
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            <p className="ssg-visually-hidden" role="status" aria-live="assertive" aria-atomic="true">
              {state === "submitting" ? "Submitting project update." : ""}
              {checkingDuplicate ? "Checking for existing report." : ""}
            </p>
            {(state === "invalid" || state === "transport-error" || state === "conflict") && (
              <div className="ssg-summary" role="alert" tabIndex="-1" ref={summaryRef}>
                <AlertCircle size={20} aria-hidden="true" /><div><strong>{state === "conflict" ? "This request key belongs to different content." : state === "transport-error" ? "Submission status could not be confirmed." : "Review the highlighted fields."}</strong>
                {requestError && <p>{requestError}</p>}</div>
              </div>
            )}
            <div className="ssg-form-grid">
              <section className="ssg-form-section" aria-labelledby="details-heading">
                <div className="ssg-section-heading"><span>01</span><div><h2 id="details-heading">Reporting details</h2><p>Choose the week and team or project.</p></div></div>
                <div className="ssg-two-columns">
                  <Field id="start_of_week" label="Start of week" error={errors.start_of_week}><input {...inputProps("start_of_week")} type="date" /></Field>
                  <Field id="end_of_week" label="End of week" error={errors.end_of_week}><input {...inputProps("end_of_week")} type="date" readOnly /></Field>
                  <Field id="team_project" label="Team / project" error={errors.team_project}>
                    <select {...inputProps("team_project")}>
                      <option value="">Select a team or project</option>
                      {teamProjects.map((teamProject) => <option key={teamProject} value={teamProject}>{teamProject}</option>)}
                    </select>
                  </Field>
                </div>
              </section>
              <section className="ssg-form-section" aria-labelledby="update-heading">
                <div className="ssg-section-heading"><span>02</span><div><h2 id="update-heading">Weekly narrative</h2><p>Keep each area specific and outcome focused.</p></div></div>
                {[ ["achievements", "Achievements"], ["initiatives", "Initiatives"], ["next_weeks_plan", "Next week's plan"] ].map(([name, label]) => (
                  <Field key={name} id={name} label={label} error={errors[name]}>
                    <RichTextEditor
                      id={name}
                      value={values[name]}
                      onChange={(html) => setValues((current) => ({ ...current, [name]: html }))}
                      disabled={state === "submitting"}
                      invalid={Boolean(errors[name])}
                      describedBy={errors[name] ? `${name}-error` : undefined}
                    />
                  </Field>
                ))}
              </section>
            </div>
            <footer className="ssg-form-actions"><p>Your submission is stored as one weekly record.</p><div>{state === "conflict" && <button type="button" className="ssg-button ssg-button--secondary" onClick={startNew}>Start new submission</button>}<button type="submit" className="ssg-button ssg-button--primary" disabled={state === "submitting" || checkingDuplicate}><Send size={18} aria-hidden="true" />{state === "submitting" ? "Submitting..." : state === "transport-error" ? "Retry request" : "Submit update"}</button></div></footer>
          </form>
        )}
      </main>
      )}
    </>
  );
}

export default function App() {
  const { isAuthenticated, loading, login } = useAuth();

  if (loading) {
    return <div className="ssg-loading">Loading...</div>;
  }

  return isAuthenticated ? <ProjectUpdateForm /> : <LoginPage onLoginSuccess={login} />;
}