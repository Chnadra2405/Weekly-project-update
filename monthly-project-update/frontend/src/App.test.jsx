import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

afterEach(() => vi.restoreAllMocks());

async function completeForm(user) {
  await user.type(screen.getByLabelText(/Employee name/), "Ada Lovelace");
  await user.type(screen.getByLabelText(/Employee email/), "ada@example.com");
  fireEvent.change(screen.getByLabelText(/Reporting month/), { target: { value: "2026-07" } });
  await user.type(screen.getByLabelText(/Team \/ project/), "Platform");
  await user.type(screen.getByLabelText(/Achievements/), "Delivered reporting");
  await user.type(screen.getByLabelText(/Initiatives/), "Improve telemetry");
  await user.type(screen.getByLabelText(/Next week's plan/), "Measure adoption");
}

describe("App", () => {
  it("links validation errors to required fields", async () => {
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: "Submit update" }));
    const name = screen.getByLabelText(/Employee name/);
    expect(name).toHaveAttribute("aria-invalid", "true");
    expect(name).toHaveAccessibleDescription("This field is required.");
    expect(screen.getByRole("alert")).toHaveTextContent("Review the highlighted fields");
  });

  it("announces a sent result", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ id: "update-1", reporting_month: "2026-07", team_project: "Platform", delivery_status: "SENT", smtp_message_id: "<id@example.com>", attachments: [] }),
    });
    const user = userEvent.setup();
    render(<App />);
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Update sent"));
  });

  it("retains form values after an ambiguous transport failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Network unavailable"));
    const user = userEvent.setup();
    render(<App />);
    await completeForm(user);
    await user.click(screen.getByRole("button", { name: "Submit update" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Retry request" })).toBeInTheDocument());
    expect(screen.getByLabelText(/Employee name/)).toHaveValue("Ada Lovelace");
  });
});