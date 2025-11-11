import { useState, useRef, useEffect } from 'react';
import { Send, FileText, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useChatQuery } from '@/hooks/useApi';
import { useChatStore, useDocumentStore } from '@/store';

export default function ChatInterface() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, isLoading } = useChatStore();
  const { selectedDocument } = useDocumentStore();
  const chatMutation = useChatQuery();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput('');

    chatMutation.mutate({
      question,
      document_id: selectedDocument?.id,
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <FileText className="mx-auto h-16 w-16 mb-4 text-gray-300" />
            <p className="text-lg font-medium">No messages yet</p>
            <p className="text-sm mt-2">
              {selectedDocument
                ? `Ask a question about "${selectedDocument.filename}"`
                : 'Upload a document and start asking questions'}
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {message.content}
                  </ReactMarkdown>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-300">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
                      <div className="space-y-1">
                        {message.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="text-xs bg-white rounded p-2 border border-gray-200"
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
                            <p className="text-gray-600 mt-1 line-clamp-2">
                              {source.content}
                            </p>
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
        {isLoading && (
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
        {selectedDocument && (
          <div className="mb-3 flex items-center text-sm text-gray-600 bg-blue-50 px-3 py-2 rounded">
            <FileText className="h-4 w-4 mr-2" />
            <span>Asking about: <strong>{selectedDocument.filename}</strong></span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              selectedDocument
                ? 'Ask a question about this document...'
                : 'Upload a document first...'
            }
            disabled={isLoading || !selectedDocument}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !selectedDocument}
            className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
