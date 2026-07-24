import { AlertCircle, CalendarDays, Send } from "lucide-react";
import { useRef, useState } from "react";
import { submitProjectUpdate } from "./api";
import FileDropzone from "./components/FileDropzone";
import SubmissionResult from "./components/SubmissionResult";
import { validateForm } from "./validation";

const initialValues = {
  employee_name: "", employee_email: "", reporting_month: "", team_project: "",
  achievements: "", initiatives: "", next_weeks_plan: "",
};

function Field({ id, label, error, children }) {
  return <div className="ssg-field"><label htmlFor={id}>{label} <span aria-hidden="true">*</span></label>{children}{error && <small id={`${id}-error`} className="ssg-error">{error}</small>}</div>;
}

export default function App() {
  const [values, setValues] = useState(initialValues);
  const [files, setFiles] = useState({ reference_email: null, image: null });
  const [errors, setErrors] = useState({});
  const [state, setState] = useState("idle");
  const [result, setResult] = useState(null);
  const [requestError, setRequestError] = useState("");
  const keyRef = useRef(crypto.randomUUID());
  const summaryRef = useRef(null);

  const updateValue = (event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }));
  const inputProps = (name) => ({
    id: name, name, value: values[name], disabled: state === "submitting", onChange: updateValue,
    required: true, "aria-required": "true",
    "aria-invalid": Boolean(errors[name]), "aria-describedby": errors[name] ? `${name}-error` : undefined,
  });

  async function handleSubmit(event) {
    event.preventDefault();
    const found = validateForm(values, files);
    setErrors(found);
    setRequestError("");
    if (Object.keys(found).length) {
      setState("invalid");
      queueMicrotask(() => summaryRef.current?.focus());
      return;
    }
    setState("submitting");
    try {
      const payload = await submitProjectUpdate(values, files, keyRef.current);
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
    setFiles({ reference_email: null, image: null });
    setErrors({});
    setResult(null);
    setRequestError("");
    setState("idle");
  }

  return (
    <>
      <header className="ssg-header"><div><span className="ssg-product-mark">MPU</span><h1>Monthly Project Update</h1></div><span className="ssg-month-label"><CalendarDays size={18} aria-hidden="true" /> Reporting workspace</span></header>
      <main className="ssg-main">
        <div className="ssg-intro"><div><p className="ssg-eyebrow">Employee reporting</p><h2>{"Capture this month's progress"}</h2></div><p>Submit one concise update for one team or project. Required fields are marked with an asterisk.</p></div>
        {result ? <SubmissionResult result={result} onNew={startNew} /> : (
          <form onSubmit={handleSubmit} noValidate>
            <p className="ssg-visually-hidden" role="status" aria-live="assertive" aria-atomic="true">
              {state === "submitting" ? "Submitting project update." : ""}
            </p>
            {(state === "invalid" || state === "transport-error" || state === "conflict") && (
              <div className="ssg-summary" role="alert" tabIndex="-1" ref={summaryRef}>
                <AlertCircle size={20} aria-hidden="true" /><div><strong>{state === "conflict" ? "This request key belongs to different content." : state === "transport-error" ? "Delivery status could not be confirmed." : "Review the highlighted fields."}</strong>
                {requestError && <p>{requestError}</p>}</div>
              </div>
            )}
            <div className="ssg-form-grid">
              <section className="ssg-form-section" aria-labelledby="details-heading">
                <div className="ssg-section-heading"><span>01</span><div><h2 id="details-heading">Reporting details</h2><p>Who is reporting, and for which work?</p></div></div>
                <div className="ssg-two-columns">
                  <Field id="employee_name" label="Employee name" error={errors.employee_name}><input {...inputProps("employee_name")} type="text" maxLength="200" autoComplete="name" /></Field>
                  <Field id="employee_email" label="Employee email" error={errors.employee_email}><input {...inputProps("employee_email")} type="email" maxLength="320" autoComplete="email" /></Field>
                  <Field id="reporting_month" label="Reporting month" error={errors.reporting_month}><input {...inputProps("reporting_month")} type="month" /></Field>
                  <Field id="team_project" label="Team / project" error={errors.team_project}><input {...inputProps("team_project")} type="text" maxLength="300" /></Field>
                </div>
              </section>
              <section className="ssg-form-section" aria-labelledby="update-heading">
                <div className="ssg-section-heading"><span>02</span><div><h2 id="update-heading">Monthly narrative</h2><p>Keep each area specific and outcome focused.</p></div></div>
                {[ ["achievements", "Achievements"], ["initiatives", "Initiatives"], ["next_weeks_plan", "Next week's plan"] ].map(([name, label]) => (
                  <Field key={name} id={name} label={label} error={errors[name]}><textarea {...inputProps(name)} maxLength="5000" rows="5" /><small className="ssg-count">{values[name].length} / 5000</small></Field>
                ))}
              </section>
            </div>
            <section className="ssg-form-section ssg-attachments" aria-labelledby="attachments-heading">
              <div className="ssg-section-heading"><span>03</span><div><h2 id="attachments-heading">Supporting files</h2><p>Add evidence only when it helps the recipient understand the update.</p></div></div>
              <div className="ssg-two-columns">
                <FileDropzone id="reference_email" label="Reference email" hint="EML or MSG" accept=".eml,.msg,message/rfc822,application/vnd.ms-outlook" file={files.reference_email} error={errors.reference_email} disabled={state === "submitting"} onChange={(file) => setFiles((current) => ({ ...current, reference_email: file }))} />
                <FileDropzone id="image" label="Image" hint="PNG, JPEG, or WebP" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" file={files.image} error={errors.image} disabled={state === "submitting"} onChange={(file) => setFiles((current) => ({ ...current, image: file }))} />
              </div>
            </section>
            <footer className="ssg-form-actions"><p>Your submission is stored before email delivery is attempted.</p><div>{state === "conflict" && <button type="button" className="ssg-button ssg-button--secondary" onClick={startNew}>Start new submission</button>}<button type="submit" className="ssg-button ssg-button--primary" disabled={state === "submitting"}><Send size={18} aria-hidden="true" />{state === "submitting" ? "Submitting..." : state === "transport-error" ? "Retry request" : "Submit update"}</button></div></footer>
          </form>
        )}
      </main>
    </>
  );
}