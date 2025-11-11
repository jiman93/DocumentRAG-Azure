import ChatInterface from '@/components/ChatInterface';
import { useDocumentStore } from '@/store';
import { FileText, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ChatPage() {
  const { selectedDocument } = useDocumentStore();
  const navigate = useNavigate();

  if (!selectedDocument) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <FileText className="mx-auto h-20 w-20 text-gray-300 mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 mb-3">
            No Document Selected
          </h2>
          <p className="text-gray-600 mb-6">
            Select a document from the Documents page or upload a new one to start chatting
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/documents')}
              className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 transition-colors"
            >
              View Documents
            </button>
            <button
              onClick={() => navigate('/')}
              className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors flex items-center"
            >
              <Upload className="h-5 w-5 mr-2" />
              Upload New
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <ChatInterface />
    </div>
  );
}
