import React from "react";
import Editor, {
  DiffEditor,
} from "@monaco-editor/react";

export default function CodeEditor({
  code,
  fixedCode,
  language,
  showDiff,
  patch,
  patchStats,
  onCodeChange,
  onEditorMount,
  onApplyFix,
}) {
  return (
    <div className="border border-white/10 rounded-b-lg overflow-hidden">
      {showDiff ? (
        <div>
          <DiffEditor
            height="420px"
            original={code}
            modified={fixedCode}
            language={language.toLowerCase()}
            options={{
              readOnly: true,
            }}
          />

          {!fixedCode && (
            <div className="mt-2 text-yellow-700">
              No AI fix available for this selection.
            </div>
          )}

          {fixedCode && (
            <div className="p-3 bg-white border-t">
              <div className="flex items-center justify-between gap-3 mb-3 text-sm text-gray-600">
                <span>Unified patch: {patch ? "generated" : "not available"}</span>
                <span>+{patchStats.additions} additions · -{patchStats.deletions} deletions</span>
              </div>
              <div className="flex justify-end">
              <button
                onClick={onApplyFix}
                className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-full hover:bg-green-700"
              >
                ✅ Apply Fix to Code
              </button>
              </div>
              {patch && (
                <details className="mt-3">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700">View unified patch</summary>
                  <pre className="mt-2 max-h-48 overflow-auto rounded bg-gray-950 p-3 text-xs text-gray-100 whitespace-pre-wrap">{patch}</pre>
                </details>
              )}
            </div>
          )}
        </div>
      ) : (
        <Editor
          height="420px"
          value={code}
          language={language.toLowerCase()}
          theme="vs-dark"
          onMount={onEditorMount}
          onChange={(value) =>
            onCodeChange(value || "")
          }
        />
      )}
    </div>
  );
}