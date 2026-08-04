import { AlertCircle, CalendarDays, Send } from "lucide-react";
import { useRef, useState } from "react";
import { submitProjectUpdate } from "./api";
import SubmissionResult from "./components/SubmissionResult";
import { endOfWeek, validateForm } from "./validation";

const initialValues = {
  start_of_week: "", end_of_week: "", team_project: "",
  achievements: "", initiatives: "", next_weeks_plan: "",
};

const teamProjects = ["CustAppIS", "DSI Tools", "Auroria", "Other AI Initiatives"];

function Field({ id, label, error, children }) {
  return <div className="ssg-field"><label htmlFor={id}>{label} <span aria-hidden="true">*</span></label>{children}{error && <small id={`${id}-error`} className="ssg-error">{error}</small>}</div>;
}

export default function App() {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [state, setState] = useState("idle");
  const [result, setResult] = useState(null);
  const [requestError, setRequestError] = useState("");
  const keyRef = useRef(crypto.randomUUID());
  const summaryRef = useRef(null);

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
  }

  return (
    <>
      <header className="ssg-header"><div><span className="ssg-product-mark">WPU</span><h1>Weekly Project Update</h1></div><span className="ssg-period-label"><CalendarDays size={18} aria-hidden="true" /> Reporting workspace</span></header>
      <main className="ssg-main">
        <div className="ssg-intro"><div><p className="ssg-eyebrow">Weekly reporting</p><h2>{"Capture this week's progress"}</h2></div><p>Submit one concise update for one team or project. Required fields are marked with an asterisk.</p></div>
        {result ? <SubmissionResult result={result} onNew={startNew} /> : (
          <form onSubmit={handleSubmit} noValidate>
            <p className="ssg-visually-hidden" role="status" aria-live="assertive" aria-atomic="true">
              {state === "submitting" ? "Submitting project update." : ""}
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
                  <Field key={name} id={name} label={label} error={errors[name]}><textarea {...inputProps(name)} maxLength="5000" rows="5" /><small className="ssg-count">{values[name].length} / 5000</small></Field>
                ))}
              </section>
            </div>
            <footer className="ssg-form-actions"><p>Your submission is stored as one weekly record.</p><div>{state === "conflict" && <button type="button" className="ssg-button ssg-button--secondary" onClick={startNew}>Start new submission</button>}<button type="submit" className="ssg-button ssg-button--primary" disabled={state === "submitting"}><Send size={18} aria-hidden="true" />{state === "submitting" ? "Submitting..." : state === "transport-error" ? "Retry request" : "Submit update"}</button></div></footer>
          </form>
        )}
      </main>
    </>
  );
}