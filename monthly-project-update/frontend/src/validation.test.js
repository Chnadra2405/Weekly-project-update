import { describe, expect, it } from "vitest";
import { MAX_FILE_BYTES, validateForm } from "./validation";

const valid = {
  employee_name: "Ada", employee_email: "ada@example.com", reporting_month: "2026-07", team_project: "Platform",
  achievements: "Delivered", initiatives: "Measure", next_weeks_plan: "Iterate",
};

describe("validateForm", () => {
  it("accepts a complete submission", () => {
    expect(validateForm(valid, { reference_email: null, image: null })).toEqual({});
  });

  it("rejects invalid file extensions and sizes", () => {
    const errors = validateForm(valid, {
      reference_email: new File(["x"], "mail.txt", { type: "text/plain" }),
      image: new File([new Uint8Array(MAX_FILE_BYTES + 1)], "chart.png", { type: "image/png" }),
    });
    expect(errors.reference_email).toMatch(/EML or MSG/);
    expect(errors.image).toMatch(/10 MiB/);
  });
});