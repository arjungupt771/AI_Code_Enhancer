import React from "react";
import Editor, {
  DiffEditor,
} from "@monaco-editor/react";

export default function CodeEditor({
  code,
  fixedCode,
  language,
  showDiff,
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
            <div className="p-3 flex justify-end bg-white">
              <button
                onClick={onApplyFix}
                className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-full hover:bg-green-700"
              >
                ✅ Apply Fix to Code
              </button>
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