// Document types
export type DocumentStatus = 'uploaded' | 'processing' | 'indexed' | 'failed';

export interface Document {
  id?: string;
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: DocumentStatus;
  upload_time: string;
  indexed_at?: string | null;
  chunk_count?: number;
  blob_url?: string | null;
  metadata?: Record<string, unknown>;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: string;
}

export interface Source {
  document_id: string;
  document_name: string;
  chunk_id: string;
  content: string;
  score: number;
  page?: number;
}

export interface ChatRequest {
  question: string;
  document_id?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  conversation_id: string;
}

// Upload types
export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}
