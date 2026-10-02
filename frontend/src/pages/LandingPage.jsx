import { Link } from 'react-router-dom';
import { FileText, Brain, Target, Shield, Upload, BarChart3, Sparkles } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative pt-24 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900 z-0"></div>
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 z-0"></div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight mb-6">
            AI-Powered <span className="text-blue-400">Resume Analysis</span>
          </h1>
          <p className="mt-4 max-w-2xl text-xl text-gray-300 mx-auto mb-10">
            Upload your resume &rarr; Analyze your skills &rarr; Discover matching careers
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-blue-900 bg-white rounded-full hover:bg-blue-50 transition-colors shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
          >
            <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
            Analyze Your Resume
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">Powerful Features</h2>
            <p className="mt-4 text-lg text-gray-600">Everything you need to optimize your career path.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="bg-blue-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Brain className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Analysis</h3>
              <p className="text-gray-600 leading-relaxed">
                NLP-powered resume parsing and skill extraction to understand your professional profile deeply.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="bg-indigo-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Target className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Job Matching</h3>
              <p className="text-gray-600 leading-relaxed">
                AI-driven job recommendations with similarity scoring to find your perfect role.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="bg-purple-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <BarChart3 className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Skill Insights</h3>
              <p className="text-gray-600 leading-relaxed">
                Identify skill gaps and get actionable improvement suggestions to level up.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4 border-2 border-blue-200">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">1. Upload Resume</h3>
              <p className="text-gray-500 mt-2">Simply upload your PDF resume.</p>
            </div>
            
            <div className="flex flex-col items-center relative">
              <div className="hidden md:block absolute top-8 left-0 w-full h-0.5 bg-gray-200 -z-10"></div>
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4 border-2 border-blue-200">
                <Brain className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">2. AI Analyzes</h3>
              <p className="text-gray-500 mt-2">Our AI parses and understands your profile.</p>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4 border-2 border-blue-200">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">3. Get Results</h3>
              <p className="text-gray-500 mt-2">Receive personalized recommendations.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy Banner */}
      <section className="bg-slate-900 py-10">
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-center gap-4 text-center sm:text-left">
          <Shield className="w-10 h-10 text-blue-400" />
          <div>
            <h4 className="text-white font-bold text-lg">Your privacy matters.</h4>
            <p className="text-gray-400">Resumes are processed locally and never shared with third parties.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
