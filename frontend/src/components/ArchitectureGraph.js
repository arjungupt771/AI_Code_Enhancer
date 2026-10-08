import React from "react";

export default function ArchitectureGraph({
  architecture,
}) {
  if (!architecture) {
    return null;
  }

  const {
    nodes = [],
    edges = [],
    cycles = [],
    total_nodes = 0,
    total_edges = 0,
    cycle_count = 0,
  } = architecture;

  return (
    <section className="mt-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            🏗️ Architecture Overview
          </h2>

          <p className="text-sm text-gray-500">
            Static dependency relationships detected across the repository.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 text-sm">
          <span className="rounded-lg bg-blue-50 px-3 py-1 text-blue-700">
            Nodes: <strong>{total_nodes}</strong>
          </span>

          <span className="rounded-lg bg-indigo-50 px-3 py-1 text-indigo-700">
            Edges: <strong>{total_edges}</strong>
          </span>

          <span
            className={`rounded-lg px-3 py-1 ${
              cycle_count > 0
                ? "bg-red-50 text-red-700"
                : "bg-green-50 text-green-700"
            }`}
          >
            Cycles: <strong>{cycle_count}</strong>
          </span>
        </div>
      </div>

      {cycle_count > 0 && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="font-medium text-red-800">
            🔄 Circular dependencies detected
          </div>

          <div className="mt-2 space-y-1 text-sm text-red-700">
            {cycles.map((cycle, index) => (
              <div key={index}>
                {cycle.join(" → ")}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
          <h3 className="mb-3 font-medium text-gray-800">
            Files
          </h3>

          {nodes.length ? (
            <div className="max-h-72 space-y-2 overflow-y-auto">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  className="rounded-md border border-gray-200 bg-white px-3 py-2"
                >
                  <div className="font-medium text-gray-800">
                    {node.label}
                  </div>

                  {node.path && (
                    <div className="mt-1 break-all text-xs text-gray-500">
                      {node.path}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              No architecture nodes detected.
            </p>
          )}
        </div>

        <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
          <h3 className="mb-3 font-medium text-gray-800">
            Import Relationships
          </h3>

          {edges.length ? (
            <div className="max-h-72 space-y-2 overflow-y-auto">
              {edges.map((edge, index) => (
                <div
                  key={`${edge.source}-${edge.target}-${index}`}
                  className="rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                >
                  <div className="break-all font-medium text-gray-800">
                    {edge.source}
                  </div>

                  <div className="py-1 text-gray-400">
                    ↓ {edge.edge_type}
                  </div>

                  <div className="break-all text-gray-700">
                    {edge.target}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              No internal dependency relationships detected.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}