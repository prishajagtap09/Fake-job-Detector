import { useState } from "react";
import AnalysisResult from "./components/AnalysisResult";
import InputPanel from "./components/InputPanel";
import Header from "./components/Header";
import HowItWorks from "./components/HowItWorks";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastInput, setLastInput] = useState("");
  const [lastMode, setLastMode] = useState("text");

  const analyze = async ({ mode, input }) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setLastInput(input);
    setLastMode(mode);

    try {
      const endpoint =
        mode === "text" ? "/analyze/text" : "/analyze/url";
      const body =
        mode === "text" ? { text: input } : { url: input };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      if (err.message.includes("fetch")) {
        setError(
          "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."
        );
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-3xl mx-auto px-4 py-8">
        {!result ? (
          <>
            <InputPanel onAnalyze={analyze} loading={loading} error={error} />
            <HowItWorks />
          </>
        ) : (
          <AnalysisResult
            result={result}
            originalText={lastMode === "text" ? lastInput : ""}
            onReset={reset}
          />
        )}
      </main>

      <footer className="text-center text-sm text-gray-400 py-8">
        FakeJob Detector · Built with FastAPI + React · For educational use
      </footer>
    </div>
  );
}
