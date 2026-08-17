import DOMPurify from "dompurify";
import { AlertCircle, ChevronDown, ChevronUp, Pencil, RefreshCw, X } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchProjectUpdates } from "../api";
import ReportEditor from "./ReportEditor";

const ALLOWED_TAGS = ["p", "strong", "em", "s", "ul", "ol", "li", "br", "blockquote", "code"];
const PREVIEW_LENGTH = 130;

function formatDate(value) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function stripHtml(html) {
  return (html || "").replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
}

function SafeHtml({ html, className }) {
  const clean = DOMPurify.sanitize(html || "", { ALLOWED_TAGS, ALLOWED_ATTR: [] });
  const content = clean.startsWith("<") ? clean : `<p>${clean}</p>`;
  return <div className={className} dangerouslySetInnerHTML={{ __html: content }} />;
}

function ContentCell({ reportId, field, label, html, expandedCells, onToggle }) {
  const key = `${reportId}-${field}`;
  const expanded = expandedCells.has(key);
  const plain = stripHtml(html);
  const truncated = plain.length > PREVIEW_LENGTH;

  return (
    <td data-label={label}>
      {!truncated || expanded ? (
        <SafeHtml html={html} className="ssg-rt-content" />
      ) : (
        <p className="ssg-rt-preview">{plain.slice(0, PREVIEW_LENGTH)}&hellip;</p>
      )}
      {truncated && (
        <button type="button" className="ssg-expand-btn" onClick={() => onToggle(key)}>
          {expanded
            ? <><ChevronUp size={13} aria-hidden="true" /> Show less</>
            : <><ChevronDown size={13} aria-hidden="true" /> Show more</>}
        </button>
      )}
    </td>
  );
}

function groupByWeek(reports) {
  const map = new Map();
  for (const report of reports) {
    const key = `${report.start_of_week}|${report.end_of_week}`;
    if (!map.has(key)) map.set(key, { start: report.start_of_week, end: report.end_of_week, rows: [] });
    map.get(key).rows.push(report);
  }
  return [...map.values()].sort((a, b) => b.start.localeCompare(a.start));
}

function isCurrentMonth(dateValue) {
  const date = new Date(`${dateValue}T00:00:00`);
  const now = new Date();
  return date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth();
}

function isOldMonth(dateValue) {
  const date = new Date(`${dateValue}T00:00:00`);
  const now = new Date();
  if (date.getFullYear() < now.getFullYear()) return true;
  if (date.getFullYear() > now.getFullYear()) return false;
  return date.getMonth() < now.getMonth();
}

