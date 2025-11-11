import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { MessageSquare, Loader2 } from "lucide-react";
import { useConversations } from "@/hooks/useApi";
import { useChatStore, useDocumentStore } from "@/store";
import { documentApi } from "@/services/api";
import type { ConversationSummary, Document } from "@/types";

interface ConversationListProps {
  onSelect?: () => void;
}

const MAX_PREVIEW_LENGTH = 120;

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
  return (
    conversation.title ||
    conversation.metadata?.document_name ||
    "Conversation"
  );
};

const getPreviewText = (conversation: ConversationSummary) => {
  const preview = conversation.last_message_preview;
  if (!preview) {
    return conversation.message_count > 0
      ? `${conversation.message_count} messages`
      : "No messages yet";
  }

  if (preview.length <= MAX_PREVIEW_LENGTH) {
    return preview;
  }

  return `${preview.slice(0, MAX_PREVIEW_LENGTH)}…`;
};

export default function ConversationList({ onSelect }: ConversationListProps) {
  const { data: conversations, isLoading } = useConversations();
  const {
    clearConversation,
    setConversationId,
    setDocumentId,
    conversationId,
  } = useChatStore();
  const {
    documents,
    selectDocument,
    removeDocument,
  } = useDocumentStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSwitching, setIsSwitching] = useState(false);

  const conversationList = conversations ?? [];

  const handleSelectConversation = async (conversation: ConversationSummary) => {
    if (conversation.conversation_id === conversationId) {
      onSelect?.();
      return;
    }

    setIsSwitching(true);
    clearConversation();

    const documentId = (conversation.metadata?.document_id as string | undefined) ?? null;

    if (documentId) {
      setDocumentId(documentId);
      const existingDocument =
        documents.find(
          (doc: Document) =>
            doc.document_id === documentId || (doc.id ? doc.id === documentId : false),
        ) ?? null;

      if (existingDocument) {
        selectDocument(existingDocument);
      } else {
        try {
          const fetchedDocument = await documentApi.get(documentId);
          selectDocument(fetchedDocument);
        } catch (error) {
          console.error("Failed to load document metadata", error);
          removeDocument(documentId);
        }
      }
    } else {
      selectDocument(null);
      setDocumentId(null);
    }

    setConversationId(conversation.conversation_id);
    setIsSwitching(false);

    if (!location.pathname.startsWith("/chat")) {
      navigate("/chat");
    }

    onSelect?.();
  };

  return (
    <div className="mt-6">
      <div className="mb-2 flex items-center justify-between px-4 text-sm font-semibold text-gray-900">
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-4 w-4 text-primary-500" />
          <span>Conversations</span>
        </div>
        {(isLoading || isSwitching) && (
          <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
        )}
      </div>
      <div className="max-h-72 overflow-y-auto px-2 pb-4">
        {conversationList.length === 0 && !isLoading ? (
          <div className="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-3 text-xs text-gray-500">
            No conversations yet. Ask a question to start a new conversation.
          </div>
        ) : (
          <ul className="space-y-2">
            {conversationList.map((conversation) => {
              const active = conversation.conversation_id === conversationId;
              const documentName = conversation.metadata?.document_name as string | undefined;

              return (
                <li key={conversation.conversation_id}>
                  <button
                    type="button"
                    disabled={isSwitching}
                    onClick={() => void handleSelectConversation(conversation)}
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
    </div>
  );
}

