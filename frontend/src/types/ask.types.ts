export interface AskRequest {
  question: string;
}

export interface Citation {
  source_file: string;
  chunk_id: string;
  snippet: string;
  score: number;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
  grounded: boolean;
  trace: string[];
}
