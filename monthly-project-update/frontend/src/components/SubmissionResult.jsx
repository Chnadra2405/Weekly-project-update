import { CheckCircle2 } from "lucide-react";

export default function SubmissionResult({ result, onNew }) {
  return (
    <section className="ssg-result ssg-result--saved" role="status" aria-live="polite" tabIndex="-1">
      <CheckCircle2 size={24} aria-hidden="true" />
      <div>
        <h2>Update saved</h2>
        <p>Your weekly project update is stored.</p>
        <dl>
          <div><dt>Reference</dt><dd>{result.id}</dd></div>
          <div><dt>Start of week</dt><dd>{result.start_of_week}</dd></div>
          <div><dt>End of week</dt><dd>{result.end_of_week}</dd></div>
          <div><dt>Team / project</dt><dd>{result.team_project}</dd></div>
          <div><dt>Achievements</dt><dd>{result.achievements}</dd></div>
          <div><dt>Initiatives</dt><dd>{result.initiatives}</dd></div>
          <div><dt>{"Next week's plan"}</dt><dd>{result.next_weeks_plan}</dd></div>
          <div><dt>Created</dt><dd><time dateTime={result.created_at}>{result.created_at}</time></dd></div>
          <div><dt>Updated</dt><dd><time dateTime={result.updated_at}>{result.updated_at}</time></dd></div>
        </dl>
        <button className="ssg-button ssg-button--secondary" type="button" onClick={onNew}>Start new submission</button>
      </div>
    </section>
  );
}