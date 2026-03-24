const STEPS = [
  {
    icon: "📥",
    title: "Input",
    desc: "Paste job text, enter a URL, or upload a screenshot",
  },
  {
    icon: "🔬",
    title: "Extract",
    desc: "We pull 18+ signals: language patterns, contact info, urgency phrases",
  },
  {
    icon: "🤖",
    title: "Analyze",
    desc: "ML model + rule engine score the posting from 0 to 100",
  },
  {
    icon: "🛡️",
    title: "Result",
    desc: "Get a verdict with highlighted red flags and full explanation",
  },
];

const RED_FLAGS = [
  "Asks for registration fee",
  "WhatsApp-only contact",
  "Unrealistic salary claims",
  "No company name / location",
  "Requests Aadhar / PAN upfront",
  "Urgency + pressure language",
  "Free email domain (Gmail/Yahoo)",
  "'Guaranteed job' promises",
];

export default function HowItWorks() {
  return (
    <div className="mt-6 space-y-4">
      {/* Steps */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">How it works</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STEPS.map((step, i) => (
            <div key={i} className="text-center">
              <div className="text-2xl mb-1.5">{step.icon}</div>
              <div className="text-sm font-semibold text-gray-700">{step.title}</div>
              <div className="text-xs text-gray-500 mt-1 leading-relaxed">{step.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Common Red Flags */}
      <div className="bg-red-50 rounded-2xl border border-red-200 p-5">
        <h3 className="font-semibold text-red-800 mb-3 flex items-center gap-2">
          <span>🚩</span> Common Scam Red Flags
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          {RED_FLAGS.map((flag, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-red-700">
              <span className="text-red-400">●</span>
              {flag}
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <p className="text-xs text-center text-gray-400 px-4">
        This tool is for educational purposes. Always verify companies independently before
        sharing personal information or paying any fees.
      </p>
    </div>
  );
}
