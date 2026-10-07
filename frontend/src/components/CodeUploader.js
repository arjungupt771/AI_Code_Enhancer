import React, {
  useEffect,
  useRef,
} from "react";

import useCodeReview from "../hooks/useCodeReview";

import ErrorBanner from "./ErrorBanner";
import FileUploadPanel from "./FileUploadPanel";
import FileList from "./FileList";
import ReviewSummary from "./ReviewSummary";
import CodeEditor from "./CodeEditor";
import ReviewPanel from "./ReviewPanel";


export default function CodeUploader() {
  const langRef = useRef(null);

  const {
    languages,

    error,
    clearError,

    files,
    fileList,
    fileContents,
    activeFile,
    selectedFolder,
    invalidFiles,

    code,
    fixedCode,
    editorRef,

    reviewData,
    filteredReview,
    filteredBySeverity,
    selectedIssue,
    stats,

    language,
    model,
    category,
    filter,

    parsing,
    parsingProgress,
    uploading,
    loadingFix,
    applyingFix,

    dragActive,
    showDiff,
    showConfirmRemoveAll,

    fileInputRef,
    fileSingleRef,

    setLanguage,
    setModel,
    setCategory,
    setFilter,
    setCode,
    setSelectedIssue,
    setShowDiff,
    setShowConfirmRemoveAll,
    setInvalidFiles,
    setDragActive,

    handleFiles,
    handleSingleFileChange,
    handleSubmit,
    applyIssueFix,
    generateAllFixes,
    removeFile,
    clearAll,
    selectFile,
    handleEditorDidMount,

    formatBytes,
    getFileIcon,
  } = useCodeReview();


  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setShowConfirmRemoveAll(false);
      }
    };

    document.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [
    setShowConfirmRemoveAll,
  ]);


  const handleBrowse = () => {
    fileInputRef.current?.click();
  };


  const handleSingleBrowse = () => {
    fileSingleRef.current?.click();
  };


  const handleFileChange = (event) => {
    handleFiles(event.target.files);
  };


  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(true);
  };


  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);
  };


  const handleDrop = async (event) => {
    event.preventDefault();
    event.stopPropagation();

    setDragActive(false);

    const items =
      event.dataTransfer?.items;

    if (
      items &&
      items.length
    ) {
      const droppedFiles = [];


      const traverseEntry =
        (entry, path = "") =>
          new Promise((resolve) => {
            if (!entry) {
              resolve();
              return;
            }

            if (entry.isFile) {
              entry.file((file) => {
                Object.defineProperty(
                  file,
                  "webkitRelativePath",
                  {
                    value:
                      path +
                      file.name,
                    configurable: true,
                    writable: true,
                  }
                );

                droppedFiles.push(
                  file
                );

                resolve();
              });

              return;
            }


            if (entry.isDirectory) {
              const reader =
                entry.createReader();

              const readEntries =
                () => {
                  reader.readEntries(
                    async (
                      entries
                    ) => {
                      if (
                        !entries.length
                      ) {
                        resolve();
                        return;
                      }

                      for (
                        const entryItem of
                        entries
                      ) {
                        await traverseEntry(
                          entryItem,
                          path +
                            entry.name +
                            "/"
                        );
                      }

                      readEntries();
                    }
                  );
                };

              readEntries();
              return;
            }

            resolve();
          });


      const promises = [];

      for (
        let i = 0;
        i < items.length;
        i++
      ) {
        const item = items[i];

        if (
          item.kind === "file" &&
          item.webkitGetAsEntry
        ) {
          const entry =
            item.webkitGetAsEntry();

          if (entry) {
            promises.push(
              traverseEntry(entry)
            );
          }
        }
      }

      await Promise.all(promises);

      if (droppedFiles.length) {
        await handleFiles(
          droppedFiles
        );

        return;
      }
    }


    const fallbackFiles =
      event.dataTransfer?.files;

    if (
      fallbackFiles &&
      fallbackFiles.length
    ) {
      await handleFiles(
        fallbackFiles
      );
    }
  };


  const handleApplyCurrentFix =
    () => {
      if (!fixedCode) return;

      setCode(fixedCode);
      setShowDiff(false);
    };


  return (
    <div className="p-4">

      <ErrorBanner
        message={error}
        onDismiss={clearError}
      />

      {/* Selection summary */}

      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-sm text-gray-600">
          {selectedFolder ? (
            <span>
              Selected folder:{" "}
              <strong>
                {selectedFolder}
              </strong>
            </span>
          ) : (
            <span>
              No folder selected
            </span>
          )}

          {activeFile && (
            <span className="ml-3">
              | Active:{" "}
              <strong>
                {activeFile}
              </strong>
            </span>
          )}
        </div>

        <button
          onClick={clearAll}
          className="px-3 py-1 border rounded text-sm"
        >
          Clear selection
        </button>
      </div>


      {/* Parsing progress */}

      {parsing && (
        <div className="mb-3">
          <div className="text-sm text-gray-700">
            Parsing files:{" "}
            {parsingProgress}%
          </div>

          <div className="w-full bg-gray-200 rounded h-2 mt-2 overflow-hidden">
            <div
              className="h-2 bg-indigo-500"
              style={{
                width: `${parsingProgress}%`,
                transition:
                  "width 150ms",
              }}
            />
          </div>
        </div>
      )}


      {/* Upload progress */}

      {uploading && (
        <div className="mb-3">
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <span className="inline-block h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />

            Reviewing selected code...
          </div>

          <div className="w-full bg-gray-200 rounded h-2 mt-2 overflow-hidden">
            <div className="h-2 w-1/2 bg-indigo-500 animate-pulse" />
          </div>
        </div>
      )}


      {/* Summary */}

      <ReviewSummary
        stats={stats}
        reviewData={reviewData}
        filter={filter}
        onFilterChange={setFilter}
      />


      {/* Upload */}

      <FileUploadPanel
        dragActive={dragActive}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onBrowse={handleBrowse}
        onSingleBrowse={
          handleSingleBrowse
        }
        fileInputRef={fileInputRef}
        fileSingleRef={fileSingleRef}
        onFileChange={
          handleFileChange
        }
        onSingleFileChange={
          handleSingleFileChange
        }
        invalidFiles={invalidFiles}
        dismissInvalidFiles={() =>
          setInvalidFiles([])
        }
        onClear={clearAll}
      />


      {/* File list */}

      <FileList
        fileList={fileList}
        files={files}
        activeFile={activeFile}
        selectedFolder={
          selectedFolder
        }
        fileContents={fileContents}
        onSelectFile={selectFile}
        onRemoveFile={removeFile}
        onBrowse={handleBrowse}
        onRemoveAll={() =>
          setShowConfirmRemoveAll(true)
        }
        formatBytes={formatBytes}
        getFileIcon={getFileIcon}
      />


      {/* Remove-all confirmation */}

      {showConfirmRemoveAll && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() =>
              setShowConfirmRemoveAll(
                false
              )
            }
          />

          <div className="relative bg-white rounded-lg shadow-lg max-w-md w-full p-5 z-60">
            <div className="font-semibold text-lg">
              Remove all files?
            </div>

            <div className="mt-2 text-sm text-gray-600">
              This will clear all selected
              files and their contents.
              This action cannot be
              undone.
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() =>
                  setShowConfirmRemoveAll(
                    false
                  )
                }
                className="px-3 py-1 border rounded"
              >
                Cancel
              </button>

              <button
                onClick={() => {
                  clearAll();

                  setShowConfirmRemoveAll(
                    false
                  );
                }}
                className="px-3 py-1 bg-red-600 text-white rounded"
              >
                Remove all
              </button>
            </div>
          </div>
        </div>
      )}


      {/* Filters */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
        <select
          className="w-full border p-2 rounded"
          value={category}
          onChange={(event) =>
            setCategory(
              event.target.value
            )
          }
        >
          <option value="all">
            All categories
          </option>

          <option value="security">
            Security
          </option>

          <option value="performance">
            Performance
          </option>

          <option value="style">
            Style
          </option>

          <option value="bug">
            Bug
          </option>
        </select>


        <div
          ref={langRef}
          className="flex items-center gap-2"
        >
          <select
            className="w-full border p-2 rounded"
            value={language}
            onChange={(event) =>
              setLanguage(
                event.target.value
              )
            }
          >
            {languages.map(
              (item) => (
                <option
                  key={item.key}
                  value={item.key}
                >
                  {item.icon}{" "}
                  {item.key}
                </option>
              )
            )}
          </select>
        </div>
      </div>


      {/* Model */}

      <select
        className="w-full mb-3 border p-2 rounded"
        value={model}
        onChange={(event) =>
          setModel(event.target.value)
        }
      >
        <option value="gemini-2.5-flash">
          Gemini 2.5 Flash
        </option>

        <option value="gemini-2.5-pro">
          Gemini 2.5 Pro
        </option>
      </select>


      {/* Editor header */}

      <div className="mb-4">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-white/80 backdrop-blur-md rounded-t-lg px-4 py-3 border border-white/30">

          <div className="flex items-center gap-4">
            <div
              className="text-sm font-medium truncate max-w-xs"
              title={
                activeFile || ""
              }
            >
              {activeFile ||
                "No file selected"}
            </div>

            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded">
                ❌{" "}
                {stats.error || 0}
              </span>

              <span className="inline-flex items-center gap-1 bg-yellow-50 text-yellow-700 text-xs px-2 py-0.5 rounded">
                ⚠️{" "}
                {stats.warning ||
                  0}
              </span>

              <span className="inline-flex items-center gap-1 bg-purple-50 text-purple-700 text-xs px-2 py-0.5 rounded">
                🔐{" "}
                {stats.security ||
                  0}
              </span>
            </div>
          </div>


          <div className="mt-3 sm:mt-0 flex items-center gap-2">

            <button
              onClick={handleSubmit}
              disabled={
                uploading ||
                !files.length
              }
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 text-white font-semibold shadow-md hover:scale-[1.02] transition disabled:opacity-60"
            >
              {uploading
                ? "Reviewing..."
                : "🔍 Review"}
            </button>


            <button
              onClick={
                generateAllFixes
              }
              disabled={
                loadingFix ||
                uploading ||
                !filteredReview.length
              }
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-200 text-indigo-700 bg-white hover:bg-indigo-50 disabled:opacity-60"
            >
              {loadingFix
                ? "Applying..."
                : "✨ Generate Fixes"}
            </button>

          </div>
        </div>


        {filter !== "all" && (
          <div className="mt-2 mb-3 px-3 py-2 rounded bg-gray-50 border border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Filtering:{" "}
              <strong className="capitalize">
                {filter}
              </strong>{" "}
              (
              {
                filteredBySeverity.length
              }
              )
            </div>

            <button
              onClick={() =>
                setFilter("all")
              }
              className="text-sm text-gray-500"
            >
              Clear
            </button>
          </div>
        )}


        <CodeEditor
          code={code}
          fixedCode={fixedCode}
          language={language}
          showDiff={showDiff}
          onCodeChange={setCode}
          onEditorMount={
            handleEditorDidMount
          }
          onApplyFix={
            handleApplyCurrentFix
          }
        />

      </div>


      {/* Severity filters */}

      <div className="flex flex-wrap gap-2 mb-3">
        {[
          ["all", "All"],
          ["error", "Errors"],
          ["warning", "Warnings"],
          ["info", "Info"],
        ].map(
          ([key, label]) => (
            <button
              key={key}
              onClick={() =>
                setFilter(key)
              }
              className={`px-3 py-1 border rounded ${
                filter === key
                  ? "bg-indigo-50 border-indigo-300"
                  : ""
              }`}
            >
              {label}
            </button>
          )
        )}
      </div>


      {/* Review results */}

      <ReviewPanel
        reviewData={reviewData}
        filteredReview={
          filteredBySeverity
        }
        selectedIssue={
          selectedIssue
        }
        onSelectIssue={
          setSelectedIssue
        }
        onApplyFix={
          applyIssueFix
        }
        onShowDiff={() =>
          setShowDiff(true)
        }
        onCloseIssue={() =>
          setSelectedIssue(null)
        }
        applyingFix={
          applyingFix
        }
        editorRef={editorRef}
      />

    </div>
  );
}