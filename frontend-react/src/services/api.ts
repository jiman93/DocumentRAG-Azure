import axios from "axios";
import type { Document, ChatRequest, ChatResponse, ConversationHistory, Source } from "@/types";

const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

const api = axios.create({
  baseURL: API_URL,
  timeout: 120_000, // 2 minutes for long-running operations
});

// Request interceptor (for auth tokens if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Document APIs
const mapDocument = (doc: any): Document => {
  const rawType = doc.file_type ?? "";
  const normalizedType =
    typeof rawType === "string" ? rawType.replace(/^\./, "").toLowerCase() : "";

  return {
    id: doc.document_id,
    document_id: doc.document_id,
    filename: doc.filename,
    file_type: normalizedType,
    file_size: doc.file_size,
    status: doc.status,
    upload_time: doc.upload_time,
    indexed_at: doc.indexed_at ?? null,
    chunk_count: doc.chunk_count ?? undefined,
    blob_url: doc.blob_url ?? undefined,
    metadata: doc.metadata ?? undefined,
  };
};

export const documentApi = {
  upload: async (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/documents/upload", formData, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  list: async (): Promise<Document[]> => {
    const response = await api.get("/documents");
    const documents = response.data?.documents ?? [];
    return documents.map(mapDocument);
  },

  delete: async (id: string) => {
    await api.delete(`/documents/${id}`);
  },

  get: async (id: string): Promise<Document> => {
    const response = await api.get(`/documents/${id}`);
    return mapDocument(response.data);
  },
};

// Chat APIs
export const chatApi = {
  query: async (request: ChatRequest) => {
    const response = await api.post("/chat/query", request);
    const data = response.data;

    const sources: Source[] = (data.citations ?? []).map((citation: any) => ({
      document_id: citation.document_id,
      document_name: citation.document_name,
      chunk_id: citation.chunk_id,
      content: citation.content,
      score: citation.score,
      page: citation.page,
    }));

    const chatResponse: ChatResponse = {
      answer: data.answer,
      sources,
      conversation_id: data.conversation_id,
      metadata: data.metadata ?? undefined,
      confidence_score: data.confidence_score,
      related_questions: data.related_questions,
    };

    return chatResponse;
  },

  getHistory: async (conversationId: string) => {
    const response = await api.get<ConversationHistory>(`/chat/history/${conversationId}`);
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

export default api;
