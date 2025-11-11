import { useState } from "react";
import { FileText, Upload, Loader2, MessageSquare } from "lucide-react";
import ChatInterface from "@/components/ChatInterface";
import { useChatStore, useDocumentStore } from "@/store";
import { useConversations } from "@/hooks/useApi";
import { documentApi } from "@/services/api";
import type { ConversationSummary } from "@/types";
import { useNavigate } from "react-router-dom";

const MAX_PREVIEW_LENGTH = 140;

const NoDocumentSelected = ({ onViewDocuments, onUpload }: { onViewDocuments: () => void; onUpload: () => void }) => (
  <div className="flex h-full items-center justify-center">
    <div className="text-center max-w-md">
      <FileText className="mx-auto mb-6 h-20 w-20 text-gray-300" />
      <h2 className="mb-3 text-2xl font-bold text-gray-900">No Document Selected</h2>
      <p className="mb-6 text-gray-600">
        Select a document from the Documents page or upload a new one to start chatting.
      </p>
      <div className="flex justify-center space-x-4">
        <button
          onClick={onViewDocuments}
          className="rounded-lg bg-primary-500 px-6 py-2 text-white transition-colors hover:bg-primary-600"
        >
          View Documents
        </button>
        <button
          onClick={onUpload}
          className="flex items-center rounded-lg bg-gray-200 px-6 py-2 text-gray-800 transition-colors hover:bg-gray-300"
        >
          <Upload className="mr-2 h-5 w-5" />
          Upload New
        </button>
      </div>
    </div>
  </div>
);

const formatTimestamp = (isoString: string) => {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const diffMs = Date.now() - date.getTime();
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diffMs < minute) {
    return "Just now";
  }
  if (diffMs < hour) {
    const minutes = Math.round(diffMs / minute);
    return `${minutes}m ago`;
  }
  if (diffMs < day) {
    const hours = Math.round(diffMs / hour);
    return `${hours}h ago`;
  }

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
};

const getConversationTitle = (conversation: ConversationSummary) => {
  return conversation.title || conversation.metadata.document_name || "Conversation";
};

const getPreviewText = (conversation: ConversationSummary) => {
  const preview = conversation.last_message_preview;
  if (!preview) {
    return conversation.message_count > 0 ? `${conversation.message_count} messages` : "No messages yet";
  }

  if (preview.length <= MAX_PREVIEW_LENGTH) {
    return preview;
  }

  return `${preview.slice(0, MAX_PREVIEW_LENGTH)}…`;
};

export default function ChatPage() {
  const navigate = useNavigate();
  const { data: conversations, isLoading: isConversationsLoading } = useConversations();
  const {
    selectedDocument,
    documents,
    selectDocument,
  } = useDocumentStore();
  const {
    clearConversation,
    setConversationId,
    setDocumentId,
    conversationId,
  } = useChatStore();
  const [isSwitchingConversation, setIsSwitchingConversation] = useState(false);

  const conversationList = conversations ?? [];

  const handleSelectConversation = async (conversation: ConversationSummary) => {
    if (conversation.conversation_id === conversationId) {
      return;
    }

    setIsSwitchingConversation(true);
    try {
      clearConversation();

      const documentId = conversation.metadata.document_id ?? null;

      if (documentId) {
        setDocumentId(documentId);
        const existingDocument =
          documents.find(
            (doc) => doc.document_id === documentId || (doc.id ? doc.id === documentId : false),
          ) ?? null;

        if (existingDocument) {
          selectDocument(existingDocument);
        } else {
          try {
            const fetchedDocument = await documentApi.get(documentId);
            selectDocument(fetchedDocument);
          } catch (error) {
            console.error("Failed to load document metadata", error);
          }
        }
      } else {
        selectDocument(null);
        setDocumentId(null);
      }

      setConversationId(conversation.conversation_id);
    } finally {
      setIsSwitchingConversation(false);
    }
  };

  return (
    <div className="flex h-full flex-col lg:flex-row">
      <aside className="border-b border-gray-200 bg-white lg:h-full lg:w-80 lg:border-b-0 lg:border-r">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5 text-primary-500" />
            <span className="text-sm font-semibold text-gray-900">Conversations</span>
          </div>
          {(isConversationsLoading || isSwitchingConversation) && (
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          )}
        </div>

        <div className="h-48 overflow-y-auto px-2 py-3 lg:h-[calc(100%-56px)]">
          {conversationList.length === 0 && !isConversationsLoading ? (
            <div className="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-4 text-center text-xs text-gray-500">
              No conversations yet. Ask a question to start a new conversation.
            </div>
          ) : (
            <ul className="space-y-2">
              {conversationList.map((conversation) => {
                const active = conversation.conversation_id === conversationId;
                const documentName = conversation.metadata.document_name;

                return (
                  <li key={conversation.conversation_id}>
                    <button
                      type="button"
                      disabled={isSwitchingConversation}
                      onClick={() => handleSelectConversation(conversation)}
                      className={`w-full rounded-lg border px-4 py-3 text-left transition-colors ${
                        active
                          ? "border-primary-500 bg-primary-50"
                          : "border-gray-200 bg-white hover:border-primary-300 hover:bg-gray-50"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-gray-900">
                          {getConversationTitle(conversation)}
                        </h3>
                        <span className="text-xs text-gray-400">
                          {formatTimestamp(conversation.updated_at)}
                        </span>
                      </div>

                      {documentName && (
                        <span className="mt-2 inline-flex max-w-full items-center truncate rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                          {documentName}
                        </span>
                      )}

                      <p className="mt-2 line-clamp-2 text-xs text-gray-600">
                        {getPreviewText(conversation)}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </aside>

      <section className="flex-1">
        {selectedDocument ? (
          <ChatInterface />
        ) : (
          <NoDocumentSelected
            onViewDocuments={() => navigate("/documents")}
            onUpload={() => navigate("/")}
          />
        )}
      </section>
    </div>
  );
}
