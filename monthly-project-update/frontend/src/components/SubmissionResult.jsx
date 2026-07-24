import { AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";

const statusCopy = {
  SENT: { title: "Update sent", detail: "Your update was saved and delivered by email.", Icon: CheckCircle2 },
  FAILED: { title: "Saved, delivery failed", detail: "Your update is safely stored, but email delivery failed. Do not create a duplicate submission.", Icon: AlertTriangle },
  PENDING: { title: "Saved, awaiting reconciliation", detail: "Your update is stored and its delivery state will be reviewed.", Icon: Clock3 },
};

export default function SubmissionResult({ result, onNew }) {
  const copy = statusCopy[result.delivery_status] || statusCopy.PENDING;
  return (
    <section className={`ssg-result ssg-result--${result.delivery_status.toLowerCase()}`} role="status" aria-live="polite" tabIndex="-1">
      <copy.Icon size={24} aria-hidden="true" />
      <div>
        <h2>{copy.title}</h2>
        <p>{copy.detail}</p>
        <dl>
          <div><dt>Reference</dt><dd>{result.id}</dd></div>
          <div><dt>Reporting month</dt><dd>{result.reporting_month}</dd></div>
          <div><dt>Team / project</dt><dd>{result.team_project}</dd></div>
          {result.smtp_message_id && <div><dt>Message ID</dt><dd>{result.smtp_message_id}</dd></div>}
          {result.failure_detail && <div><dt>Delivery detail</dt><dd>{result.failure_detail}</dd></div>}
        </dl>
        {result.attachments?.length > 0 && <p>Attachments: {result.attachments.map((item) => item.original_filename).join(", ")}</p>}
        <button className="ssg-button ssg-button--secondary" type="button" onClick={onNew}>Start new submission</button>
      </div>
    </section>
  );
}