import React from "react";

export default function FileList({
  fileList,
  files,
  activeFile,
  selectedFolder,
  fileContents,
  onSelectFile,
  onRemoveFile,
  onBrowse,
  onRemoveAll,
  formatBytes,
  getFileIcon,
}) {
  if (!fileList.length) {
    return null;
  }

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-gray-600">
          {selectedFolder
            ? `Folder: ${selectedFolder}`
            : "Selected files:"}

          <span className="ml-2 inline-block bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-xs">
            {fileList.length} files
          </span>
        </div>

        <div className="text-sm">
          <button
            onClick={onBrowse}
            className="text-sm text-indigo-600 underline mr-2"
          >
            Add more
          </button>

          <button
            onClick={onRemoveAll}
            className="text-sm text-red-600 underline"
          >
            Remove all
          </button>
        </div>
      </div>

      <div className="grid gap-2">
        {fileList.map((item) => {
          const sourceFile = files.find(
            (file) =>
              (
                file.webkitRelativePath ||
                file.name
              ) === item.path
          );

          const size =
            sourceFile?.size || 0;

          const isActive =
            activeFile === item.path;

          return (
            <div
              key={item.path}
              className={`flex items-center justify-between p-3 rounded-lg border ${
                isActive
                  ? "bg-indigo-50 border-indigo-200"
                  : "bg-white"
              } hover:shadow-sm transition`}
            >
              <div
                className="flex items-center gap-3 cursor-pointer min-w-0"
                onClick={() =>
                  onSelectFile(item.path)
                }
              >
                <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded bg-gray-100 text-lg font-semibold text-gray-700">
                  {getFileIcon(item.name)}
                </div>

                <div className="text-left min-w-0">
                  <div
                    className="text-sm font-medium truncate"
                    title={item.name}
                  >
                    {item.name}
                  </div>

                  <div
                    className="text-xs text-gray-500 truncate"
                    title={item.path}
                  >
                    {item.path}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-shrink-0">
                <div className="text-xs text-gray-500">
                  {formatBytes(size)}
                </div>

                <button
                  onClick={() =>
                    onRemoveFile(item.path)
                  }
                  className="text-sm text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}