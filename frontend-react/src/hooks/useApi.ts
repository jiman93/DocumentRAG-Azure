import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { documentApi, chatApi } from '@/services/api';
import { useDocumentStore, useChatStore } from '@/store';
import type { ChatRequest } from '@/types';

// Document hooks
export const useDocuments = () => {
  const { setDocuments } = useDocumentStore();

  return useQuery({
    queryKey: ['documents'],
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
  const { addDocument } = useDocumentStore();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      documentApi.upload(file, onProgress),
    onSuccess: (data) => {
      addDocument(data);
      queryClient.invalidateQueries({ queryKey: ['documents'] });
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
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

// Chat hooks
export const useChatQuery = () => {
  const { addMessage, setConversationId, setLoading } = useChatStore();

  return useMutation({
    mutationFn: async (request: ChatRequest) => {
      setLoading(true);
      
      // Add user message
      addMessage({
        id: Date.now().toString(),
        role: 'user',
        content: request.question,
        timestamp: new Date().toISOString(),
      });

      const response = await chatApi.query(request);
      return response;
    },
    onSuccess: (data) => {
      // Add assistant message
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date().toISOString(),
      });
      setConversationId(data.conversation_id);
      setLoading(false);
    },
    onError: () => {
      setLoading(false);
    },
  });
};
