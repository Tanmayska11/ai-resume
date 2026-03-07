//frontend/components/AnalysisDetails.tsx


import { useEffect, useState } from "react"
import { MatchResponse } from "@/lib/matchApi"

export default function AnalysisDetails({ data }: { data: MatchResponse }) {
  const [showStrengths, setShowStrengths] = useState(false)
  const [showGaps, setShowGaps] = useState(false)
  const [showRecs, setShowRecs] = useState(false)
  const [showSummary, setShowSummary] = useState(false)

  useEffect(() => {
    setShowStrengths(false)
    setShowGaps(false)
    setShowRecs(false)
    setShowSummary(false)

    const t1 = setTimeout(() => setShowStrengths(true), 300)
    const t2 = setTimeout(() => setShowGaps(true), 700)
    const t3 = setTimeout(() => setShowRecs(true), 1000)
    const t4 = setTimeout(() => setShowSummary(true), 1300)

    return () => {
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
      clearTimeout(t4)
    }
  }, [data])

  return (
    <div className="details-card">
      {/* Strengths */}
      {showStrengths && data.strengths.length > 0 && (
        <section className="fade-in">
          <h4 className="green">✔ Strengths</h4>
          <ul>
            {data.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="inline-sections">
        {/* Gaps */}
        {showGaps && data.gaps.length > 0 && (
          <div className="fade-in">
            <h4 className="amber">⚠ Gaps</h4>
            <p>{data.gaps[0]}</p>
          </div>
        )}

        {/* Recommendations */}
        {showRecs && data.recommendations.length > 0 && (
          <div className="fade-in">
            <h4 className="blue">💡 Recommendations</h4>
            <p>{data.recommendations[0]}</p>
          </div>
        )}
      </section>

      {/* Summary */}
      {showSummary && data.summary && (
        <section className="fade-in">
          <h4 className="blue">📄 Summary</h4>
          <p>{data.summary}</p>
        </section>
      )}
    </div>
  )
}
