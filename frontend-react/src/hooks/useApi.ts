import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { documentApi, chatApi } from "@/services/api";
import { useDocumentStore, useChatStore } from "@/store";
import type { ChatRequest, ConversationHistoryMessage, ChatMessage } from "@/types";

// Document hooks
export const useDocuments = () => {
  const { setDocuments } = useDocumentStore();

  return useQuery({
    queryKey: ["documents"],
    queryFn: async () => {
      const documents = await documentApi.list();
      setDocuments(documents);
      return documents;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      documentApi.upload(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  const { removeDocument } = useDocumentStore();

  return useMutation({
    mutationFn: (id: string) => documentApi.delete(id),
    onSuccess: (_, id) => {
      removeDocument(id);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
};

// Chat hooks
export const useChatQuery = () => {
  const {
    addMessage,
    setConversationId,
    setLoading,
    conversationId,
    messages,
    setDocumentId,
    documentId,
  } = useChatStore();

  return useMutation({
    mutationFn: async (request: ChatRequest) => {
      setLoading(true);

      const historyPayload: ConversationHistoryMessage[] = messages.map((message) => ({
        role: message.role,
        content: message.content,
        timestamp: message.timestamp,
        metadata: message.metadata,
      }));

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content: request.question,
        timestamp: new Date().toISOString(),
      };

      addMessage(userMessage);

      const payload: ChatRequest = {
        ...request,
        document_id: request.document_id ?? documentId ?? undefined,
        conversation_id: request.conversation_id ?? conversationId ?? undefined,
        conversation_history: historyPayload,
      };

      if (payload.document_id) {
        setDocumentId(payload.document_id);
      }

      const response = await chatApi.query(payload);
      return response;
    },
    onSuccess: (data, variables) => {
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        timestamp: new Date().toISOString(),
        metadata: data.metadata,
      };

      addMessage(assistantMessage);

      if (variables.document_id) {
        setDocumentId(variables.document_id);
      }

      setConversationId(data.conversation_id);
    },
    onError: () => {
      setLoading(false);
    },
    onSettled: () => {
      setLoading(false);
    },
  });
};
