import React from "react";

import {
  render,
  screen,
  fireEvent,
} from "@testing-library/react";

import ErrorBanner from "./ErrorBanner";


test("does not render without an error", () => {
  const { container } =
    render(
      <ErrorBanner message="" />
    );

  expect(
    container.firstChild
  ).toBeNull();
});


test("renders the error message", () => {
  render(
    <ErrorBanner
      message="Unable to review code."
    />
  );

  const alert =
    screen.getByRole("alert");

  expect(
    alert.textContent
  ).toContain(
    "Unable to review code."
  );
});


test("dismisses the error", () => {
  const onDismiss =
    jest.fn();

  render(
    <ErrorBanner
      message="Something failed."
      onDismiss={onDismiss}
    />
  );

  const button =
    screen.getByRole(
      "button",
      {
        name: /dismiss error/i,
      }
    );

  fireEvent.click(button);

  expect(
    onDismiss
  ).toHaveBeenCalledTimes(1);
});