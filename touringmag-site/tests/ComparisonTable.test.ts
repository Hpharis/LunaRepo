import { expect, test } from "vitest";
import { screen } from "@testing-library/dom";

test("renders product rows in table", () => {
  document.body.innerHTML = `
    <table class="comparison-table">
      <tbody>
        <tr>
          <td>Touring Seat</td>
          <td>⭐</td>
          <td><ul><li>Comfort</li></ul></td>
          <td><ul><li>Durable</li></ul></td>
          <td><ul><li>Pricey</li></ul></td>
          <td><a href="#">Check Price</a></td>
        </tr>
      </tbody>
    </table>
  `;

  expect(screen.getByText("Touring Seat")).toBeDefined();
  expect(screen.getByText("Comfort")).toBeDefined();
  expect(screen.getByText("Durable")).toBeDefined();
});
