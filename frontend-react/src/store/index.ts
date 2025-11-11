import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Document, ChatMessage } from '@/types';

interface DocumentStore {
  documents: Document[];
  selectedDocument: Document | null;
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  selectDocument: (document: Document | null) => void;
}

export const useDocumentStore = create<DocumentStore>()(
  persist(
    (set) => ({
      documents: [],
      selectedDocument: null,
      setDocuments: (documents) => set({ documents }),
      addDocument: (document) =>
        set((state) => ({ documents: [...state.documents, document] })),
      removeDocument: (id) =>
        set((state) => ({
          documents: state.documents.filter((doc) => doc.id !== id),
          selectedDocument: state.selectedDocument?.id === id ? null : state.selectedDocument,
        })),
      selectDocument: (document) => set({ selectedDocument: document }),
    }),
    {
      name: 'document-storage',
    }
  )
);

interface ChatStore {
  messages: ChatMessage[];
  conversationId: string | null;
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  clearMessages: () => void;
  setConversationId: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      conversationId: null,
      isLoading: false,
      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),
      setMessages: (messages) => set({ messages }),
      clearMessages: () => set({ messages: [], conversationId: null }),
      setConversationId: (id) => set({ conversationId: id }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'chat-storage',
    }
  )
);
