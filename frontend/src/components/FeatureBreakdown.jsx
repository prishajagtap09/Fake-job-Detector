import { useState } from "react";

// Which features to display and how to format them
const DISPLAY_FEATURES = [
  { key: "asks_for_fee",         label: "Asks for fee",           type: "bool", danger: true },
  { key: "asks_for_documents",   label: "Requests personal docs", type: "bool", danger: true },
  { key: "whatsapp_contact",     label: "WhatsApp contact only",  type: "bool", danger: true },
  { key: "salary_too_high",      label: "Unrealistic salary",     type: "bool", danger: true },
  { key: "guaranteed_language",  label: "Guaranteed job/income",  type: "bool", danger: true },
  { key: "uses_free_email",      label: "Free email domain",      type: "bool", danger: true },
  { key: "no_experience_claim",  label: "No experience needed",   type: "bool", danger: false },
  { key: "urgency_score",        label: "Urgency phrases",        type: "number" },
  { key: "high_risk_pattern_count", label: "High-risk patterns",  type: "number" },
  { key: "has_company_name",     label: "Company name present",   type: "bool", danger: false, invert: true },
  { key: "has_location",         label: "Location mentioned",     type: "bool", danger: false, invert: true },
  { key: "has_job_requirements", label: "Requirements listed",    type: "bool", danger: false, invert: true },
  { key: "platform_trust_score", label: "Platform trust score",   type: "score" },
  { key: "domain_age_days",      label: "Domain age",             type: "days" },
];

export default function FeatureBreakdown({ features }) {
  const [expanded, setExpanded] = useState(false);

  if (!features) return null;

  const items = DISPLAY_FEATURES.filter((f) => features[f.key] !== undefined);
  const visible = expanded ? items : items.slice(0, 7);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <span>📊</span> Feature Analysis
      </h3>

      <div className="space-y-2">
        {visible.map((feat) => (
          <FeatureRow key={feat.key} feat={feat} value={features[feat.key]} />
        ))}
      </div>

      {items.length > 7 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-3 text-sm text-blue-600 hover:underline"
        >
          {expanded ? "Show less ↑" : `Show all ${items.length} features ↓`}
        </button>
      )}
    </div>
  );
}

function FeatureRow({ feat, value }) {
  const { label, type, danger, invert } = feat;

  let display = "";
  let statusColor = "text-gray-500";
  let dot = "bg-gray-300";

  if (type === "bool") {
    const isTrue = value === true;
    const isBad = danger ? isTrue : (invert ? !isTrue : false);

    display = isTrue ? "Yes" : "No";
    if (isBad) {
      statusColor = "text-red-600 font-semibold";
      dot = "bg-red-500";
    } else if ((!danger && isTrue) || (danger && !isTrue)) {
      statusColor = "text-green-600";
      dot = "bg-green-500";
    }
  } else if (type === "number") {
    display = String(value);
    if (value >= 3) { statusColor = "text-red-600 font-semibold"; dot = "bg-red-500"; }
    else if (value >= 1) { statusColor = "text-amber-600"; dot = "bg-amber-400"; }
    else { statusColor = "text-green-600"; dot = "bg-green-500"; }
  } else if (type === "score") {
    display = `${(value * 100).toFixed(0)}%`;
    if (value < 0.4) { statusColor = "text-red-600"; dot = "bg-red-500"; }
    else if (value < 0.7) { statusColor = "text-amber-600"; dot = "bg-amber-400"; }
    else { statusColor = "text-green-600"; dot = "bg-green-500"; }
  } else if (type === "days") {
    display = value >= 365 ? ">1 year" : `${value} days`;
    if (value < 30) { statusColor = "text-red-600"; dot = "bg-red-500"; }
    else if (value < 90) { statusColor = "text-amber-600"; dot = "bg-amber-400"; }
    else { statusColor = "text-green-600"; dot = "bg-green-500"; }
  }

  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
        {label}
      </div>
      <span className={`text-sm ${statusColor}`}>{display}</span>
    </div>
  );
}
