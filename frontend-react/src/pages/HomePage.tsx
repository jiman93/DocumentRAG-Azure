import DocumentUpload from '@/components/DocumentUpload';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Documents
        </h1>
        <p className="text-gray-600">
          Upload your documents to start asking questions using AI
        </p>
      </div>

      <DocumentUpload />

      <div className="mt-12 bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          How it works
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <div className="bg-primary-100 text-primary-700 rounded-full w-10 h-10 flex items-center justify-center font-bold mb-3">
              1
            </div>
            <h3 className="font-medium text-gray-900 mb-2">Upload Documents</h3>
            <p className="text-sm text-gray-600">
              Upload PDF, DOCX, or TXT files containing your information
            </p>
          </div>
          <div>
            <div className="bg-primary-100 text-primary-700 rounded-full w-10 h-10 flex items-center justify-center font-bold mb-3">
              2
            </div>
            <h3 className="font-medium text-gray-900 mb-2">AI Processing</h3>
            <p className="text-sm text-gray-600">
              Our AI extracts and indexes the content for intelligent search
            </p>
          </div>
          <div>
            <div className="bg-primary-100 text-primary-700 rounded-full w-10 h-10 flex items-center justify-center font-bold mb-3">
              3
            </div>
            <h3 className="font-medium text-gray-900 mb-2">Ask Questions</h3>
            <p className="text-sm text-gray-600">
              Chat with your documents and get accurate, sourced answers
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
