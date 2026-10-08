import React from "react";

import {
  render,
  screen,
} from "@testing-library/react";

import DependencySummary from "./DependencySummary";


test("renders repository dependency summary", () => {
  render(
    <DependencySummary
      dependencySummary={{
        manifests: [
          "package.json",
        ],
        dependencies: [
          {
            name: "react",
            version_spec: "^18.3.0",
            source_file: "package.json",
            dependency_type: "runtime",
          },
          {
            name: "jest",
            version_spec: "^29.0.0",
            source_file: "package.json",
            dependency_type: "development",
          },
        ],
        total_dependencies: 2,
        dependency_types: {
          runtime: 1,
          development: 1,
        },
      }}
    />
  );

  expect(
    screen.getByText("📦 Dependencies")
  ).toBeTruthy();

  expect(
    screen.getByText("2 dependencies")
  ).toBeTruthy();

  expect(screen.getAllByText("package.json").length).toBe(3);

  expect(
    screen.getByText("react")
  ).toBeTruthy();

  expect(
    screen.getByText("^18.3.0")
  ).toBeTruthy();

  expect(
    screen.getByText("jest")
  ).toBeTruthy();
});


test("does not render without dependencies", () => {
  const { container } = render(
    <DependencySummary
      dependencySummary={{
        manifests: [],
        dependencies: [],
        total_dependencies: 0,
        dependency_types: {},
      }}
    />
  );

  expect(
    container.firstChild
  ).toBeNull();
});