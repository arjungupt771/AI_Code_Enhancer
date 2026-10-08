import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  generateFix,
  reviewCode,
  DEFAULT_MODEL,
  DEFAULT_GROQ_MODEL,
} from "../services/api";

const ALLOWED_EXTENSIONS = [
  "py",
  "js",
  "ts",
  "jsx",
  "tsx",
  "java",
  "c",
  "cpp",
  "json",
  "md",
  "rs",
  "go",
];

const PROVIDER_MODELS = {
  gemini: [
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
    { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
  ],
  groq: [
    { value: DEFAULT_GROQ_MODEL, label: "Groq openai/gpt-oss-120b" },
  ],
};

const LANGUAGES = [
  { key: "Python", icon: "🐍" },
  { key: "JavaScript", icon: "📜" },
  { key: "Java", icon: "☕" },
  { key: "C++", icon: "💠" },
];

export default function useCodeReview() {
  const [files, setFiles] = useState([]);
  const [fileList, setFileList] = useState([]);
  const [fileContents, setFileContents] = useState({});

  const [selectedFolder, setSelectedFolder] =
    useState(null);
  const [activeFile, setActiveFile] =
    useState(null);

  const [language, setLanguage] =
    useState("Python");
  const [provider, setProvider] = useState("gemini");
  const [model, setModel] =
    useState(DEFAULT_MODEL);

  const [code, setCode] = useState("");
  const [fixedCode, setFixedCode] =
    useState("");
  const [patch, setPatch] = useState("");
  const [patchStats, setPatchStats] = useState({ additions: 0, deletions: 0 });

  const [reviewData, setReviewData] =
    useState([]);

  // Phase 2.3: Code quality score
  const [qualityScore, setQualityScore] =
    useState(null);

  const [dependencySummary, setDependencySummary] =
  useState(null);

  const [architecture, setArchitecture] = useState(null);

  const [selectedIssue, setSelectedIssue] =
    useState(null);

  const [filter, setFilter] =
    useState("all");
  const [category, setCategory] =
    useState("all");

  const [parsing, setParsing] =
    useState(false);
  const [parsingProgress, setParsingProgress] =
    useState(0);

  const [uploading, setUploading] =
    useState(false);

  const [loadingFix, setLoadingFix] =
    useState(false);
  const [applyingFix, setApplyingFix] =
    useState(false);

  const [error, setError] =
    useState("");

  const [showDiff, setShowDiff] =
    useState(false);
  const [
    showConfirmRemoveAll,
    setShowConfirmRemoveAll,
  ] = useState(false);

  const [dragActive, setDragActive] =
    useState(false);
  const [invalidFiles, setInvalidFiles] =
    useState([]);

  const fileInputRef = useRef(null);
  const fileSingleRef = useRef(null);

  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  const isAllowedFile = useCallback(
    (file) => {
      const extension = (
        file.name.split(".").pop() || ""
      ).toLowerCase();

      return ALLOWED_EXTENSIONS.includes(
        extension
      );
    },
    []
  );

  const formatBytes = useCallback(
    (bytes, decimals = 2) => {
      if (!bytes) return "0 B";

      const sizes = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
      ];

      const k = 1024;

      const dm =
        decimals < 0 ? 0 : decimals;

      const i = Math.floor(
        Math.log(bytes) / Math.log(k)
      );

      return (
        parseFloat(
          (
            bytes /
            Math.pow(k, i)
          ).toFixed(dm)
        ) +
        " " +
        sizes[i]
      );
    },
    []
  );

  const getFileIcon = useCallback(
    (name) => {
      const ext = (
        name.split(".").pop() || ""
      ).toLowerCase();

      if (ext === "py") return "🐍";
      if (
        ext === "js" ||
        ext === "jsx"
      )
        return "📜";
      if (
        ext === "ts" ||
        ext === "tsx"
      )
        return "🔷";
      if (ext === "java") return "☕";
      if (ext === "json") return "🧾";
      if (ext === "md") return "📘";

      return "📄";
    },
    []
  );

  const handleFiles = useCallback(
    async (fileListInput) => {
      setError("");

      try {
        const selectedFiles =
          Array.from(
            fileListInput || []
          ).filter(isAllowedFile);

        if (!selectedFiles.length) {
          return;
        }

        const normalized =
          selectedFiles.map((file) => {
            if (
              !file.webkitRelativePath &&
              file.fullPath
            ) {
              Object.defineProperty(
                file,
                "webkitRelativePath",
                {
                  value:
                    file.fullPath,
                  configurable: true,
                }
              );
            }

            return file;
          });

        setFiles(normalized);

        const nextFileList =
          normalized.map((file) => ({
            file,
            name: file.name,
            path:
              file.webkitRelativePath ||
              file.name,
          }));

        setFileList(nextFileList);

        setParsing(true);
        setParsingProgress(0);

        const results = [];

        for (
          let i = 0;
          i < normalized.length;
          i++
        ) {
          const file = normalized[i];

          const text =
            await file.text();

          const path =
            file.webkitRelativePath ||
            file.name;

          results.push({
            path,
            name: file.name,
            text,
          });

          setParsingProgress(
            Math.round(
              ((i + 1) /
                normalized.length) *
                100
            )
          );
        }

        const contents = {};

        results.forEach((result) => {
          contents[result.path] =
            result.text;
        });

        setFileContents(contents);

        const first = results[0];

        if (first) {
          setActiveFile(first.path);
          setCode(first.text);

          const root =
            first.path.includes("/")
              ? first.path.split("/")[0]
              : null;

          setSelectedFolder(root);
        }
      } catch (error) {
        console.error(
          "Error reading files:",
          error
        );

        setError(
          error instanceof Error
            ? error.message
            : "Unable to read the selected files."
        );
      } finally {
        setParsing(false);

        setTimeout(
          () => setParsingProgress(0),
          300
        );
      }
    },
    [isAllowedFile]
  );

  const removeFile = useCallback(
    (path) => {
      const nextFileList =
        fileList.filter(
          (item) =>
            item.path !== path
        );

      const nextFiles = files.filter(
        (file) =>
          (
            file.webkitRelativePath ||
            file.name
          ) !== path
      );

      const nextContents = {
        ...fileContents,
      };

      delete nextContents[path];

      setFileList(nextFileList);
      setFiles(nextFiles);
      setFileContents(nextContents);

      if (activeFile === path) {
        const nextActive =
          nextFileList[0];

        if (nextActive) {
          setActiveFile(
            nextActive.path
          );

          setCode(
            nextContents[
              nextActive.path
            ] || ""
          );
        } else {
          setActiveFile(null);
          setCode("");
          setSelectedFolder(null);
        }
      }
    },
    [
      activeFile,
      fileContents,
      fileList,
      files,
    ]
  );

  const clearAll = useCallback(() => {
    setFiles([]);
    setFileList([]);
    setFileContents({});
    setActiveFile(null);
    setCode("");
    setFixedCode("");
    setPatch("");
    setPatchStats({ additions: 0, deletions: 0 });
    setReviewData([]);

    // Phase 2.3: clear quality score
    setQualityScore(null);
    setDependencySummary(null);
    setArchitecture(null);
    setSelectedIssue(null);
    setSelectedFolder(null);
    setShowDiff(false);
    setFilter("all");
    setCategory("all");
    setError("");
  }, []);

  const selectFile = useCallback(
    (path) => {
      setActiveFile(path);
      setCode(
        fileContents[path] || ""
      );
    },
    [fileContents]
  );

  const handleSingleFileChange =
    useCallback(
      (event) => {
        const selected =
          Array.from(
            event.target.files || []
          );

        const invalid =
          selected.filter(
            (file) =>
              !isAllowedFile(file)
          );

        const valid =
          selected.filter(
            isAllowedFile
          );

        if (invalid.length) {
          setInvalidFiles(
            invalid.map(
              (file) => file.name
            )
          );

          event.target.value = "";
        }

        if (valid.length) {
          handleFiles(valid);
        }
      },
      [handleFiles, isAllowedFile]
    );

  const handleSubmit =
    useCallback(async () => {
      if (!files.length) {
        setError(
          "Select at least one source file before starting a review."
        );

        return;
      }

      setError("");

      try {
        setUploading(true);

        const response =
          await reviewCode({
            files,
            language,
            model,
            provider,
          });

        // Phase 2.3:
        // Store quality score returned
        // by the backend.
        setQualityScore(
          response.quality_score ||
            null
        );

        setDependencySummary(
          response.dependency_summary || null
        );
        setArchitecture(
          response.architecture || null
        );

        setReviewData(
          response.issues || []
        );

        setFixedCode(
          response.fixedCode ||
            response.fixed_code ||
            ""
        );
        setPatch(response.patch || "");
        setPatchStats({
          additions: response.additions || 0,
          deletions: response.deletions || 0,
        });

        setSelectedIssue(null);
      } catch (error) {
        console.error(
          "Error reviewing code:",
          error
        );

        setError(
          error instanceof Error
            ? error.message
            : "Unable to review the selected code."
        );
      } finally {
        setUploading(false);
      }
    }, [
      files,
      language,
      model,
      provider,
    ]);

  const applyIssueFix =
    useCallback(
      async (issue) => {
        if (!code.trim()) {
          setError(
            "There is no source code available to fix."
          );

          return;
        }

        setError("");

        try {
          setApplyingFix(true);

          const response =
            await generateFix({
              code,
              language,
              issues: [issue],
              model,
              provider,
            });

          const generatedCode =
            response.fixedCode ||
            response.fixed_code ||
            "";

          if (!generatedCode.trim()) {
            throw new Error(
              "The AI did not return a valid code fix."
            );
          }

          setFixedCode(
            generatedCode
          );
          setPatch(response.patch || "");
          setPatchStats({
            additions: response.additions || 0,
            deletions: response.deletions || 0,
          });

          setShowDiff(true);
        } catch (error) {
          console.error(
            "Error applying fix:",
            error
          );

          setError(
            error instanceof Error
              ? error.message
              : "Unable to generate the selected fix."
          );
        } finally {
          setApplyingFix(false);
        }
      },
      [
        code,
        language,
        model,
        provider,
      ]
    );

  const stats = useMemo(
    () =>
      reviewData.reduce(
        (acc, item) => {
          acc.total += 1;

          acc[item.severity] =
            (acc[item.severity] || 0) +
            1;

          acc[item.category] =
            (acc[item.category] || 0) +
            1;

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
      ),
    [reviewData]
  );

  const filteredReview =
    useMemo(
      () =>
        reviewData.filter(
          (item) =>
            category === "all"
              ? true
              : item.category ===
                category
        ),
      [
        reviewData,
        category,
      ]
    );

  const filteredBySeverity =
    useMemo(() => {
      if (filter === "all") {
        return filteredReview;
      }

      return filteredReview.filter(
        (item) =>
          item.severity === filter
      );
    }, [
      filteredReview,
      filter,
    ]);

  const generateAllFixes =
    useCallback(async () => {
      if (!filteredReview.length) {
        setError(
          "There are no review issues to fix."
        );

        return;
      }

      if (!code.trim()) {
        setError(
          "There is no source code available to fix."
        );

        return;
      }

      setError("");

      try {
        setLoadingFix(true);

        const response =
          await generateFix({
            code,
            language,
            issues: filteredReview,
            model,
            provider,
          });

        const generatedCode =
          response.fixedCode ||
          response.fixed_code ||
          "";

        if (!generatedCode.trim()) {
          throw new Error(
            "The AI did not return a valid code fix."
          );
        }

        setFixedCode(
          generatedCode
        );
        setPatch(response.patch || "");
        setPatchStats({
          additions: response.additions || 0,
          deletions: response.deletions || 0,
        });

        setShowDiff(true);
      } catch (error) {
        console.error(
          "Error generating fixes:",
          error
        );

        setError(
          error instanceof Error
            ? error.message
            : "Unable to generate code fixes."
        );
      } finally {
        setLoadingFix(false);
      }
    }, [
      code,
      language,
      model,
      provider,
      filteredReview,
    ]);

  const handleEditorDidMount =
    useCallback(
      (editor, monaco) => {
        editorRef.current = editor;
        monacoRef.current = monaco;
      },
      []
    );

  useEffect(() => {
    if (
      !editorRef.current ||
      !monacoRef.current
    ) {
      return;
    }

    const model =
      editorRef.current.getModel();

    if (!model) return;

    const severityMap = {
      security:
        monacoRef.current.MarkerSeverity
          .Error,

      performance:
        monacoRef.current.MarkerSeverity
          .Warning,

      style:
        monacoRef.current.MarkerSeverity
          .Info,

      bug:
        monacoRef.current.MarkerSeverity
          .Error,
    };

    const markers =
      filteredReview
        .filter(
          (item) =>
            Number.isInteger(
              item.line
            )
        )
        .map((item) => ({
          startLineNumber: item.line,
          endLineNumber: item.line,
          startColumn: 1,
          endColumn: 1,

          message:
            `${item.message}\n\n` +
            `AI: ${
              item.explanation || ""
            }`,

          severity:
            severityMap[
              item.category
            ] ||
            monacoRef.current
              .MarkerSeverity
              .Warning,
        }));

    monacoRef.current.editor.setModelMarkers(
      model,
      "ai-reviewer",
      markers
    );

    return () => {
      if (
        monacoRef.current &&
        model
      ) {
        monacoRef.current.editor.setModelMarkers(
          model,
          "ai-reviewer",
          []
        );
      }
    };
  }, [filteredReview]);

  const handleProviderChange = useCallback((nextProvider) => {
    setProvider(nextProvider);
    const nextModels = PROVIDER_MODELS[nextProvider] || [];
    setModel(nextModels[0]?.value || DEFAULT_MODEL);
  }, []);

  const clearError = useCallback(() => {
    setError("");
  }, []);

  return {
    // constants
    languages: LANGUAGES,

    // files
    files,
    fileList,
    fileContents,
    activeFile,
    selectedFolder,
    invalidFiles,

    // editor
    code,
    fixedCode,
    patch,
    patchStats,
    editorRef,
    monacoRef,

    // review
    reviewData,
    filteredReview,
    filteredBySeverity,
    selectedIssue,
    stats,
    dependencySummary,
    architecture,

    // Phase 2.3
    qualityScore,

    // configuration
    language,
    provider,
    model,
    providerModels: PROVIDER_MODELS,
    category,
    filter,

    // loading
    parsing,
    parsingProgress,
    uploading,
    loadingFix,
    applyingFix,

    // error
    error,
    clearError,

    // UI
    dragActive,
    showDiff,
    showConfirmRemoveAll,

    // refs
    fileInputRef,
    fileSingleRef,

    // setters
    setLanguage,
    setModel,
    setProvider: handleProviderChange,
    setCategory,
    setFilter,
    setCode,
    setSelectedIssue,
    setShowDiff,
    setShowConfirmRemoveAll,
    setInvalidFiles,
    setDragActive,
    

    // actions
    handleFiles,
    handleSingleFileChange,
    handleSubmit,
    applyIssueFix,
    generateAllFixes,
    removeFile,
    clearAll,
    selectFile,
    handleEditorDidMount,

    // utilities
    isAllowedFile,
    formatBytes,
    getFileIcon,
  };
}