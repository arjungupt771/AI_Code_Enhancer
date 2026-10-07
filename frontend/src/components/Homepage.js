import React from 'react';

export default function Homepage({ onStart }) {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-pink-50 overflow-hidden">
      {/* Decorative blobs */}
      <svg className="absolute -left-10 -top-10 w-72 opacity-20 transform rotate-12 text-indigo-400" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <defs>
          <linearGradient id="g1" x1="0%" x2="100%">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
        <path fill="url(#g1)" d="M43.7,-66.8C56.6,-55.1,67.3,-44.5,72.7,-31.5C78.1,-18.5,78.3,-3.2,74.2,11.2C70,25.5,61.4,38.9,50.1,48.8C38.8,58.6,24.9,64.9,9.7,71.1C-5.5,77.3,-21.1,83.6,-34.9,78C-48.7,72.4,-60.8,54.9,-66.8,36.2C-72.9,17.5,-72.9,-2.4,-66.4,-20.4C-59.9,-38.4,-46.9,-54.5,-31.2,-66.8C-15.5,-79,1.6,-87.4,18.3,-85.4C35,-83.3,51.1,-70.4,43.7,-66.8Z" transform="translate(100 100)" />
      </svg>

      <svg className="absolute right-0 bottom-0 w-96 opacity-15 transform -translate-y-10 text-pink-400" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <path fill="#fb7185" d="M39.6,-58.2C51.8,-48.1,62.2,-36.1,66.3,-22.7C70.4,-9.4,68.2,5.6,61.9,19.5C55.6,33.4,45.1,46.0,32.1,55.0C19.1,64.0,3.6,69.4,-11.6,71.1C-26.9,72.7,-42.8,70.7,-54.6,61.2C-66.4,51.7,-74.0,34.6,-78.8,16.4C-83.6,-1.9,-85.7,-21.3,-78.5,-34C-71.3,-46.8,-54.8,-52.8,-39.4,-61.1C-24,-69.4,-12,-80.1,0.3,-80.1C12.6,-80.1,25.1,-69.9,39.6,-58.2Z" transform="translate(100 100)" />
      </svg>

      <div className="relative z-10 container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/40 p-8 lg:flex lg:items-center lg:gap-8">
          <div className="lg:w-1/2 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 mb-4">
              <span className="text-xs font-semibold bg-gradient-to-r from-indigo-600 to-pink-500 text-white px-2 py-1 rounded-full">AI-powered</span>
              <span className="text-xs text-gray-500">Beta</span>
            </div>
            <h1 className="text-4xl sm:text-5xl font-extrabold leading-tight mb-4">
              <span className="bg-gradient-to-r from-indigo-600 to-pink-500 bg-clip-text text-transparent">GENAI</span>
              <span className="ml-2">Code Reviewer</span>
            </h1>
            <p className="text-gray-700 mb-6">Upload your project and get instant, contextual code reviews and one-click fixes — focusing on style, bugs, and security so you can ship safer.</p>

            <div className="flex flex-col sm:flex-row items-center gap-3 sm:justify-start">
              <button
                onClick={onStart}
                className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 text-white font-medium shadow-lg transform transition hover:-translate-y-0.5 active:scale-95"
                aria-label="Open Code Editor"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Open Code Editor
              </button>

              <a
                href="https://github.com/arjungupt771/AI_Code_Enhancer"
                target="_blank"
                rel="noreferrer"
                className="px-5 py-3 rounded-full border border-gray-200 text-gray-700 hover:bg-gray-50"
              >
                View Repository
              </a>
            </div>

            <div className="mt-6 text-sm text-gray-500">Tip: Upload a folder from the file picker to load an entire project at once.</div>
          </div>

          <div className="mt-8 lg:mt-0 lg:w-1/2">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-gradient-to-br from-white to-gray-50 border border-transparent hover:shadow-lg transform transition hover:-translate-y-1">
                <div className="text-3xl">⚡</div>
                <div className="mt-2 font-semibold">Fast reviews</div>
                <div className="text-sm text-gray-600">Quick suggestions for style, bugs & security.</div>
              </div>
              <div className="p-4 rounded-xl bg-gradient-to-br from-white to-gray-50 border border-transparent hover:shadow-lg transform transition hover:-translate-y-1">
                <div className="text-3xl">🛠️</div>
                <div className="mt-2 font-semibold">One-click fixes</div>
                <div className="text-sm text-gray-600">Apply fixes and inspect diffs before merging.</div>
              </div>
              <div className="p-4 rounded-xl bg-gradient-to-br from-white to-gray-50 border border-transparent hover:shadow-lg transform transition hover:-translate-y-1">
                <div className="text-3xl">🔒</div>
                <div className="mt-2 font-semibold">Safe edits</div>
                <div className="text-sm text-gray-600">Review changes carefully before applying them.</div>
              </div>
            </div>

            <div className="mt-6 bg-gradient-to-r from-indigo-50 to-pink-50 rounded-lg p-4 text-sm text-gray-700 border border-white/30">
              <strong>Built for local code review:</strong>

              <div className="mt-1 text-xs text-gray-500">
                Analyze source files locally and inspect AI findings
                before applying changes.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
