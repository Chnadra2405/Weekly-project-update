import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchProjectUpdates, updateProjectUpdate } from "../api";
import ReportsPage from "./ReportsPage";

vi.mock("./RichTextEditor", () => ({
  default: ({ id, value, onChange, disabled }) => (
    <textarea
      id={id}
      value={value || ""}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    />
  ),
}));

vi.mock("../api", () => ({
  fetchProjectUpdates: vi.fn(),
  updateProjectUpdate: vi.fn(),
}));

const owner = { id: "user-1", username: "employee", role: "EMPLOYEE" };
const report = {
  id: "report-1",
  user_id: owner.id,
  owner_username: owner.username,
  start_of_week: "2026-08-03",
  end_of_week: "2026-08-09",
  team_project: "CustAppIS",
  achievements: "Delivered authentication",
  initiatives: "Improved reporting",
  next_weeks_plan: "Release the dashboard",
  created_at: "2026-08-09T10:00:00Z",
  updated_at: "2026-08-09T10:00:00Z",
};

beforeEach(() => {
  vi.clearAllMocks();
  fetchProjectUpdates.mockResolvedValue([report]);
});

describe("ReportsPage", () => {
  it("allows the report owner to edit and save their report", async () => {
    const user = userEvent.setup();
    updateProjectUpdate.mockResolvedValue({ ...report, achievements: "Delivered the report page" });

    render(<ReportsPage auth={owner} />);

    await screen.findByText("Delivered authentication");
    await user.click(screen.getByRole("button", { name: "Edit report for 03 Aug 2026" }));
    const achievements = screen.getByLabelText("Achievements");
    await user.clear(achievements);
    await user.type(achievements, "Delivered the report page");
    await user.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() => expect(updateProjectUpdate).toHaveBeenCalledWith(
      report.id,
      expect.objectContaining({ achievements: "Delivered the report page" }),
    ));
    expect(await screen.findByText("Delivered the report page")).toBeInTheDocument();
  });

  it("does not offer edit controls for another user's report", async () => {
    render(<ReportsPage auth={{ id: "manager-1", username: "manager", role: "MANAGER" }} />);

    await screen.findByText("Delivered authentication");
    expect(screen.queryByRole("button", { name: /Edit report/ })).not.toBeInTheDocument();
  });
});
