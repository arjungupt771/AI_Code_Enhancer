import React from "react";

export default function ReviewPanel({
  reviewData,
  filteredReview,
  selectedIssue,
  onSelectIssue,
  onApplyFix,
  onShowDiff,
  onCloseIssue,
  applyingFix,
  editorRef,
}) {
  if (!reviewData.length) {
    return null;
  }

  const severityClass = {
    error:
      "bg-red-100 text-red-800",
    warning:
      "bg-yellow-100 text-yellow-800",
    info:
      "bg-gray-100 text-gray-700",
  };

  const categoryClass = {
    security:
      "bg-purple-100 text-purple-800",
    performance:
      "bg-indigo-100 text-indigo-800",
    style:
      "bg-green-100 text-green-800",
    bug:
      "bg-red-100 text-red-800",
  };

  return (
    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="p-2 bg-gray-100 rounded">
        {filteredReview.length === 0 ? (
          <div className="p-4 text-sm text-gray-500">
            No issues match the selected filter.
          </div>
        ) : (
          filteredReview.map(
            (item, index) => {
              const isActive =
                selectedIssue === item;

              return (
                <div
                  key={`${item.line}-${index}`}
                  className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
                    isActive
                      ? "ring-2 ring-indigo-100 bg-white"
                      : ""
                  }`}
                  onClick={() => {
                    onSelectIssue(item);

                    if (
                      editorRef.current &&
                      item.line
                    ) {
                      editorRef.current.revealLineInCenter(
                        item.line
                      );

                      editorRef.current.setPosition(
                        {
                          lineNumber:
                            item.line,
                          column: 1,
                        }
                      );

                      editorRef.current.focus();
                    }
                  }}
                >
                  <div className="flex items-start gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        severityClass[
                          item.severity
                        ] ||
                        severityClass.info
                      }`}
                    >
                      {item.severity}
                    </span>

                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        categoryClass[
                          item.category
                        ] ||
                        "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {item.category}
                    </span>

                    <div className="flex-1 text-sm">
                      Line {item.line} —{" "}
                      {item.message}
                    </div>

                    {item.score !==
                      undefined &&
                      item.score !== null && (
                        <div className="text-sm text-gray-400">
                          {Math.round(
                            item.score * 100
                          )}
                          %
                        </div>
                      )}
                  </div>
                </div>
              );
            }
          )
        )}
      </div>

      <div>
        {selectedIssue ? (
          <div className="p-4 border rounded bg-white">
            <div className="font-bold">
              Issue details
            </div>

            <div className="text-sm text-gray-600 mt-2">
              Line:{" "}
              {selectedIssue.line}
            </div>

            <div className="text-sm text-gray-600">
              Severity:{" "}
              {selectedIssue.severity}
            </div>

            <div className="text-sm text-gray-600">
              Category:{" "}
              {selectedIssue.category}
            </div>

            <div className="mt-3">
              {selectedIssue.message}
            </div>

            {selectedIssue.explanation && (
              <div className="mt-3 text-sm text-gray-600">
                <strong>
                  Explanation:
                </strong>{" "}
                {selectedIssue.explanation}
              </div>
            )}

            <div className="flex flex-wrap gap-2 mt-4">
              <button
                onClick={() =>
                  onApplyFix(
                    selectedIssue
                  )
                }
                className="px-3 py-1 bg-blue-600 text-white rounded"
                disabled={applyingFix}
              >
                {applyingFix
                  ? "Applying..."
                  : "Apply Fix"}
              </button>

              <button
                onClick={onShowDiff}
                className="px-3 py-1 border rounded"
              >
                Show AI Fix
              </button>

              <button
                onClick={onCloseIssue}
                className="px-3 py-1 border rounded"
              >
                Close
              </button>
            </div>
          </div>
        ) : (
          <div className="p-4 border rounded bg-white text-sm text-gray-600">
            Click an issue to see its details
            and apply a suggested fix.
          </div>
        )}
      </div>
    </div>
  );
}