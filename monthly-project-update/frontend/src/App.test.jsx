import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

afterEach(() => vi.restoreAllMocks());

async function completeForm(user) {
  fireEvent.change(screen.getByLabelText(/Start of week/), { target: { value: "2026-07-20" } });
  await user.selectOptions(screen.getByLabelText(/Team \/ project/), "CustAppIS");
  await user.type(screen.getByLabelText(/Achievements/), "Delivered reporting");
  await user.type(screen.getByLabelText(/Initiatives/), "Improve telemetry");
  await user.type(screen.getByLabelText(/Next week's plan/), "Measure adoption");
}

describe("App", () => {
  it("links validation errors to required fields", async () => {
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: "Submit update" }));
    const start = screen.getByLabelText(/Start of week/);
    expect(start).toHaveAttribute("aria-invalid", "true");
    expect(start).toHaveAccessibleDescription("This field is required.");
    expect(screen.getByRole("alert")).toHaveTextContent("Review the highlighted fields");
  });

  it("announces and displays the stored record", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "update-1", start_of_week: "2026-07-20", end_of_week: "2026-07-26", team_project: "CustAppIS",
        achievements: "Delivered reporting", initiatives: "Improve telemetry", next_weeks_plan: "Measure adoption",
        created_at: "2026-07-27T10:00:00Z", updated_at: "2026-07-27T10:00:00Z",
      }),
    });
    const user = userEvent.setup();
    render(<App />);
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Update saved"));
    expect(screen.getByRole("status")).toHaveTextContent("Delivered reporting");
    expect(screen.getByRole("status")).toHaveTextContent("2026-07-27T10:00:00Z");
  });

  it("retains form values after an ambiguous transport failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Network unavailable"));
    const user = userEvent.setup();
    render(<App />);
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Retry request" })).toBeInTheDocument());
    expect(screen.getByLabelText(/Start of week/)).toHaveValue("2026-07-20");
    expect(screen.getByLabelText(/End of week/)).toHaveValue("2026-07-26");
  });
});