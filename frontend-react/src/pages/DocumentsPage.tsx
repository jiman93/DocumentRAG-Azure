import { FileText, Trash2, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { useDocuments, useDeleteDocument } from "@/hooks/useApi";
import { useDocumentStore } from "@/store";
import { useNavigate } from "react-router-dom";
import type { Document } from "@/types";

export default function DocumentsPage() {
  const { data: documents, isLoading } = useDocuments();
  const deleteMutation = useDeleteDocument();
  const { selectedDocument, selectDocument } = useDocumentStore();
  const navigate = useNavigate();
  const resolveId = (doc: Document) => doc.document_id || doc.id || "";

  const handleSelect = (doc: Document) => {
    selectDocument(doc);
    navigate("/chat");
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this document?")) {
      await deleteMutation.mutateAsync(id);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "indexed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "processing":
      case "uploaded":
        return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />;
      case "failed":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  const documentList = documents ?? [];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
        <p className="text-gray-600">Manage your uploaded documents</p>
      </div>

      {documentList.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FileText className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
          <p className="text-gray-600 mb-6">Upload your first document to get started</p>
          <button
            onClick={() => navigate("/")}
            className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 transition-colors"
          >
            Upload Document
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {documentList.map((doc: Document) => {
            const docId = resolveId(doc);
            return (
              <div
                key={docId || doc.filename}
                onClick={() => doc.status === "indexed" && docId && handleSelect(doc)}
                className={`
                bg-white rounded-lg border-2 p-6 transition-all cursor-pointer
                ${
                  selectedDocument?.document_id === doc.document_id
                    ? "border-primary-500 shadow-md"
                    : "border-gray-200 hover:border-primary-300 hover:shadow-sm"
                }
                ${doc.status !== "indexed" && "opacity-75 cursor-not-allowed"}
              `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="bg-primary-100 p-3 rounded-lg">
                      <FileText className="h-6 w-6 text-primary-600" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {doc.filename}
                        </h3>
                        {getStatusIcon(doc.status)}
                      </div>

                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center">
                          <span className="font-medium mr-1">Type:</span>
                          {`.${doc.file_type.toUpperCase()}`}
                        </span>
                        <span className="flex items-center">
                          <span className="font-medium mr-1">Size:</span>
                          {formatFileSize(doc.file_size)}
                        </span>
                        {doc.chunk_count && (
                          <span className="flex items-center">
                            <span className="font-medium mr-1">Chunks:</span>
                            {doc.chunk_count}
                          </span>
                        )}
                        <span className="flex items-center">
                          <span className="font-medium mr-1">Uploaded:</span>
                          {doc.upload_time ? formatDate(doc.upload_time) : "—"}
                        </span>
                      </div>

                      <div className="mt-2">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            doc.status === "indexed"
                              ? "bg-green-100 text-green-800"
                              : doc.status === "processing"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => handleDelete(e, docId)}
                    disabled={deleteMutation.isPending}
                    className="ml-4 text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
