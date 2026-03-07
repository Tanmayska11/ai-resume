export interface MatchResponse {
  match_score: number; // 0–100
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  summary: string;
}
