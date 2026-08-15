import { describe, expect, it } from "vitest";
import { endOfWeek, validateForm } from "./validation";

const valid = {
  start_of_week: "2026-07-20", end_of_week: "2026-07-26", team_project: "Platform",
  achievements: "Delivered", initiatives: "Measure", next_weeks_plan: "Iterate",
};

describe("validateForm", () => {
  it("accepts a complete submission", () => {
    expect(validateForm(valid)).toEqual({});
  });

  it("derives a seven-day inclusive week", () => {
    expect(endOfWeek("2026-07-20")).toBe("2026-07-26");
  });

  it("rejects any other end date", () => {
    const errors = validateForm({ ...valid, end_of_week: "2026-07-27" });
    expect(errors.end_of_week).toMatch(/six days after/);
  });
});