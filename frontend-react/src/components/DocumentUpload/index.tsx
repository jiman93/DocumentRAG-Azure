import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useUploadDocument } from '@/hooks/useApi';
import type { UploadProgress } from '@/types';

export default function DocumentUpload() {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const uploadMutation = useUploadDocument();

  const onDrop = async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const uploadProgress: UploadProgress = {
        filename: file.name,
        progress: 0,
        status: 'uploading',
      };

      setUploads((prev) => [...prev, uploadProgress]);

      try {
        await uploadMutation.mutateAsync({
          file,
          onProgress: (progress) => {
            setUploads((prev) =>
              prev.map((u) =>
                u.filename === file.name
                  ? { ...u, progress, status: progress === 100 ? 'processing' : 'uploading' }
                  : u
              )
            );
          },
        });

        // Mark as complete
        setUploads((prev) =>
          prev.map((u) =>
            u.filename === file.name ? { ...u, status: 'complete', progress: 100 } : u
          )
        );

        // Remove after 3 seconds
        setTimeout(() => {
          setUploads((prev) => prev.filter((u) => u.filename !== file.name));
        }, 3000);
      } catch (error) {
        setUploads((prev) =>
          prev.map((u) =>
            u.filename === file.name
              ? { ...u, status: 'error', error: 'Upload failed' }
              : u
          )
        );
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          or click to select files
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Supports PDF, DOCX, TXT, MD (max 10MB)
        </p>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="space-y-2">
          {uploads.map((upload) => (
            <div
              key={upload.filename}
              className="bg-white border border-gray-200 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700 truncate max-w-xs">
                    {upload.filename}
                  </span>
                </div>
                {upload.status === 'complete' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {upload.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
              </div>

              {/* Progress Bar */}
              {(upload.status === 'uploading' || upload.status === 'processing') && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${upload.progress}%` }}
                  />
                </div>
              )}

              {/* Status Text */}
              <div className="mt-2 text-xs text-gray-500">
                {upload.status === 'uploading' && `Uploading... ${upload.progress}%`}
                {upload.status === 'processing' && 'Processing document...'}
                {upload.status === 'complete' && 'Upload complete!'}
                {upload.status === 'error' && (
                  <span className="text-red-500">{upload.error}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
