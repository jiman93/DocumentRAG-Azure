import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Document, ChatMessage } from "@/types";

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
      addDocument: (document) => set((state) => ({ documents: [...state.documents, document] })),
      removeDocument: (id) =>
        set((state) => {
          const match = (doc: Document) =>
            doc.document_id === id || (doc.id ? doc.id === id : false);
          const filtered = state.documents.filter((doc) => !match(doc));
          const selected =
            state.selectedDocument && match(state.selectedDocument) ? null : state.selectedDocument;
          return { documents: filtered, selectedDocument: selected };
        }),
      selectDocument: (document) => set({ selectedDocument: document }),
    }),
    {
      name: "document-storage",
    }
  )
);

interface ChatStore {
  messages: ChatMessage[];
  conversationId: string | null;
  documentId: string | null;
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  clearConversation: () => void;
  setConversationId: (id: string | null) => void;
  setDocumentId: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      conversationId: null,
      documentId: null,
      isLoading: false,
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      setMessages: (messages) => set({ messages }),
      clearConversation: () =>
        set({ messages: [], conversationId: null, documentId: null, isLoading: false }),
      setConversationId: (id) => set({ conversationId: id }),
      setDocumentId: (id) => set({ documentId: id }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: "chat-storage",
    }
  )
);
