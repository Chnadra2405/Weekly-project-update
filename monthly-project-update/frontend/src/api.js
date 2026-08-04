const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function errorMessage(detail) {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg).filter(Boolean);
    if (messages.length) return messages.join(" ");
  }
  return "The service could not process this update.";
}

export async function submitProjectUpdate(values, idempotencyKey) {
  const body = new FormData();
  Object.entries(values).forEach(([name, value]) => body.append(name, value));

  const response = await fetch(`${API_BASE_URL}/project-updates`, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body,
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }
  if (!response.ok) {
    const error = new Error(errorMessage(payload.detail));
    error.status = response.status;
    throw error;
  }
  return payload;
}