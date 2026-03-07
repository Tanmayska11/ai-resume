export default function MatchScoreGauge({
  score,
  label,
}: {
  score: number
  label: string
}) {
  const radius = 44
  const circumference = 2 * Math.PI * radius
  const value = Math.round(score)
  const offset = circumference - (value / 100) * circumference

  const isLowScore = value < 50
  const gaugeColor = isLowScore ? "#e53935" : "var(--primary)"

  return (
    <div className="score-card">
      <h5>MATCH SCORE</h5>

      <div className="gauge">
        <svg viewBox="0 0 120 120">
          {/* Background track */}
          <circle
            className="gauge-track"
            cx="60"
            cy="60"
            r={radius}
          />

          {/* Progress arc */}
          <circle
            className="gauge-progress"
            cx="60"
            cy="60"
            r={radius}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            stroke={gaugeColor}
          />
        </svg>


        <div className="gauge-text">
          <span className="score-value">{value}%</span>
          <small
            className="score-label"
            style={{ color: gaugeColor }}
          >
            {label}
          </small>
        </div>
      </div>

      <p className="score-note">
        Score shows compatibility with core role requirements.
      </p>
      <div className="score-help">
        <span className="help-trigger">How score calculated?</span>

        <div className="help-tooltip">
          <strong>ℹ️ How the Match Score Is Calculated</strong>

          <p>
            The score reflects how closely a resume aligns with a job description
            based on skills, experience, and demonstrated relevance.
          </p>

          <p className="tooltip-heading">It considers:</p>

          <ol>
            <li>Required skill match & proficiency</li>
            <li>Relevant professional experience</li>
            <li>Similarity between job responsibilities and past work</li>
            <li>Role alignment (e.g. Data Engineer, ML Engineer, Backend)</li>
            <li>Projects and hands-on evidence</li>
            <li>Education and certifications (minor boost)</li>
          </ol>

          <p>
            Extra skills never reduce the score.
            <br />
            Safeguards prevent unfair inflation or under-scoring.
          </p>

          <p className="tooltip-foot">
            This is an alignment estimate, not a hiring decision.
          </p>
        </div>
      </div>

    </div>
  )
}
