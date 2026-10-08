import React from "react";

export default function DependencySummary({
  dependencySummary,
}) {
  if (
    !dependencySummary ||
    !dependencySummary.total_dependencies
  ) {
    return null;
  }

  const dependencies =
    dependencySummary.dependencies || [];

  const dependencyTypes =
    dependencySummary.dependency_types || {};

  return (
    <section className="mb-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            📦 Dependencies
          </h2>

          <p className="text-sm text-gray-500">
            Dependencies detected from the repository manifests.
          </p>
        </div>

        <div className="rounded-lg bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
          {dependencySummary.total_dependencies}{" "}
          {dependencySummary.total_dependencies === 1
            ? "dependency"
            : "dependencies"}
        </div>
      </div>

      {dependencySummary.manifests?.length > 0 && (
        <div className="mt-4">
          <h3 className="mb-2 text-sm font-semibold text-gray-700">
            Manifest Files
          </h3>

          <div className="flex flex-wrap gap-2">
            {dependencySummary.manifests.map(
              (manifest) => (
                <span
                  key={manifest}
                  className="rounded-md bg-gray-100 px-3 py-1 text-xs text-gray-700"
                >
                  {manifest}
                </span>
              )
            )}
          </div>
        </div>
      )}

      {Object.keys(dependencyTypes).length > 0 && (
        <div className="mt-4">
          <h3 className="mb-2 text-sm font-semibold text-gray-700">
            Dependency Types
          </h3>

          <div className="flex flex-wrap gap-2">
            {Object.entries(
              dependencyTypes
            ).map(([type, count]) => (
              <span
                key={type}
                className="rounded-md bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700"
              >
                {type}: {count}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5 overflow-x-auto rounded-lg border border-gray-100">
        <table className="w-full min-w-[600px] text-left text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-4 py-3">
                Dependency
              </th>

              <th className="px-4 py-3">
                Version
              </th>

              <th className="px-4 py-3">
                Type
              </th>

              <th className="px-4 py-3">
                Manifest
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-100">
            {dependencies.map(
              (dependency, index) => (
                <tr
                  key={`${dependency.name}-${dependency.source_file}-${index}`}
                  className="hover:bg-gray-50"
                >
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {dependency.name}
                  </td>

                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    {dependency.version_spec ||
                      "unspecified"}
                  </td>

                  <td className="px-4 py-3">
                    <span className="rounded-md bg-gray-100 px-2 py-1 text-xs text-gray-700">
                      {dependency.dependency_type}
                    </span>
                  </td>

                  <td className="px-4 py-3 text-gray-600">
                    {dependency.source_file}
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}