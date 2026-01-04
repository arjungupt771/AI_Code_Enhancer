import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import Editor, { DiffEditor } from "@monaco-editor/react"; 

export default function CodeUploader() {
  const [files, setFiles] = useState([]);
  const [fileList, setFileList] = useState([]); // [{file, name, path}]
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [language, setLanguage] = useState("Python");
  const [reviewData, setReviewData] = useState([]);
  const [filter, setFilter] = useState("all");
  const [category, setCategory] = useState("all");
  const [code, setCode] = useState("");
  const [fixedCode, setFixedCode] = useState("");
  // store contents of uploaded files: { filename: content }
  const [fileContents, setFileContents] = useState({});
  const [activeFile, setActiveFile] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [applyingFix, setApplyingFix] = useState(false);
  const [showDiff, setShowDiff] = useState(false);
  const [model, setModel] = useState("gemini-pro");
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const count = reviewData.reduce((acc, item) => {
    acc[item.severity] = (acc[item.severity] || 0) + 1;
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {});
  const [loadingFix, setLoadingFix] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const fileSingleRef = useRef(null);
  const [invalidFiles, setInvalidFiles] = useState([]);

  const handleBrowse = () => fileInputRef.current && fileInputRef.current.click();
  const handleSingleBrowse = () => fileSingleRef.current && fileSingleRef.current.click();

  const allowedExtensions = ['py','js','ts','jsx','tsx','java','c','cpp','json','md','rs','go'];
  const isAllowedFile = (file) => {
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    return allowedExtensions.includes(ext);
  };

  // Ensure the file input has the webkitdirectory attribute set (some browsers need it explicitly)
  useEffect(() => {
    if (fileInputRef.current && !fileInputRef.current.hasAttribute('webkitdirectory')) {
      try {
        fileInputRef.current.setAttribute('webkitdirectory', '');
      } catch (e) {
        // ignore if not supported
      }
    }
  }, []);

  const handleSingleFileChange = (e) => {
    const selected = Array.from(e.target.files || []);
    const invalid = selected.filter((f) => !isAllowedFile(f));
    const valid = selected.filter((f) => isAllowedFile(f));

    if (invalid.length) {
      setInvalidFiles(invalid.map((f) => f.name));
      // clear the invalid file input so user can reselect
      e.target.value = null;
    }

    if (valid.length) {
      handleFiles(valid);
    }
  };

  const dismissInvalidFiles = () => setInvalidFiles([]);

  const formatBytes = (bytes, decimals = 2) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const [parsing, setParsing] = useState(false);
  const [parsingProgress, setParsingProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showConfirmRemoveAll, setShowConfirmRemoveAll] = useState(false);
  const [langOpen, setLangOpen] = useState(false);
  const langRef = useRef(null);

  const languages = [
    { key: 'Python', icon: '🐍' },
    { key: 'JavaScript', icon: '📜' },
    { key: 'Java', icon: '☕' },
    { key: 'C++', icon: '💠' },
  ];

  const handleSelectLanguage = (lang) => {
    setLanguage(lang);
    setLangOpen(false);
  };

  // Close language dropdown on outside click or Escape
  useEffect(() => {
    const onDocClick = (e) => {
      if (langRef.current && !langRef.current.contains(e.target)) setLangOpen(false);
    };
    const onKey = (e) => { if (e.key === 'Escape') setLangOpen(false); };
    document.addEventListener('click', onDocClick);
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('click', onDocClick); document.removeEventListener('keydown', onKey); };
  }, []);

  const reviewListRef = useRef(null);
  const viewFilteredIssues = () => {
    if (reviewListRef.current) reviewListRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const getFileIcon = (name) => {
    const ext = (name.split('.').pop() || '').toLowerCase();
    if (ext === 'py') return '🐍';
    if (ext === 'js' || ext === 'jsx') return '📜';
    if (ext === 'ts' || ext === 'tsx') return '🔷';
    if (ext === 'java') return '☕';
    if (ext === 'json') return '🧾';
    if (ext === 'md') return '📘';
    return '📄';
  };

  const handleFiles = async (fileListInput) => {
    try {
      console.debug('handleFiles called with', (fileListInput && fileListInput.length) || 0);
      const selectedFiles = Array.from(fileListInput || []);

      // Normalize file.webkitRelativePath if missing but fullPath exists on dropped File
      const normalized = selectedFiles.map((f) => {
        if (!f.webkitRelativePath && f.fullPath) {
          Object.defineProperty(f, 'webkitRelativePath', { value: f.fullPath, configurable: true });
        }
        return f;
      });

      setFiles(normalized);
      const fl = normalized.map((f) => ({ file: f, name: f.name, path: f.webkitRelativePath || f.name }));
      setFileList(fl);

      setParsing(true);
      setParsingProgress(0);

      const results = [];
      for (let i = 0; i < normalized.length; i++) {
        const f = normalized[i];
        const text = await f.text();
        const path = f.webkitRelativePath || f.name;
        results.push({ path, name: f.name, text });
        setParsingProgress(Math.round(((i + 1) / normalized.length) * 100));
      }

      const map = {};
      results.forEach((r) => (map[r.path] = r.text));
      setFileContents(map);

      if (results[0]) {
        setActiveFile(results[0].path);
        setCode(results[0].text);

        const firstPath = results[0].path;
        const root = firstPath.includes('/') ? firstPath.split('/')[0] : null;
        setSelectedFolder(root);
      } else {
        setActiveFile(null);
        setCode('');
        setSelectedFolder(null);
      }
    } catch (err) {
      console.error('Error reading files:', err);
    } finally {
      setParsing(false);
      setTimeout(() => setParsingProgress(0), 300);
    }
  };

  const onDragOver = (e) => { e.preventDefault(); e.stopPropagation(); setDragActive(true); };
  const onDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); setDragActive(false); };

  // rich drop handler: supports file drops and folder drops via webkit entries
  const onDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    // If DataTransferItemList is available, try to walk directories
    const items = e.dataTransfer && e.dataTransfer.items;
    if (items && items.length) {
      console.debug('Drop items count:', items.length);
      const files = [];

      const traverseEntry = (entry, path = '') => new Promise((resolve) => {
        if (!entry) return resolve();
        if (entry.isFile) {
          entry.file((file) => {
            // attach path for later
            Object.defineProperty(file, 'webkitRelativePath', {
              value: path + file.name,
              configurable: true,
              writable: true,
            });
            files.push(file);
            resolve();
          });
        } else if (entry.isDirectory) {
          const reader = entry.createReader();
          const read = () => {
            reader.readEntries(async (entries) => {
              if (!entries.length) return resolve();
              for (const ent of entries) {
                await traverseEntry(ent, path + entry.name + '/');
              }
              // read again in case of more entries
              read();
            });
          };
          read();
        } else {
          resolve();
        }
      });

      const promises = [];
      for (let i = 0; i < items.length; i++) {
        const it = items[i];
        if (it.kind === 'file' && it.webkitGetAsEntry) {
          const entry = it.webkitGetAsEntry();
          if (entry) promises.push(traverseEntry(entry));
        } else if (it.kind === 'file') {
          const f = it.getAsFile();
          if (f) files.push(f);
        }
      }

      await Promise.all(promises);
      console.debug('Resolved drop files:', files.length);
      if (files.length) {
        handleFiles(files);
        return;
      }
    }

    // Fallback to files (single files dropped)
    const fileList = e.dataTransfer && e.dataTransfer.files;
    if (fileList && fileList.length) {
      console.debug('Fallback drop files:', fileList.length);
      handleFiles(fileList);
      return;
    }

    console.debug('Drop had no files');
  };

  const removeFile = (path) => {
    const newFileList = fileList.filter(f => f.path !== path);
    setFileList(newFileList);
    const newFiles = files.filter(f => (f.webkitRelativePath || f.name) !== path);
    setFiles(newFiles);
    const newContents = { ...fileContents };
    delete newContents[path];
    setFileContents(newContents);
    if (activeFile === path) {
      if (newFileList[0]) {
        setActiveFile(newFileList[0].path);
        setCode(newContents[newFileList[0].path] || "");
      } else {
        setActiveFile(null);
        setCode("");
        setSelectedFolder(null);
      }
    }
  };


  const stats = reviewData.reduce(
    (acc, item) => {
      acc.total += 1;

      acc[item.severity] = (acc[item.severity] || 0) + 1;
      acc[item.category] = (acc[item.category] || 0) + 1;

      return acc;
    },
    {
      total: 0,
      error: 0,
      warning: 0,
      info: 0,
      security: 0,
      performance: 0,
      style: 0,
      bug: 0,
    }
  );


  // formData is built when submitting to avoid creating it on each render



  // Filter review items based on category or severity
  const filteredReview = reviewData.filter(item =>
    category === "all" ? true : item.category === category
  );

  // Add markers in Monaco Editor
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current || filteredReview.length === 0) return;

    const categoryColor = {
      security: monacoRef.current.MarkerSeverity.Error,
      performance: monacoRef.current.MarkerSeverity.Warning,
      style: monacoRef.current.MarkerSeverity.Info,
      bug: monacoRef.current.MarkerSeverity.Error,
    };

    const markers = filteredReview.map((item) => ({
      startLineNumber: item.line,
      endLineNumber: item.line,
      startColumn: 1,
      endColumn: 1,
      message: `${item.message}\n\n🤖 AI: ${item.explanation || ""}`,
      severity: categoryColor[item.category] || monacoRef.current.MarkerSeverity.Warning,
    }));

    monacoRef.current.editor.setModelMarkers(editorRef.current.getModel(), "ai-reviewer", markers);
  }, [filteredReview]);

  // Handle file upload (multi-file and directory support)
  const handleFileChange = (e) => handleFiles(e.target.files);

  // Handle submitting code for review
  const handleSubmit = async () => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("language", language);
    formData.append("model", model); // Gemini API model selection

    try {
      setUploading(true);
      setUploadProgress(0);
      const response = await axios.post("http://localhost:8000/review-code", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      });

      // Expect backend to return { issues: [...], fixedCode: "..." } or { issues: [...], fixed_code: "..." }
      setReviewData(response.data.issues || []);
      setFixedCode(response.data.fixedCode || response.data.fixed_code || "");
    } catch (err) {
      console.error("Error reviewing code:", err);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 300);
    }
  };

  // Apply fix for a single issue by calling the backend /fix-code endpoint with that issue
  const applyIssueFix = async (issue) => {
    setApplyingFix(true);
    try {
      const res = await axios.post("http://localhost:8000/fix-code", {
        code,
        language,
        issues: [issue],
      });

      setFixedCode(res.data.fixedCode || res.data.fixed_code || "");
      setShowDiff(true);
    } catch (err) {
      console.error("Error applying issue fix:", err);
    } finally {
      setApplyingFix(false);
    }
  };

  // Apply fixes for all detected issues (used by toolbar)
  const generateAllFixes = async () => {
    setLoadingFix(true);
    try {
      const res = await axios.post("http://localhost:8000/fix-code", {
        code,
        language,
        issues: filteredReview,
      });
      setFixedCode(res.data.fixedCode || res.data.fixed_code || "");
      setShowDiff(true);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFix(false);
    }
  };

  // Handle Monaco Editor mount
  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    monaco.languages.registerCodeActionProvider(language.toLowerCase(), {
      provideCodeActions: (model, range, context) => {
        const actions = context.markers.map((marker) => ({
          title: "Apply AI Fix",
          kind: "quickfix",
          edit: {
            edits: [
              {
                resource: model.uri,
                textEdit: {
                  range: marker,
                  text:
                    "// AI Suggested Fix\n" +
                    fixedCode
                      .split("\n")
                      .slice(marker.startLineNumber - 1, marker.endLineNumber)
                      .join("\n"),
                },
              },
            ],
          },
        }));
        return { actions, dispose: () => {} };
      },
    });

  };

  return (


    <div className="p-4">
        <div className="grid grid-cols-4 gap-3 mb-4">
            {/* <div className="bg-red-100 p-2 rounded">Errors: {count.error || 0}</div>
            <div className="bg-yellow-100 p-2 rounded">Warnings: {count.warning || 0}</div>
            <div className="bg-purple-100 p-2 rounded">Security: {count.security || 0}</div>
            <div className="bg-blue-100 p-2 rounded">Performance: {count.performance || 0}</div> */}
        </div>
      {/* File Upload */}
      
      {/* Selection summary */}
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-sm text-gray-600">
          {selectedFolder ? (
            <span>Selected folder: <strong>{selectedFolder}</strong></span>
          ) : (
            <span>No folder selected</span>
          )}
          {activeFile && (
            <span className="ml-3">| Active: <strong>{activeFile}</strong></span>
          )}
        </div>
        <div>
          <button
            onClick={() => {
              setFiles([]);
              setFileList([]);
              setFileContents({});
              setActiveFile(null);
              setCode("");
              setReviewData([]);
              setSelectedFolder(null);
            }}
            className="px-3 py-1 border rounded text-sm"
          >
            Clear selection
          </button>
        </div>
      </div>

      {parsing && (
        <div className="mb-3">
          <div className="text-sm text-gray-700">Parsing files: {parsingProgress}%</div>
          <div className="w-full bg-gray-200 rounded h-2 mt-2 overflow-hidden">
            <div className="h-2 bg-indigo-500" style={{ width: `${parsingProgress}%`, transition: 'width 150ms' }} />
          </div>
        </div>
      )}

      {uploading && (
        <div className="mb-3">
          <div className="text-sm text-gray-700">Uploading files: {uploadProgress}%</div>
          <div className="w-full bg-gray-200 rounded h-2 mt-2 overflow-hidden">
            <div className="h-2 bg-pink-500" style={{ width: `${uploadProgress}%`, transition: 'width 150ms' }} />
          </div>
        </div>
      )}

      {reviewData.length > 0 && (
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div  onClick={() => setFilter("error")} className="cursor-pointer bg-red-100 text-red-800 p-3 rounded hover:scale-105 transition">
            ❌ Errors: {stats.error}
          </div>
          <div  onClick={() => setFilter("warning")} className="cursor-pointer bg-yellow-100 text-yellow-800 p-3 rounded hover:scale-105 transition">
            ⚠️ Warnings: {stats.warning}
          </div>
          <div onClick={() => setFilter("security")} className="cursor-pointer bg-purple-100 text-purple-800 p-3 rounded hover:scale-105 transition">
            🔐 Security: {stats.security}
          </div>
          <div onClick={() => setFilter("performance")} className="cursor-pointer bg-purple-100 text-purple-800 p-3 rounded hover:scale-105 transition">
            🚀 Performance: {stats.performance}
          </div>
          <div onClick={() => setFilter("style")} className="cursor-pointer bg-purple-100 text-purple-800 p-3 rounded hover:scale-105 transition">
            🎨 Style: {stats.style}
          </div>
          <div onClick={() => setFilter("bug")} className="cursor-pointer bg-purple-100 text-purple-800 p-3 rounded hover:scale-105 transition">
            🐞 Bugs: {stats.bug}
          </div>
          <div onClick={() => setFilter("all")} className="cursor-pointer bg-purple-100 text-purple-800 p-3 rounded hover:scale-105 transition">
            📊 Total Issues: {stats.total}
          </div>
        </div>
      )}


      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`mb-3 p-6 rounded-lg border-2 ${dragActive ? 'border-indigo-400 bg-indigo-50' : 'border-dashed border-gray-300 bg-white'} flex flex-col items-center justify-center text-center transition`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4 4 4m6 8v-8m0 0l4 4m-4-4-4 4" />
        </svg>
        <div className="mt-3 text-sm text-gray-700">Drag & drop your project folder here</div>
        <div className="mt-1 text-xs text-gray-500">or select a folder using the button below</div>
        <div className="mt-2">
          <div className="flex items-center justify-center gap-1">
            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '75ms' }}></span>
            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '175ms' }}></span>
            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '275ms' }}></span>
          </div>
        </div>
        <div className="mt-4 flex gap-2 items-center">
          <button onClick={handleBrowse} className="px-4 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 text-white shadow-sm">Browse folder</button>
          <button onClick={handleSingleBrowse} className="px-4 py-2 rounded-full border border-gray-200 text-sm text-gray-700">Add files</button>
          <button onClick={() => { setFiles([]); setFileList([]); setFileContents({}); setActiveFile(null); setCode(''); setSelectedFolder(null); }} className="px-4 py-2 rounded-full border border-gray-200 text-sm text-red-600">Clear</button>
        </div>

        <input ref={fileInputRef} type="file" webkitdirectory="true" directory="true" multiple className="hidden" onChange={handleFileChange} />
        <input ref={fileSingleRef} type="file" accept=".py,.js,.ts,.jsx,.tsx,.java,.c,.cpp,.json,.md,.rs,.go" multiple className="hidden" onChange={handleSingleFileChange} />

        {invalidFiles.length > 0 && (
          <div className="mt-3 p-2 bg-red-50 text-red-800 rounded text-sm flex items-center justify-between">
            <div>
              <strong>Unsupported files:</strong> {invalidFiles.join(', ')}
            </div>
            <button onClick={dismissInvalidFiles} className="text-xs underline">Dismiss</button>
          </div>
        )}
      </div>

      {fileList.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-600">{selectedFolder ? `Folder: ${selectedFolder}` : "Selected files:"} <span className="ml-2 inline-block bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-xs">{fileList.length} files</span></div>
            <div className="text-sm">
              <button onClick={handleBrowse} className="text-sm text-indigo-600 underline mr-2">Add more</button>
              <button onClick={() => setShowConfirmRemoveAll(true)} className="text-sm text-red-600 underline">Remove all</button>
            </div>
          </div>

          <div className="grid gap-2">
            {fileList.map((f) => {
              const size = (files.find(ff => (ff.webkitRelativePath||ff.name)===f.path)?.size) || 0;
              return (
                <div key={f.path} className={`flex items-center justify-between p-3 rounded-lg border ${activeFile===f.path ? 'bg-indigo-50 border-indigo-200' : 'bg-white'} hover:shadow-sm transition`}>
                  <div className="flex items-center gap-3 cursor-pointer" onClick={() => { setActiveFile(f.path); setCode(fileContents[f.path]||''); }}>
                    <div className="w-10 h-10 flex items-center justify-center rounded bg-gray-100 text-lg font-semibold text-gray-700">{getFileIcon(f.name)}</div>
                    <div className="text-left">
                      <div className="text-sm font-medium truncate" title={f.name}>{f.name}</div>
                      <div className="text-xs text-gray-500 truncate" title={f.path}>{f.path}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-xs text-gray-500">{formatBytes(size)}</div>
                    <button onClick={() => removeFile(f.path)} className="text-sm text-red-500 hover:text-red-700">Remove</button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {showConfirmRemoveAll && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowConfirmRemoveAll(false)} />
          <div className="relative bg-white rounded-lg shadow-lg max-w-md w-full p-5 z-60">
            <div className="font-semibold text-lg">Remove all files?</div>
            <div className="mt-2 text-sm text-gray-600">This will clear all selected files and their contents from the uploader. This action cannot be undone.</div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setShowConfirmRemoveAll(false)} className="px-3 py-1 border rounded">Cancel</button>
              <button onClick={() => { setFiles([]); setFileList([]); setFileContents({}); setActiveFile(null); setCode(''); setSelectedFolder(null); setShowConfirmRemoveAll(false); }} className="px-3 py-1 bg-red-600 text-white rounded">Remove all</button>
            </div>
          </div>
        </div>
      )}

      {/* Category Filter */}
      <select
        className="w-full mb-3 border p-2 rounded"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
      >
        <option value="all">All</option>
        <option value="security">Security</option>
        <option value="performance">Performance</option>
        <option value="style">Style</option>
        <option value="bug">Bug</option>
      </select>

      {/* Model Switch */}
      <select
        className="w-full mb-3 border p-2 rounded"
        value={model}
        onChange={(e) => setModel(e.target.value)}
      >
        <option value="gpt-4">GPT-4</option>
        <option value="claude">Claude</option>
        <option value="gemini-flash">Gemini Flash</option>
        <option value="local">Local LLM</option>
        <option value="gemini-pro">Gemini Pro</option>
        
      </select>

      {/* Monaco Editor */}
      <div className="mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-white/80 backdrop-blur-md rounded-t-lg px-4 py-3 border border-white/30">
          <div className="flex items-center gap-4">
            <div className="text-sm font-medium truncate max-w-xs" title={activeFile || ''}>{activeFile || 'No file selected'}</div>
            <div className="flex items-center gap-2">
              <span title="Errors" className="inline-flex items-center gap-1 bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded">❌ {stats.error || 0}</span>
              <span title="Warnings" className="inline-flex items-center gap-1 bg-yellow-50 text-yellow-700 text-xs px-2 py-0.5 rounded">⚠️ {stats.warning || 0}</span>
              <span title="Security" className="inline-flex items-center gap-1 bg-purple-50 text-purple-700 text-xs px-2 py-0.5 rounded">🔐 {stats.security || 0}</span>
            </div>
          </div>

          <div className="mt-3 sm:mt-0 flex items-center gap-2">
            <div className="flex items-center gap-2 bg-white rounded-full border px-2 py-1">
              <label className="text-xs text-gray-500">Lang</label>
              <select value={language} onChange={(e)=>setLanguage(e.target.value)} className="text-sm outline-none bg-transparent">
                <option>Python</option>
                <option>JavaScript</option>
                <option>Java</option>
                <option>C++</option>
              </select>
            </div>

            <button onClick={handleSubmit} disabled={uploading} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 text-white font-semibold shadow-md hover:scale-[1.02] transition disabled:opacity-60">
              {uploading ? (<><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg> Uploading... {uploadProgress}%</>) : (<><svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 0 0 2 2h14"/><path strokeLinecap="round" strokeLinejoin="round" d="M16 3l-4 4-4-4"/><path strokeLinecap="round" strokeLinejoin="round" d="M12 7v10"/></svg> Review</>)}
            </button>

            <button onClick={generateAllFixes} disabled={loadingFix || uploading} className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-200 text-indigo-700 bg-white hover:bg-indigo-50 disabled:opacity-60">
              {loadingFix ? (<><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg> Applying</>) : (<><svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg> Generate Fixes</>)}
            </button>
          </div>
        </div>

        {filter !== 'all' && (
          <div className="mt-2 mb-3 px-3 py-2 rounded bg-gray-50 border border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">Filtering: <strong className="capitalize">{filter}</strong> ({filteredReview.length})</div>
            <div className="flex items-center gap-2">
              <button onClick={viewFilteredIssues} className="text-sm text-indigo-600 underline">View issues</button>
              <button onClick={() => setFilter('all')} className="text-sm text-gray-500">Clear</button>
            </div>
          </div>
        )}

        <div className="border border-white/10 rounded-b-lg overflow-hidden">
          {showDiff ? (
            <div>
              <DiffEditor
                height="420px"
                original={code}
                modified={fixedCode}
                language={language.toLowerCase()}
                options={{ readOnly: true }}
              />
              {!fixedCode && (
                <div className="mt-2 text-yellow-700">No AI fix available for this selection.</div>
              )}
            </div>
          ) : (
            <Editor
              height="420px"
              value={code}
              language={language.toLowerCase()}
              theme="vs-dark"
              onMount={handleEditorDidMount}
              onChange={(value) => setCode(value)}
            />
          )}
        </div>

        {showDiff && (
          <div className="mt-3 flex justify-end">
            <button
              onClick={() => {
                setCode(fixedCode);
                setShowDiff(false);
              }}
              className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-full hover:bg-green-700"
            >
              ✅ Apply Fix to Code
            </button>
          </div>
        )}
      </div>



      {/* Severity Filter Buttons */}
      <div className="flex gap-2 mb-3">
        <button onClick={() => setFilter("all")} className="px-3 py-1 border rounded">All</button>
        <button onClick={() => setFilter("error")} className="px-3 py-1 border rounded">Errors</button>
        <button onClick={() => setFilter("warning")} className="px-3 py-1 border rounded">Warnings</button>
      </div>



      {/* AI Fix Diff Button */}
      {showDiff && (
        <button
          onClick={() => {
            setCode(fixedCode);
            setShowDiff(false);
          }}
          className="w-full bg-green-600 text-white py-2 rounded mt-3 hover:bg-green-700"
        >
          ✅ Apply Fix to Code
        </button>
      )}


      {/* Review Output */}
      {/* Review Summary Dashboard */}
      {reviewData.length > 0 && (
        <div className="grid grid-cols-4 gap-3 mb-4 mt-4 p-2 bg-gray-100 rounded">
          <div>Errors: {count.error || 0}</div>
          <div>Warnings: {count.warning || 0}</div>
          <div>Security: {count.security || 0}</div>
          <div>Performance: {count.performance || 0}</div>
        </div>
      )}

      {/* Detailed Review Output */}
      {reviewData.length > 0 && (
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="p-2 bg-gray-100 rounded col-span-1" ref={reviewListRef}>
            {reviewData.map((item, idx) => {
              const isActive = selectedIssue === item;
              const severityClass = item.severity === 'error' ? 'bg-red-100 text-red-800' : item.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-700';
              const catColor = item.category === 'security' ? 'bg-purple-100 text-purple-800' : item.category === 'performance' ? 'bg-indigo-100 text-indigo-800' : item.category === 'style' ? 'bg-green-100 text-green-800' : item.category === 'bug' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-700';
              return (
                <div key={idx} className={`p-2 border-b cursor-pointer hover:bg-gray-50 ${isActive ? 'ring-2 ring-indigo-100 bg-white' : ''}`} onClick={() => {
                  setSelectedIssue(item);
                  if (editorRef.current && item.line) {
                    editorRef.current.revealLineInCenter(item.line);
                    editorRef.current.setPosition({ lineNumber: item.line, column: 1 });
                    editorRef.current.focus();
                  }
                }}>
                  <div className="flex items-start gap-3">
                    <div className={`text-xs px-2 py-0.5 rounded ${severityClass}`}>{item.severity}</div>
                    <div className={`text-xs px-2 py-0.5 rounded ${catColor}`}>{item.category}</div>
                    <div className="flex-1 text-sm">Line {item.line} - {item.message}</div>
                    <div className="text-sm text-gray-400">{item.score ? `${Math.round(item.score*100)}%` : ''}</div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Issue detail panel */}
          <div className="col-span-1">
            {selectedIssue ? (
              <div className="p-3 border rounded bg-white">
                <div className="font-bold">Issue details</div>
                <div className="text-sm text-gray-600 mt-1">Line: {selectedIssue.line}</div>
                <div className="text-sm text-gray-600">Category: {selectedIssue.category}</div>
                <div className="mt-2">{selectedIssue.message}</div>
                {selectedIssue.explanation && (
                  <div className="mt-2 text-sm text-gray-600">Explanation: {selectedIssue.explanation}</div>
                )}

                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => applyIssueFix(selectedIssue)}
                    className="px-3 py-1 bg-blue-600 text-white rounded"
                    disabled={applyingFix}
                  >
                    {applyingFix ? "Applying..." : "Apply Fix"}
                  </button>

                  <button
                    onClick={() => setShowDiff(true)}
                    className="px-3 py-1 border rounded"
                  >
                    Show AI Fix
                  </button>

                  <button
                    onClick={() => setSelectedIssue(null)}
                    className="px-3 py-1 border rounded"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-3 border rounded bg-white text-sm text-gray-600">Click an issue to see details and apply a suggested fix.</div>
            )}
          </div>
        </div>
      )} 
    </div>
  );
}
