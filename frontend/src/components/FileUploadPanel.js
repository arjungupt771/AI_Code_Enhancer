import React from "react";

export default function FileUploadPanel({
  dragActive,
  onDragOver,
  onDragLeave,
  onDrop,
  onBrowse,
  onSingleBrowse,
  fileInputRef,
  fileSingleRef,
  onFileChange,
  onSingleFileChange,
  invalidFiles,
  dismissInvalidFiles,
  onClear,
}) {
  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={`mb-3 p-6 rounded-lg border-2 ${
        dragActive
          ? "border-indigo-400 bg-indigo-50"
          : "border-dashed border-gray-300 bg-white"
      } flex flex-col items-center justify-center text-center transition`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-10 w-10 text-indigo-500"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 16V4m0 0L3 8m4-4 4 4m6 8v-8m0 0l4 4m-4-4-4 4"
        />
      </svg>

      <div className="mt-3 text-sm text-gray-700">
        Drag & drop your project folder here
      </div>

      <div className="mt-1 text-xs text-gray-500">
        or select a folder using the button below
      </div>

      <div className="mt-4 flex gap-2 items-center">
        <button
          onClick={onBrowse}
          className="px-4 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 text-white shadow-sm"
        >
          Browse folder
        </button>

        <button
          onClick={onSingleBrowse}
          className="px-4 py-2 rounded-full border border-gray-200 text-sm text-gray-700"
        >
          Add files
        </button>

        <button
          onClick={onClear}
          className="px-4 py-2 rounded-full border border-gray-200 text-sm text-red-600"
        >
          Clear
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        webkitdirectory="true"
        directory="true"
        multiple
        className="hidden"
        onChange={onFileChange}
      />

      <input
        ref={fileSingleRef}
        type="file"
        accept=".py,.js,.ts,.jsx,.tsx,.java,.c,.cpp,.json,.md,.rs,.go"
        multiple
        className="hidden"
        onChange={onSingleFileChange}
      />

      {invalidFiles.length > 0 && (
        <div className="mt-3 p-2 bg-red-50 text-red-800 rounded text-sm flex items-center justify-between gap-3">
          <div>
            <strong>
              Unsupported files:
            </strong>{" "}
            {invalidFiles.join(", ")}
          </div>

          <button
            onClick={dismissInvalidFiles}
            className="text-xs underline"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}