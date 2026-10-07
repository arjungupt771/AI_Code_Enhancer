const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ||
  "http://127.0.0.1:8000";

const DEFAULT_MODEL =
  process.env.REACT_APP_DEFAULT_MODEL ||
  "gemini-2.5-flash";


async function parseResponse(response) {
  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail =
      data &&
      typeof data.detail === "string"
        ? data.detail
        : `Request failed with status ${response.status}.`;

    throw new Error(detail);
  }

  return data;
}


export async function reviewCode({
  files,
  language,
  model,
  onUploadProgress,
}) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append(
    "language",
    language
  );

  formData.append(
    "model",
    model || DEFAULT_MODEL
  );

  /*
   * fetch() does not provide upload progress.
   *
   * Keep the callback in the API contract so the
   * component doesn't need to change if we later
   * introduce a progress-capable transport.
   */
  if (onUploadProgress) {
    onUploadProgress({
      loaded: 0,
      total: 0,
    });
  }

  const response = await fetch(
    `${API_BASE_URL}/review-code`,
    {
      method: "POST",
      body: formData,
    }
  );

  const data =
    await parseResponse(response);

  if (onUploadProgress) {
    onUploadProgress({
      loaded: 1,
      total: 1,
    });
  }

  return data;
}


export async function generateFix({
  code,
  language,
  issues,
  model,
}) {
  const response = await fetch(
    `${API_BASE_URL}/fix-code`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        code,
        language,
        issues,
        model: model || DEFAULT_MODEL,
      }),
    }
  );

  return parseResponse(response);
}


export async function getHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  return parseResponse(response);
}


export {
  API_BASE_URL,
  DEFAULT_MODEL,
};