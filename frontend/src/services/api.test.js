import {
  reviewCode,
  generateFix,
  getHealth,
} from "./api";


const originalFetch =
  global.fetch;


beforeEach(() => {
  global.fetch =
    jest.fn();

  global.fetch.mockResolvedValue({
    ok: true,

    json: jest.fn().mockResolvedValue({
      issues: [],
    }),
  });
});


afterEach(() => {
  global.fetch =
    originalFetch;
});


test("reviewCode sends multipart review request", async () => {
  const file = new File(
    ["print('hello')"],
    "main.py",
    {
      type: "text/x-python",
    }
  );

  const result =
    await reviewCode({
      files: [file],
      language: "Python",
      model: "gemini-2.5-flash",
    });

  expect(
    global.fetch
  ).toHaveBeenCalledTimes(1);

  const [
    url,
    options,
  ] = global.fetch.mock.calls[0];

  expect(url).toContain(
    "/review-code"
  );

  expect(
    options.method
  ).toBe("POST");

  expect(
    options.body
  ).toBeInstanceOf(FormData);

  expect(result).toEqual({
    issues: [],
  });
});


test("generateFix sends code and issues", async () => {
  global.fetch.mockResolvedValue({
    ok: true,

    json: jest.fn().mockResolvedValue({
      fixed_code:
        "print('fixed')",
    }),
  });

  const result =
    await generateFix({
      code: "print('broken')",
      language: "Python",
      issues: [],
      model: "gemini-2.5-flash",
    });

  expect(
    global.fetch
  ).toHaveBeenCalledTimes(1);

  const [
    url,
    options,
  ] = global.fetch.mock.calls[0];

  expect(url).toContain(
    "/fix-code"
  );

  expect(
    options.method
  ).toBe("POST");

  expect(
    options.headers["Content-Type"]
  ).toBe("application/json");

  expect(
    JSON.parse(options.body)
  ).toEqual({
    code: "print('broken')",
    language: "Python",
    issues: [],
    model: "gemini-2.5-flash",
    provider: "gemini",
  });

  expect(
    result.fixed_code
  ).toBe("print('fixed')");
});


test("getHealth returns API health status", async () => {
  global.fetch.mockResolvedValue({
    ok: true,

    json: jest.fn().mockResolvedValue({
      status: "ok",
    }),
  });

  const result =
    await getHealth();

  expect(
    global.fetch
  ).toHaveBeenCalledTimes(1);

  expect(result).toEqual({
    status: "ok",
  });
});


test("API errors are converted to useful messages", async () => {
  global.fetch.mockResolvedValue({
    ok: false,

    status: 502,

    json: jest.fn().mockResolvedValue({
      detail:
        "Code review failed.",
    }),
  });

  await expect(
    getHealth()
  ).rejects.toThrow(
    "Code review failed."
  );
});

test("reviewCode sends repository-relative file paths", async () => {
  const file = new File(
    ["print('hello')"],
    "main.py",
    {
      type: "text/x-python",
    }
  );

  Object.defineProperty(
    file,
    "webkitRelativePath",
    {
      value: "src/utils/main.py",
    }
  );

  await reviewCode({
    files: [file],
    language: "Python",
    model: "gemini-2.5-flash",
  });

  const [, options] =
    global.fetch.mock.calls[0];

  expect(
    options.body.getAll("file_paths")
  ).toEqual([
    "src/utils/main.py",
  ]);
});