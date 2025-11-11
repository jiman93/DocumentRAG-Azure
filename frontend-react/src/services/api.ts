import axios from 'axios';
import type { Document, ChatRequest, ChatResponse } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for long-running operations
});

// Request interceptor (for auth tokens if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
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
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Document APIs
export const documentApi = {
  upload: async (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  list: async () => {
    const response = await api.get<{ documents: Document[] }>('/documents');
    return response.data.documents;
  },

  delete: async (id: string) => {
    await api.delete(`/documents/${id}`);
  },

  get: async (id: string) => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },
};

// Chat APIs
export const chatApi = {
  query: async (request: ChatRequest) => {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  getHistory: async (conversationId: string) => {
    const response = await api.get<{ history: ChatResponse[] }>(
      `/chat/history/${conversationId}`
    );
    return response.data.history;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
