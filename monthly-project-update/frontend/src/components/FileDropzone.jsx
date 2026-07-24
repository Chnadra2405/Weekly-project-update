import { FileUp, Trash2 } from "lucide-react";

function formatBytes(bytes) {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MiB`;
}

export default function FileDropzone({ id, label, hint, accept, file, error, disabled, onChange }) {
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  return (
    <div className="ssg-file-field">
      <span className="ssg-label">{label} <span className="ssg-optional">Optional</span></span>
      {file ? (
        <div className="ssg-selected-file">
          <FileUp size={20} aria-hidden="true" />
          <span><strong>{file.name}</strong><small>{formatBytes(file.size)}</small></span>
          <label className="ssg-replace" htmlFor={id}>Replace</label>
          <button type="button" className="ssg-icon-button" aria-label={`Remove ${label}`} title={`Remove ${label}`} disabled={disabled} onClick={() => onChange(null)}>
            <Trash2 size={18} aria-hidden="true" />
          </button>
        </div>
      ) : (
        <label className="ssg-dropzone" htmlFor={id}>
          <FileUp size={24} aria-hidden="true" />
          <strong>Select a file</strong>
          <span>{hint}</span>
        </label>
      )}
      <input
        className="ssg-visually-hidden"
        id={id}
        type="file"
        accept={accept}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={`${hintId}${error ? ` ${errorId}` : ""}`}
        onChange={(event) => onChange(event.target.files?.[0] || null)}
      />
      <small id={hintId} className="ssg-helper">Maximum 10 MiB.</small>
      {error && <small id={errorId} className="ssg-error">{error}</small>}
    </div>
  );
}