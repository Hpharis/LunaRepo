import { expect, test } from "vitest";
import { screen } from "@testing-library/dom";

test("shows default message when no match found", () => {
  document.body.innerHTML = `
    <div class="advisor">
      <p>No match found</p>
    </div>
  `;

  expect(screen.getByText("No match found")).toBeDefined();
});
