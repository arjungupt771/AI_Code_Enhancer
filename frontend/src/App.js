import React, { useState } from "react";
import CodeUploader from "./components/CodeUploader";
import Homepage from "./components/Homepage";

function App() {
  const [route, setRoute] = useState("home");

  return (
    <div className="min-h-screen bg-gray-50">
      {route === "home" ? (
        <Homepage onStart={() => setRoute("editor")} />
      ) : (
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">GENAI Code Reviewer</h1>
            <div>
              <button onClick={() => setRoute("home")} className="mr-2 px-3 py-1 border rounded">Home</button>
            </div>
          </div>

          <CodeUploader />
        </div>
      )}
    </div>
  );
}

export default App;
