export default function HighlightedText({ text, keywords }) {
  if (!text || !keywords || keywords.length === 0) return null;

  // Build highlighted HTML
  const getHighlightedSegments = () => {
    // Sort keywords by length desc so longer phrases match first
    const sorted = [...keywords].sort((a, b) => b.length - a.length);
    
    let segments = [{ text, highlighted: false }];

    for (const keyword of sorted) {
      const newSegments = [];
      for (const seg of segments) {
        if (seg.highlighted) {
          newSegments.push(seg);
          continue;
        }
        const regex = new RegExp(`(${escapeRegex(keyword)})`, "gi");
        const parts = seg.text.split(regex);
        for (const part of parts) {
          if (regex.test(part)) {
            newSegments.push({ text: part, highlighted: true });
          } else if (part) {
            newSegments.push({ text: part, highlighted: false });
          }
          regex.lastIndex = 0;
        }
      }
      segments = newSegments;
    }

    return segments;
  };

  const segments = getHighlightedSegments();
  const displayText = text.length > 800 ? text.slice(0, 800) + "…" : text;

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <span>🔍</span> Risky Keywords Highlighted
      </h3>
      <div className="text-sm text-gray-700 leading-relaxed font-mono bg-gray-50 
                      rounded-xl p-4 max-h-56 overflow-y-auto whitespace-pre-wrap">
        {segments.map((seg, i) =>
          seg.highlighted ? (
            <mark
              key={i}
              className="bg-yellow-200 text-yellow-900 px-0.5 rounded font-semibold not-italic"
            >
              {seg.text}
            </mark>
          ) : (
            <span key={i}>{seg.text}</span>
          )
        )}
        {text.length > 800 && (
          <span className="text-gray-400 italic"> (truncated for display)</span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {keywords.slice(0, 8).map((kw, i) => (
          <span
            key={i}
            className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 
                       rounded-full border border-yellow-300 font-medium"
          >
            {kw}
          </span>
        ))}
        {keywords.length > 8 && (
          <span className="text-xs text-gray-400">+{keywords.length - 8} more</span>
        )}
      </div>
    </div>
  );
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
