import { useState } from "react";

const EXAMPLE_SCAM = `URGENT HIRING! Earn ₹50,000 per day from home! No experience needed. 
No qualification required. Registration fee: ₹500 only (fully refundable). 
Send Aadhar card and bank account details to join. WhatsApp ONLY: +91 98XXXXXXXX. 
HURRY! Only 10 seats left! 100% guaranteed income! Don't miss this golden opportunity!`;

const EXAMPLE_LEGIT = `We are a mid-sized IT company looking for a Python Developer with 2+ years of experience. 
The role involves building REST APIs using FastAPI and PostgreSQL. Salary: 8-12 LPA. 
Apply through our official portal. Interview process includes a technical round and HR discussion. 
Company email: hr@techcorp.com. Location: Bangalore (Hybrid). PF and health insurance provided.`;

export default function InputPanel({ onAnalyze, loading, error }) {
  const [mode, setMode] = useState("text");
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    if (!input.trim()) return;
    onAnalyze({ mode, input: input.trim() });
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.ctrlKey) handleSubmit();
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        Analyze a Job Posting
      </h2>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-4">
        {[
          { key: "text", label: "📋 Paste Text", desc: "Copy & paste job description" },
          { key: "url",  label: "🔗 Enter URL",  desc: "LinkedIn, Internshala, etc." },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => { setMode(key); setInput(""); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              mode === key
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Input Area */}
      {mode === "text" ? (
        <div>
          <textarea
            rows={8}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Paste the full job description here…"
            className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none 
                       focus:ring-2 focus:ring-blue-400 text-sm text-gray-800 
                       placeholder-gray-400 resize-y font-mono"
          />
          {/* Quick-fill examples */}
          <div className="flex gap-2 mt-2">
            <span className="text-xs text-gray-400">Quick test:</span>
            <button
              onClick={() => setInput(EXAMPLE_SCAM)}
              className="text-xs text-red-500 hover:underline"
            >
              Scam example
            </button>
            <button
              onClick={() => setInput(EXAMPLE_LEGIT)}
              className="text-xs text-green-600 hover:underline"
            >
              Legit example
            </button>
          </div>
        </div>
      ) : (
        <div>
          <input
            type="url"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="https://www.linkedin.com/jobs/view/..."
            className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none 
                       focus:ring-2 focus:ring-blue-400 text-sm text-gray-800"
          />
          <p className="text-xs text-gray-400 mt-2">
            Note: Some platforms (LinkedIn) block scraping. Try copying text instead if it fails.
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Analyze Button */}
      <button
        onClick={handleSubmit}
        disabled={loading || !input.trim()}
        className={`mt-4 w-full py-3 rounded-xl font-semibold text-base transition-all ${
          loading || !input.trim()
            ? "bg-gray-200 text-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700 active:scale-[0.99] text-white shadow-sm"
        }`}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            Analyzing…
          </span>
        ) : (
          "🔍 Analyze Job Posting"
        )}
      </button>

      <p className="text-xs text-center text-gray-400 mt-3">
        Ctrl+Enter to analyze · Results in ~1–2 seconds
      </p>
    </div>
  );
}
