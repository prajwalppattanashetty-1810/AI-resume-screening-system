import { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const FileUpload = ({ onFileSelect, isUploading, error }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file) => {
    if (file.type !== 'application/pdf') {
      return 'Please upload a PDF file.';
    }
    if (file.size > 10 * 1024 * 1024) { // 10MB
      return 'File size should not exceed 10MB.';
    }
    return null;
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const validationError = validateFile(file);
      if (!validationError) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert(validationError);
      }
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validationError = validateFile(file);
      if (!validationError) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert(validationError);
      }
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div 
        className={`relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl transition-all duration-300 ease-in-out ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !selectedFile && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf"
          onChange={handleChange}
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center justify-center">
            <LoadingSpinner message="Uploading resume..." />
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center justify-center p-6 text-center">
            <FileText className="w-16 h-16 text-blue-500 mb-4" />
            <p className="text-sm font-semibold text-gray-700 truncate max-w-xs">{selectedFile.name}</p>
            <p className="text-xs text-gray-500 mt-1">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                removeFile();
              }}
              className="mt-4 px-4 py-2 text-sm text-red-600 bg-red-100 rounded-lg hover:bg-red-200 flex items-center gap-2 transition-colors"
            >
              <X className="w-4 h-4" /> Remove File
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-6 text-center cursor-pointer">
            <Upload className="w-12 h-12 text-gray-400 mb-4" />
            <p className="mb-2 text-sm text-gray-600">
              <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">PDF up to 10MB</p>
          </div>
        )}
      </div>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
