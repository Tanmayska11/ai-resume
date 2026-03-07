"use client"

import { useState } from "react"
import JobDescriptionCard from "@/components/JobDescriptionCard"
import MatchScoreGauge from "@/components/MatchScoreGauge"
import AnalysisDetails from "@/components/AnalysisDetails"
import PrivacyBox from "@/components/PrivacyBox"
import { runMatch, MatchResponse } from "@/lib/matchApi"
import "@/styles/match.css"

export default function MatchPage() {
  const [jd, setJd] = useState("")
  const [result, setResult] = useState<MatchResponse | null>(null)
  const [loading, setLoading] = useState(false)



  const clearAll = () => {
    setJd("")
    setResult(null)
  }


  const run = async ({
    jdText,
    file,
  }: {
    jdText: string
    file: File | null
  }) => {
    if (!jdText.trim() && !file) return

    setLoading(true)
    try {
      const res = await runMatch(jdText, file)
      setResult(res)
    } finally {
      setLoading(false)
    }
  }


  return (
    <main className="page-container">
      {/* Header */}
      <div className="page-header">
        <h1>Predictive Hiring Fit Score model</h1>
        <p>Data-driven assessment of candidate–role compatibility</p>
      </div>

      {/* JD Input */}
      <JobDescriptionCard
        value={jd}
        onChange={setJd}
        onSubmit={run}
        onClear={clearAll}     // ✅ NEW
        loading={loading}
      />


      {result && (
        <>
          {/* Analysis Results */}
          <section className="card analysis-card">
            <div className="analysis-header">
              <h3>📄 Analysis Results</h3>
            </div>

            <div className="analysis-grid">
              <MatchScoreGauge
                score={result.match_score}
                label={result.summary}
              />
              <AnalysisDetails data={result} />
            </div>
          </section>


          {/* Privacy */}
          <PrivacyBox />
        </>
      )}
    </main>
  )
}
