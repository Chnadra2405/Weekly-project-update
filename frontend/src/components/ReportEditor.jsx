import { AlertCircle, Save, X } from "lucide-react";
import { useState } from "react";
import { updateProjectUpdate } from "../api";
import { endOfWeek, validateForm } from "../validation";
import RichTextEditor from "./RichTextEditor";

const teamProjects = ["CustAppIS", "DSI Tools", "Auroria", "Other AI Initiatives"];

function formatDate(value) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

export default function ReportEditor({ report, headingId = "edit-report-heading", onCancel, onSaved }) {
  const [values, setValues] = useState({
    start_of_week: report.start_of_week,
    end_of_week: report.end_of_week,
    team_project: report.team_project,
    achievements: report.achievements,
    initiatives: report.initiatives,
    next_weeks_plan: report.next_weeks_plan,
  });
  const [errors, setErrors] = useState({});
  const [requestError, setRequestError] = useState("");
  const [saving, setSaving] = useState(false);

  function updateValue(event) {
    const { name, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: value,
      ...(name === "start_of_week" ? { end_of_week: endOfWeek(value) } : {}),
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const found = validateForm(values);
    setErrors(found);
    setRequestError("");
    if (Object.keys(found).length) return;

    setSaving(true);
    try {
      onSaved(await updateProjectUpdate(report.id, values));
    } catch (error) {
      setRequestError(error.message);
    } finally {
      setSaving(false);
    }
  }

  function fieldProps(name) {
    return {
      id: `edit-${name}`,
      name,
      value: values[name],
      onChange: updateValue,
      disabled: saving,
      required: true,
      "aria-invalid": Boolean(errors[name]),
      "aria-describedby": errors[name] ? `edit-${name}-error` : undefined,
    };
  }

  return (
    <section className="ssg-report-editor" aria-labelledby={headingId}>
      <div className="ssg-report-editor__heading">
        <div>
          <p className="ssg-eyebrow">Edit existing report</p>
          <h2 id={headingId}>
            {report.team_project} &mdash; week of {formatDate(report.start_of_week)}
          </h2>
        </div>
        {onCancel && (
          <button type="button" className="ssg-icon-button" onClick={onCancel} aria-label="Close report editor" title="Close editor">
            <X size={20} aria-hidden="true" />
          </button>
        )}
      </div>
      {requestError && (
        <div className="ssg-summary" role="alert">
          <AlertCircle size={20} aria-hidden="true" />
          <p>{requestError}</p>
        </div>
      )}
      <form onSubmit={handleSubmit} noValidate>
        <div className="ssg-edit-grid">
          <div className="ssg-field">
            <label htmlFor="edit-start_of_week">Start of week</label>
            <input {...fieldProps("start_of_week")} type="date" />
            {errors.start_of_week && <small id="edit-start_of_week-error" className="ssg-error">{errors.start_of_week}</small>}
          </div>
          <div className="ssg-field">
            <label htmlFor="edit-end_of_week">End of week</label>
            <input {...fieldProps("end_of_week")} type="date" readOnly />
            {errors.end_of_week && <small id="edit-end_of_week-error" className="ssg-error">{errors.end_of_week}</small>}
          </div>
          <div className="ssg-field">
            <label htmlFor="edit-team_project">Team / project</label>
            <select {...fieldProps("team_project")}>
              {teamProjects.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            {errors.team_project && <small id="edit-team_project-error" className="ssg-error">{errors.team_project}</small>}
          </div>
        </div>
        {[["achievements", "Achievements"], ["initiatives", "Initiatives"], ["next_weeks_plan", "Next week's plan"]].map(([name, label]) => (
          <div className="ssg-field" key={name}>
            <label htmlFor={`edit-${name}`}>{label}</label>
            <RichTextEditor
              id={`edit-${name}`}
              value={values[name]}
              onChange={(html) => setValues((current) => ({ ...current, [name]: html }))}
              disabled={saving}
              invalid={Boolean(errors[name])}
              describedBy={errors[name] ? `edit-${name}-error` : undefined}
            />
            {errors[name] && <small id={`edit-${name}-error`} className="ssg-error">{errors[name]}</small>}
          </div>
        ))}
        <div className="ssg-editor-actions">
          {onCancel && (
            <button type="button" className="ssg-button ssg-button--secondary" onClick={onCancel} disabled={saving}>Cancel</button>
          )}
          <button type="submit" className="ssg-button ssg-button--primary" disabled={saving}>
            <Save size={18} aria-hidden="true" />
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </form>
    </section>
  );
}
