import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import { CheckCircle, AlertCircle, Info } from 'lucide-react';
import { uploadResume } from '../services/api';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [fileId, setFileId] = useState(null);
  const navigate = useNavigate();

  const handleFileSelect = async (selectedFile) => {
    if (!selectedFile) {
      setFile(null);
      setUploadSuccess(false);
      setError(null);
      return;
    }

    setFile(selectedFile);
    setIsUploading(true);
    setError(null);

    try {
      // API call to upload resume
      const response = await uploadResume(selectedFile);
      setFileId(response.file_id || response.fileId || 'temp-id');
      setUploadSuccess(true);
    } catch (err) {
      console.error(err);
      // For demo purposes, we'll allow continuing even if the backend isn't up
      setError("Failed to connect to server. Running in offline mode.");
      setFileId('demo-id');
      setUploadSuccess(true);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = () => {
    if (fileId) {
      navigate(`/analysis/${fileId}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">Upload Your Resume</h1>
        <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
          Let our AI analyze your profile to find your perfect job match.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <FileUpload 
            onFileSelect={handleFileSelect} 
            isUploading={isUploading}
            error={null} // Handle errors below
          />

          {error && (
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <p className="text-sm text-yellow-800">{error}</p>
            </div>
          )}

          {uploadSuccess && (
            <div className="mt-8 flex flex-col items-center animate-fade-in-up">
              <div className="flex items-center gap-2 text-green-600 mb-6">
                <CheckCircle className="w-6 h-6" />
                <span className="font-semibold text-lg">Upload Successful!</span>
              </div>
              <button
                onClick={handleAnalyze}
                className="px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg w-full max-w-xs"
              >
                Analyze Resume
              </button>
            </div>
          )}
        </div>

        <div className="bg-slate-50 rounded-2xl p-6 border border-gray-200 h-fit">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-blue-500" />
            Instructions
          </h3>
          <ul className="space-y-4 text-gray-600 text-sm">
            <li className="flex gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5"></div>
              <span><strong>Supported format:</strong> PDF only</span>
            </li>
            <li className="flex gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5"></div>
              <span><strong>Maximum size:</strong> 10MB</span>
            </li>
            <li className="flex gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5"></div>
              <span><strong>Tips for best results:</strong> Use standard fonts, avoid complex layouts or graphics, and ensure your text is selectable.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
