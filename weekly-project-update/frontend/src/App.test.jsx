import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";

vi.mock("./components/RichTextEditor", () => ({
  default: ({ id, value, onChange, disabled }) => (
    <textarea
      id={id}
      value={value || ""}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    />
  ),
}));

beforeEach(() => {
  localStorage.setItem("auth_token", "test-token");
  localStorage.setItem("user_id", "user-1");
  localStorage.setItem("username", "employee");
  localStorage.setItem("role", "EMPLOYEE");
});

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

function renderApp() {
  return render(<AuthProvider><App /></AuthProvider>);
}

async function completeForm(user) {
  fireEvent.change(screen.getByLabelText(/Start of week/), { target: { value: "2026-07-20" } });
  await user.selectOptions(screen.getByLabelText(/Team \/ project/), "CustAppIS");
  await user.type(screen.getByLabelText(/Achievements/), "Delivered reporting");
  await user.type(screen.getByLabelText(/Initiatives/), "Improve telemetry");
  await user.type(screen.getByLabelText(/Next week's plan/), "Measure adoption");
}

describe("App", () => {
  it("links validation errors to required fields", async () => {
    renderApp();
    await userEvent.click(await screen.findByRole("button", { name: "Submit update" }));
    const start = screen.getByLabelText(/Start of week/);
    expect(start).toHaveAttribute("aria-invalid", "true");
    expect(start).toHaveAccessibleDescription("This field is required.");
    expect(screen.getByRole("alert")).toHaveTextContent("Review the highlighted fields");
  });

  it("switches to filtered reports view after successful submission", async () => {
    const record = {
      id: "update-1", start_of_week: "2026-07-20", end_of_week: "2026-07-26", team_project: "CustAppIS",
      achievements: "Delivered reporting", initiatives: "Improve telemetry", next_weeks_plan: "Measure adoption",
      created_at: "2026-07-27T10:00:00Z", updated_at: "2026-07-27T10:00:00Z",
    };
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({ ok: true, json: async () => ({ exists: false }) })  // checkExistingReport
      .mockResolvedValueOnce({ ok: true, json: async () => record })               // submitProjectUpdate
      .mockResolvedValueOnce({ ok: true, json: async () => [record] });            // fetchProjectUpdates
    const user = userEvent.setup();
    renderApp();
    await screen.findByRole("button", { name: "Submit update" });
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    const banner = await screen.findByRole("status");
    expect(banner).toHaveTextContent(/Showing reports for:/);
    expect(banner).toHaveTextContent("CustAppIS");
  });

  it("retains form values after an ambiguous transport failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Network unavailable"));
    const user = userEvent.setup();
    renderApp();
    await screen.findByRole("button", { name: "Submit update" });
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Retry request" })).toBeInTheDocument());
    expect(screen.getByLabelText(/Start of week/)).toHaveValue("2026-07-20");
    expect(screen.getByLabelText(/End of week/)).toHaveValue("2026-07-26");
  });
});