import { render } from "@testing-library/react";
import axe from "axe-core";
import { expect, it } from "vitest";
import App from "./App";

it("has no automatic serious or critical accessibility violations", async () => {
  const { container } = render(<App />);
  const results = await axe.run(container, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] },
    rules: { "color-contrast": { enabled: false } },
  });
  const blocking = results.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
  expect(blocking).toEqual([]);
});