export default function ReportsPage({ auth, filterTeam, onClearFilter, timeFilter = "all" }) {
  const [reports, setReports] = useState([]);
  const [state, setState] = useState("loading");
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null);
  const [expandedCells, setExpandedCells] = useState(new Set());

  function toggleCell(key) {
    setExpandedCells((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key); else next.add(key);
      return next;
    });
  }

  async function loadReports() {
    setState("loading");
    setError("");
    try {
      setReports(await fetchProjectUpdates());
      setState("ready");
    } catch (requestError) {
      setError(requestError.message);
      setState("error");
    }
  }

  useEffect(() => {
    loadReports();
  }, []);

  function handleSaved(savedReport) {
    setReports((current) => current.map((r) => (r.id === savedReport.id ? savedReport : r)));
    setEditing(null);
  }

  if (editing) {
    return <ReportEditor report={editing} onCancel={() => setEditing(null)} onSaved={handleSaved} />;
  }

  const allGroups = groupByWeek(reports);
  const monthFilteredGroups = allGroups
    .map((g) => ({
      ...g,
      rows: g.rows.filter((r) => {
        if (timeFilter === "current-month") return isCurrentMonth(r.start_of_week);
        if (timeFilter === "old") return isOldMonth(r.start_of_week);
        return true;
      }),
    }))
    .filter((g) => g.rows.length > 0);
  const weekGroups = filterTeam
    ? monthFilteredGroups
        .map((g) => ({ ...g, rows: g.rows.filter((r) => r.team_project === filterTeam) }))
        .filter((g) => g.rows.length > 0)
    : monthFilteredGroups;

  const reportHeading = timeFilter === "current-month"
    ? "Current month reports"
    : timeFilter === "old"
      ? "Old reports"
      : "Submitted reports";

  return (
    <section className="ssg-reports" aria-labelledby="reports-heading">
      <div className="ssg-reports__heading">
        <div>
          <p className="ssg-eyebrow">Reporting history</p>
          <h2 id="reports-heading">{reportHeading}</h2>
        </div>
        <button
          type="button"
          className="ssg-button ssg-button--secondary"
          onClick={loadReports}
          disabled={state === "loading"}
        >
          <RefreshCw size={18} aria-hidden="true" />Refresh
        </button>
      </div>
      {filterTeam && (
        <div className="ssg-filter-banner" role="status">
          <span>Showing reports for: <strong>{filterTeam}</strong></span>
          <button type="button" className="ssg-filter-clear" onClick={onClearFilter} title="Show all reports">
            <X size={15} aria-hidden="true" /> Show all
          </button>
        </div>
      )}
      {state === "loading" && <p role="status">Loading reports...</p>}
      {state === "error" && (
        <div className="ssg-summary" role="alert">
          <AlertCircle size={20} aria-hidden="true" />
          <div><strong>Reports could not be loaded.</strong><p>{error}</p></div>
        </div>
      )}
      {state === "ready" && weekGroups.length === 0 && (
        <div className="ssg-empty-state">
          <h3>No reports found</h3>
          <p>
            {filterTeam
              ? `No reports submitted for ${filterTeam} yet.`
              : reportHeading === "Current month reports"
                ? "No reports submitted in the current month yet."
                : reportHeading === "Old reports"
                  ? "No reports from older months yet."
                  : "Submitted weekly reports will appear here."}
          </p>
        </div>
      )}
      {state === "ready" && weekGroups.map((group) => (
        <div key={`${group.start}|${group.end}`} className="ssg-week-group">
          <p className="ssg-week-label">
            Reporting Week: <strong>{formatDate(group.start)}</strong> to <strong>{formatDate(group.end)}</strong>
          </p>
          <div className="ssg-table-wrap">
            <table className="ssg-data-table ssg-report-table">
              <caption className="ssg-visually-hidden">
                Reports for week {formatDate(group.start)} to {formatDate(group.end)}
              </caption>
              <thead>
                <tr>
                  <th scope="col">Team</th>
                  <th scope="col">Achievements <span className="ssg-col-hint">(Key Deliverables Completed)</span></th>
                  <th scope="col">Initiatives <span className="ssg-col-hint">(Major Work Started/Ongoing)</span></th>
                  <th scope="col">{"Next Week's plan"} <span className="ssg-col-hint">(Top 2 to 3 priorities)</span></th>
                  <th scope="col"><span className="ssg-visually-hidden">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {group.rows.map((report) => {
                  const canEdit = report.user_id === auth.id;
                  return (
                    <tr key={report.id}>
                      <td data-label="Team" className="ssg-team-cell">{report.team_project}</td>
                      <ContentCell
                        reportId={report.id} field="achievements" label="Achievements"
                        html={report.achievements} expandedCells={expandedCells} onToggle={toggleCell}
                      />
                      <ContentCell
                        reportId={report.id} field="initiatives" label="Initiatives"
                        html={report.initiatives} expandedCells={expandedCells} onToggle={toggleCell}
                      />
                      <ContentCell
                        reportId={report.id} field="next_weeks_plan" label="Next Week's plan"
                        html={report.next_weeks_plan} expandedCells={expandedCells} onToggle={toggleCell}
                      />
                      <td data-label="Actions" className="ssg-table-actions">
                        {canEdit && (
                          <button
                            type="button"
                            className="ssg-icon-button"
                            onClick={() => setEditing(report)}
                            aria-label={`Edit report for ${formatDate(report.start_of_week)}`}
                            title="Edit report"
                          >
                            <Pencil size={18} aria-hidden="true" />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </section>
  );
}
