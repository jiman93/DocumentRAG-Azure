import { FileText, Upload } from "lucide-react";
import ChatInterface from "@/components/ChatInterface";
import { useDocumentStore } from "@/store";
import { useNavigate } from "react-router-dom";

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

export default function ChatPage() {
  const navigate = useNavigate();
  const { selectedDocument } = useDocumentStore();

  return (
    <div className="flex h-full flex-col">
      {selectedDocument ? (
        <ChatInterface />
      ) : (
        <NoDocumentSelected
          onViewDocuments={() => navigate("/documents")}
          onUpload={() => navigate("/")}
        />
      )}
    </div>
  );
}
