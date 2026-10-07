import React from "react";

export default function ErrorBanner({
  message,
  onDismiss,
}) {
  if (!message) {
    return null;
  }

  return (
    <div
      role="alert"
      className="mb-4 flex items-start justify-between gap-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800"
    >
      <div>
        <div className="font-semibold">
          Something went wrong
        </div>

        <div className="mt-1">
          {message}
        </div>
      </div>

      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-red-600 hover:text-red-800 font-medium"
          aria-label="Dismiss error"
        >
          ✕
        </button>
      )}
    </div>
  );
}