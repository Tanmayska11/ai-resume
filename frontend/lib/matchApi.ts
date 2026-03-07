// frontend/lib/matchApi.ts

export interface MatchResponse {
  match_score: number
  strengths: string[]
  gaps: string[]
  recommendations: string[]
  summary: string
}

/**
 * Runs resume–JD match using text and/or file.
 * Uses multipart/form-data (required for file upload).
 */
export async function runMatch(
  jdText: string,
  file: File | null
): Promise<MatchResponse> {
  const formData = new FormData()

  // Add text JD if present
  if (jdText && jdText.trim()) {
    formData.append("job_description", jdText)
  }

  // Add file if present
  if (file) {
    formData.append("file", file)
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/match`, {
    method: "POST",
    body: formData, // ✅ NO headers here
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || "Failed to evaluate resume–job match")
  }

  return res.json()
}
