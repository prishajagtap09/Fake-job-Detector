export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-3xl mx-auto px-4 py-4 flex items-center gap-3">
        <div className="text-2xl">🛡️</div>
        <div>
          <h1 className="text-xl font-bold text-gray-900 leading-tight">
            FakeJob Detector
          </h1>
          <p className="text-xs text-gray-500">
            AI-powered scam detection for job & internship postings
          </p>
        </div>
        <div className="ml-auto">
          <span className="bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full border border-blue-200">
            v1.0 · Free
          </span>
        </div>
      </div>
    </header>
  );
}
