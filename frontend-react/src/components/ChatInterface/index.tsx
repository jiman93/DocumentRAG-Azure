import { useState, useRef, useEffect, useMemo } from "react";
import { Send, FileText, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useChatQuery } from "@/hooks/useApi";
import { useChatStore, useDocumentStore } from "@/store";
import { chatApi } from "@/services/api";
import type { ChatMessage, ConversationHistory } from "@/types";
import { useQueryClient } from "@tanstack/react-query";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    conversationId,
    clearConversation,
    setMessages,
    setLoading,
    documentId,
    setDocumentId,
    setConversationId,
  } = useChatStore();
  const { selectedDocument, selectDocument, removeDocument } = useDocumentStore();
  const chatMutation = useChatQuery();
  const [isHydrating, setIsHydrating] = useState(false);
  const hydratedConversationRef = useRef<string | null>(null);
  const queryClient = useQueryClient();

  // Ensure loading flag resets when the component mounts
  useEffect(() => {
    setLoading(false);
  }, [setLoading]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Reset conversation when switching documents
  useEffect(() => {
    if (!selectedDocument) {
      clearConversation();
      return;
    }

    if (documentId && selectedDocument.document_id !== documentId) {
      clearConversation();
    }
  }, [selectedDocument, documentId, clearConversation]);

  // Hydrate conversation from backend if needed
  useEffect(() => {
    let cancelled = false;
    const loadHistory = async () => {
      if (
        !conversationId ||
        messages.length > 0 ||
        isHydrating ||
        hydratedConversationRef.current === conversationId
      ) {
        return;
      }

      let fetchedHistory: ConversationHistory | null = null;
      try {
        setIsHydrating(true);
        setLoading(true);
        const history = await chatApi.getHistory(conversationId);
        fetchedHistory = history;
        if (cancelled) return;

        const mapped: ChatMessage[] = history.messages.map((msg, index) => ({
          id: `${conversationId}-${index}`,
          role: msg.role === "assistant" ? "assistant" : "user",
          content: msg.content,
          timestamp: msg.timestamp,
          metadata: msg.metadata,
        }));

        setMessages(mapped);
      } catch (error) {
        console.error("Failed to hydrate conversation history", error);
      } finally {
        if (!cancelled) {
          setIsHydrating(false);
          setLoading(false);
          hydratedConversationRef.current = conversationId ?? null;
        }

        if (fetchedHistory?.missing) {
          hydratedConversationRef.current = null;
          if (selectedDocument) {
            removeDocument(selectedDocument.document_id);
            selectDocument(null);
          } else if (documentId) {
            removeDocument(documentId);
          }
          clearConversation();
          setDocumentId(null);
          setConversationId(null);
          queryClient.invalidateQueries({ queryKey: ["conversations"] });
          queryClient.invalidateQueries({ queryKey: ["documents"] });
          return;
        }
      }
    };

    void loadHistory();

    return () => {
      cancelled = true;
    };
  }, [
    conversationId,
    messages.length,
    isHydrating,
    setMessages,
    setLoading,
    clearConversation,
    selectDocument,
    queryClient,
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput("");

    chatMutation.mutate({
      question,
      document_id: selectedDocument?.document_id,
    });
  };

  const showLoading = useMemo(() => isLoading || isHydrating, [isLoading, isHydrating]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {showLoading && conversationId && messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-gray-500">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-100" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-200" />
              </div>
            </div>
            <p className="mt-4 text-sm font-medium text-gray-600">Restoring conversation…</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="mt-12 text-center text-gray-500">
            <FileText className="mx-auto mb-4 h-16 w-16 text-gray-300" />
            <p className="text-lg font-medium">No messages yet</p>
            <p className="mt-2 text-sm">
              {selectedDocument
                ? `Ask a question about "${selectedDocument.filename}"`
                : "Upload a document and start asking questions"}
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    message.role === "user"
                      ? "bg-primary-500 text-white"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {message.content}
                  </ReactMarkdown>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 border-t border-gray-300 pt-3">
                      <p className="mb-2 text-xs font-semibold text-gray-600">Sources:</p>
                      <div className="space-y-1">
                        {message.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="rounded border border-gray-200 bg-white p-2 text-xs"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-gray-700">
                                {source.document_name}
                                {source.page && ` (Page ${source.page})`}
                              </span>
                              <span className="text-gray-500">
                                Score: {(source.score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p className="mt-1 line-clamp-2 text-gray-600">{source.content}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </>
        )}

        {/* Loading Indicator */}
        {showLoading && messages.length > 0 && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="mb-3 flex items-center justify-between text-sm text-gray-600">
          {selectedDocument && (
            <div className="flex items-center bg-blue-50 px-3 py-2 rounded">
              <FileText className="h-4 w-4 mr-2" />
              <span>
                Asking about: <strong>{selectedDocument.filename}</strong>
              </span>
            </div>
          )}
          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearConversation}
              className="flex items-center text-xs text-gray-500 hover:text-gray-700"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              New conversation
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              selectedDocument
                ? "Ask a question about this document..."
                : "Upload a document first..."
            }
            disabled={showLoading}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || showLoading || !selectedDocument}
            className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
