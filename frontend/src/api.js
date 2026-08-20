const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function getAuthToken() {
  return localStorage.getItem("auth_token");
}

function getHeaders() {
  const token = getAuthToken();
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function errorMessage(detail) {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        // Handle FastAPI validation error format
        if (item?.msg && item?.loc) {
          const field = item.loc[item.loc.length - 1];
          return `${field}: ${item.msg}`;
        }
        return item?.msg;
      })
      .filter(Boolean);
    if (messages.length) return messages.join("; ");
  }
  return "The service could not process this update.";
}

export async function submitProjectUpdate(values, idempotencyKey) {
  const token = getAuthToken();
  if (!token) {
    throw new Error("Authentication token not found. Please login first.");
  }

  if (!idempotencyKey || typeof idempotencyKey !== "string" || !idempotencyKey.trim()) {
    throw new Error("Idempotency key is required for submission.");
  }

  const body = new FormData();
  Object.entries(values).forEach(([name, value]) => {
    body.append(name, value);
  });

  console.log("Submitting form with Idempotency-Key:", idempotencyKey);
  console.log("Form values:", values);

  const response = await fetch(`${API_BASE_URL}/project-updates`, {
    method: "POST",
    headers: {
      "Idempotency-Key": idempotencyKey,
      Authorization: `Bearer ${token}`,
    },
    body,
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }
  if (!response.ok) {
    console.error("API error response:", payload);
    const error = new Error(errorMessage(payload.detail));
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function parseResponse(response) {
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

export async function fetchProjectUpdates() {
  const response = await fetch(`${API_BASE_URL}/project-updates`, {
    headers: getHeaders(),
  });
  return parseResponse(response);
}

export async function checkExistingReport(start_of_week, team_project) {
  const params = new URLSearchParams({ start_of_week, team_project });
  const response = await fetch(`${API_BASE_URL}/project-updates/check?${params}`, {
    headers: getHeaders(),
  });
  return parseResponse(response);
}

export async function updateProjectUpdate(updateId, values) {
  const response = await fetch(`${API_BASE_URL}/project-updates/${updateId}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(values),
  });
  return parseResponse(response);
}

export async function approveReport(reportId) {
  const response = await fetch(`${API_BASE_URL}/project-updates/${reportId}/approve`, {
    method: "POST",
    headers: getHeaders(),
  });
  return parseResponse(response);
}

export async function exportReports(format) {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/project-updates/export/${format}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    let payload = {};
    try { payload = await response.json(); } catch { /* ignore */ }
    const error = new Error(errorMessage(payload.detail));
    error.status = response.status;
    throw error;
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = format === "excel" ? "weekly_project_updates.xlsx" : "weekly_project_updates.pptx";
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  // Delay cleanup so the browser has time to start the download
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 200);
}

export async function assignDelegate(managerId, delegateId) {
  const response = await fetch(`${API_BASE_URL}/auth/delegate`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ manager_id: managerId, delegate_id: delegateId }),
  });
  return parseResponse(response);
}

export async function fetchUsers(role) {
  const params = role ? `?role=${encodeURIComponent(role)}` : "";
  const response = await fetch(`${API_BASE_URL}/auth/users${params}`, {
    headers: getHeaders(),
  });
  return parseResponse(response);
}
