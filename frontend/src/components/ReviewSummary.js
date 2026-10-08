import React from "react";

export default function ReviewSummary({
  stats,
  reviewData,
  qualityScore,
  filter,
  onFilterChange,
}) {
  if (!reviewData.length) {
    return null;
  }

  const cards = [
    {
      key: "error",
      label: "Errors",
      icon: "❌",
      className:
        "bg-red-100 text-red-800",
    },
    {
      key: "warning",
      label: "Warnings",
      icon: "⚠️",
      className:
        "bg-yellow-100 text-yellow-800",
    },
    {
      key: "security",
      label: "Security",
      icon: "🔐",
      className:
        "bg-purple-100 text-purple-800",
    },
    {
      key: "performance",
      label: "Performance",
      icon: "🚀",
      className:
        "bg-indigo-100 text-indigo-800",
    },
    {
      key: "style",
      label: "Style",
      icon: "🎨",
      className:
        "bg-green-100 text-green-800",
    },
    {
      key: "bug",
      label: "Bugs",
      icon: "🐞",
      className:
        "bg-red-100 text-red-800",
    },
    {
      key: "all",
      label: "Total Issues",
      icon: "📊",
      className:
        "bg-gray-100 text-gray-800",
    },
  ];

  return (
    <div className="mb-4">
      {qualityScore && (
        <div className="mb-4 rounded-xl border border-indigo-100 bg-gradient-to-r from-indigo-50 to-purple-50 p-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-sm font-medium text-gray-600">
                Code Quality Score
              </div>

              <div className="mt-1 text-sm text-gray-500">
                Based on severity and category of detected issues
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-4xl font-bold text-indigo-700">
                {qualityScore.overall}
              </div>

              <div className="text-sm text-gray-500">
                / 100
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {cards.map((card) => {
          const value =
            card.key === "all"
              ? stats.total
              : stats[card.key] || 0;

          const active =
            filter === card.key;

          return (
            <button
              key={card.key}
              onClick={() =>
                onFilterChange(card.key)
              }
              className={`rounded p-3 text-left transition hover:scale-[1.02] ${
                card.className
              } ${
                active
                  ? "ring-2 ring-indigo-400"
                  : ""
              }`}
            >
              {card.icon} {card.label}:{" "}
              <strong>{value}</strong>
            </button>
          );
        })}
      </div>
    </div>
  );
}