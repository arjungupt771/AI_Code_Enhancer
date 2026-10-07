import React, {
  useState,
} from "react";

import CodeUploader from "./components/CodeUploader";
import Homepage from "./components/Homepage";
import AppErrorBoundary from "./components/AppErrorBoundary";


function App() {
  const [route, setRoute] =
    useState("home");

  return (
    <AppErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {route === "home" ? (
          <Homepage
            onStart={() =>
              setRoute("editor")
            }
          />
        ) : (
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold">
                GENAI Code Reviewer
              </h1>

              <button
                onClick={() =>
                  setRoute("home")
                }
                className="px-3 py-1 border rounded hover:bg-gray-50"
              >
                Home
              </button>
            </div>

            <CodeUploader />
          </div>
        )}
      </div>
    </AppErrorBoundary>
  );
}

export default App;
