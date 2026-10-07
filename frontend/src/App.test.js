import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

test("renders the application homepage", () => {
  render(<App />);

  expect(
    screen.getByRole("heading", { name: /GENAI Code Reviewer/i })
  ).toBeTruthy();
});

test("navigates to the editor", () => {
  render(<App />);

  const openEditorButton = screen.getByRole("button", {
    name: /open code editor/i,
  });

  fireEvent.click(openEditorButton);

  expect(screen.getByText(/GENAI Code Reviewer/i)).toBeTruthy();
});