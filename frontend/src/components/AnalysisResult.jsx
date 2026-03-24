import FeatureBreakdown from "./FeatureBreakdown";
import HighlightedText from "./HighlightedText";

const CONFIG = {
  LEGITIMATE: {
    bg: "bg-green-50",
    border: "border-green-300",
    badge: "bg-green-100 text-green-800 border-green-300",
    bar: "bg-green-500",
    icon: "✓",
    iconBg: "bg-green-100 text-green-700",
    title: "This job looks Legitimate",
    subtitle: "No major red flags detected",
  },
  SUSPICIOUS: {
    bg: "bg-amber-50",
    border: "border-amber-300",
    badge: "bg-amber-100 text-amber-800 border-amber-300",
    bar: "bg-amber-500",
    icon: "⚠",
    iconBg: "bg-amber-100 text-amber-700",
    title: "This job looks Suspicious",
    subtitle: "Some red flags found — proceed with caution",
  },
  SCAM: {
    bg: "bg-red-50",
    border: "border-red-300",
    badge: "bg-red-100 text-red-800 border-red-300",
    bar: "bg-red-500",
    icon: "✕",
    iconBg: "bg-red-100 text-red-700",
    title: "This is likely a Scam",
    subtitle: "Multiple scam indicators detected — do NOT proceed",
  },
};

export default function AnalysisResult({ result, originalText, onReset }) {
  const cfg = CONFIG[result.label] || CONFIG["SUSPICIOUS"];
  const scorePercent = Math.min(100, Math.max(0, result.score));

  return (
    <div className="space-y-4">
      {/* Main Result Card */}
      <div className={`rounded-2xl border-2 ${cfg.border} ${cfg.bg} p-6`}>
        {/* Header */}
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center 
                           text-2xl font-bold flex-shrink-0 ${cfg.iconBg}`}>
            {cfg.icon}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-xl font-bold text-gray-900">{cfg.title}</h2>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${cfg.badge}`}>
                {result.label}
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{cfg.subtitle}</p>
          </div>
        </div>

        {/* Score Bar */}
        <div className="mt-5">
          <div className="flex justify-between text-xs text-gray-500 mb-1.5">
            <span>Safe</span>
            <span className="font-semibold text-gray-700">
              Scam Score: {scorePercent.toFixed(1)} / 100
            </span>
            <span>Scam</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1.5">
            <span className="text-green-600 font-medium">0–39 Legitimate</span>
            <span className="text-amber-600 font-medium">40–69 Suspicious</span>
            <span className="text-red-600 font-medium">70–100 Scam</span>
          </div>
        </div>

        {/* Confidence + Components */}
        <div className="mt-4 grid grid-cols-3 gap-3">
          <ScorePill label="Confidence" value={`${(result.confidence * 100).toFixed(0)}%`} />
          <ScorePill label="ML Score" value={result.ml_probability.toFixed(2)} />
          <ScorePill label="Rule Penalty" value={`+${result.rule_penalty.toFixed(1)}`} />
        </div>
      </div>

      {/* Red Flags */}
      {result.reasons && result.reasons.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span>🚩</span> Red Flags Detected ({result.reasons.length})
          </h3>
          <ul className="space-y-2">
            {result.reasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-gray-700">
                <span className="text-red-500 mt-0.5 flex-shrink-0">●</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Highlighted Text */}
      {originalText && result.highlighted_keywords?.length > 0 && (
        <HighlightedText
          text={originalText}
          keywords={result.highlighted_keywords}
        />
      )}

      {/* Feature Breakdown */}
      <FeatureBreakdown features={result.feature_breakdown} />

      {/* Analyze Another Button */}
      <button
        onClick={onReset}
        className="w-full py-3 rounded-xl border border-gray-300 text-gray-700 
                   font-medium hover:bg-gray-50 transition-colors"
      >
        ← Analyze Another Job Posting
      </button>
    </div>
  );
}

function ScorePill({ label, value }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 px-3 py-2 text-center">
      <div className="text-xs text-gray-400">{label}</div>
      <div className="text-base font-bold text-gray-800 mt-0.5">{value}</div>
    </div>
  );
}
