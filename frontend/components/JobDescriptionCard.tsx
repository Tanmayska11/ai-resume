import { useRef, useState } from "react"

interface Props {
  value: string
  onChange: (v: string) => void
  onSubmit: (payload: { jdText: string; file: File | null }) => void
  onClear: () => void
  loading: boolean
}

export default function JobDescriptionCard({
  value,
  onChange,
  onSubmit,
  onClear,
  loading,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleAttachClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleClear = () => {
    removeFile()
    onClear()
  }

  const handleSubmit = () => {


    if (!value.trim() && !selectedFile) {
      alert("Please enter the job description or upload the JD file.")
      return
    }

    onSubmit({
      jdText: value,
      file: selectedFile,
    })
  }

  return (
    <section className="card jd-card">
      {/* LEFT PROFILE */}
      <div className="profile-side">
        <div className="profile-circle">👤+</div>
        <p>Tanmay’s Profile</p>
      </div>

      {/* RIGHT INPUT */}
      <div className="jd-side">
        <div className="jd-input-wrapper">
          <h3 className="jd-title">✏️ Paste the job description</h3>

          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Type or paste the job description details here..."
            disabled={!!selectedFile}
          />

          {/* FILE PREVIEW */}
          {selectedFile && (
            <div className="file-preview">
              📄 {selectedFile.name}
              <button
                type="button"
                className="remove-file"
                onClick={removeFile}
                aria-label="Remove file"
              >
                ✕
              </button>
            </div>
          )}

          {/* FOOTER */}
          <div className="jd-footer">
            {/* LEFT BUTTON GROUP */}
            <div className="jd-footer-left">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx"
                style={{ display: "none" }}
                onChange={handleFileChange}
              />

              <button
                type="button"
                className="attach-btn"
                onClick={handleAttachClick}
              >
                📎 Attachment
              </button>

              <button
                type="button"
                className="clear-btn danger"
                onClick={handleClear}
                disabled={!value && !selectedFile}
              >
                ✖ Clear Text
              </button>
            </div>

            {/* PRIMARY ACTION */}
            <button onClick={handleSubmit} disabled={loading} style={{
                                                                    opacity: loading ? 0.7 : 1,
                                                                    cursor: loading ? "not-allowed" : "pointer",
                                                                  }}
            >
              {loading ? "Analyzing..." : "Start Analysis ↻"}
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
