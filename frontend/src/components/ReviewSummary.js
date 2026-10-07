import React from "react";

export default function ReviewSummary({
  stats,
  reviewData,
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
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
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
            className={`text-left p-3 rounded transition hover:scale-[1.02] ${
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
  );
}