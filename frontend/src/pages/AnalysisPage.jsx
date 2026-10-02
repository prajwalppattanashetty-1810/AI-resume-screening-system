import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { analyzeResume } from '../services/api';
import {
  User,
  Mail,
  Phone,
  GraduationCap,
  Briefcase,
  FolderGit2,
  Award,
  FileText,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  Cpu,
  Sparkles,
  TrendingUp,
  CheckCircle2,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';

const AnalysisPage = () => {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyzeResume(fileId);
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        console.error('Analysis failed:', err);
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
            'Failed to analyze resume. Please ensure the server is running and the file ID is valid.'
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (fileId) {
      fetchAnalysis();
    }

    return () => {
      isMounted = false;
    };
  }, [fileId]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <LoadingSpinner message="Extracting text and running NLP Information Extraction..." />
        <p className="text-gray-500 text-sm mt-3">Parsing contact info, sections, experience, technologies, and computing ATS scores...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="p-8 bg-red-50 border border-red-200 rounded-2xl inline-block max-w-lg shadow-sm">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-800 mb-2">Analysis Error</h2>
          <p className="text-red-700 text-sm mb-6">{error || 'Resume data could not be retrieved.'}</p>
          <button
            onClick={() => navigate('/upload')}
            className="px-6 py-2.5 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition"
          >
            Upload Again
          </button>
        </div>
      </div>
    );
  }

  const profile = data.profile || {};
  const education = profile.education || [];
  const experience = profile.experience || [];
  const projects = profile.projects || [];
  const certifications = profile.certifications || [];
  const metadata = data.metadata || {};
  const scores = data.scores || null;
  const suggestions = data.improvement_suggestions || [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 sm:px-6 lg:px-8 animate-fade-in">
      {/* Header with Candidate Profile Overview */}
      <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-gray-100">
          <div>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shadow-sm">
                <User className="w-7 h-7" />
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-3xl font-extrabold text-gray-900">
                    {profile.name || 'Candidate Profile'}
                  </h1>
                  {scores && (
                    <span className="hidden sm:inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                      ATS Score: {Math.round(scores.overall)}%
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-0.5">Resume ID: {data.file_id}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
            {profile.email && (
              <span className="flex items-center gap-1.5 bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-medium">
                <Mail className="w-3.5 h-3.5 text-blue-600" />
                {profile.email}
              </span>
            )}
            {profile.phone && (
              <span className="flex items-center gap-1.5 bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-medium">
                <Phone className="w-3.5 h-3.5 text-emerald-600" />
                {profile.phone}
              </span>
            )}
            <Link
              to={`/improvements/${fileId}`}
              className="flex items-center gap-1.5 bg-amber-50 hover:bg-amber-100 px-3.5 py-2 rounded-xl border border-amber-200 text-xs font-bold text-amber-800 transition"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              Suggestions ({suggestions.length})
            </Link>
          </div>
        </div>

        {/* NLP Processing & Document Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pages</span>
            <p className="text-xl font-bold text-slate-800 mt-1">{metadata.page_count || 1}</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Raw Characters</span>
            <p className="text-xl font-bold text-slate-800 mt-1">{data.text_length || 0}</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">NLP Tokens</span>
            <p className="text-xl font-bold text-slate-800 mt-1">{data.token_count || 0}</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pipeline Status</span>
            <p className="text-xl font-bold text-emerald-600 mt-1 capitalize">{data.status || 'Analyzed'}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Experience and Projects (2 cols on large screens) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Work Experience Timeline */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2.5">
              <Briefcase className="w-5 h-5 text-blue-600" />
              Work Experience ({experience.length})
            </h2>

            {experience.length === 0 ? (
              <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center">
                <p className="text-gray-500 text-sm italic mb-2">No formal employment records detected.</p>
                <Link
                  to={`/improvements/${fileId}`}
                  className="text-xs font-bold text-blue-600 hover:underline"
                >
                  View recommended ways to add project/internship experience →
                </Link>
              </div>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-blue-200">
                {experience.map((exp, index) => (
                  <div key={index} className="relative">
                    {/* Timeline node */}
                    <div className="absolute -left-[29px] top-1.5 w-3 h-3 rounded-full bg-blue-600 ring-4 ring-blue-100" />

                    <div className="p-5 bg-slate-50 rounded-xl border border-slate-200">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                        <h3 className="font-bold text-gray-900 text-base">{exp.title || 'Role'}</h3>
                        {exp.duration && (
                          <span className="text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md w-fit">
                            {exp.duration}
                          </span>
                        )}
                      </div>
                      {exp.company && (
                        <p className="text-sm font-semibold text-slate-700 mb-2">{exp.company}</p>
                      )}
                      {exp.description && (
                        <p className="text-sm text-gray-600 leading-relaxed">{exp.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Projects */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2.5">
              <FolderGit2 className="w-5 h-5 text-indigo-600" />
              Projects ({projects.length})
            </h2>

            {projects.length === 0 ? (
              <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center">
                <p className="text-gray-500 text-sm italic mb-2">No projects detected.</p>
                <Link
                  to={`/improvements/${fileId}`}
                  className="text-xs font-bold text-indigo-600 hover:underline"
                >
                  Learn how adding 2 technical projects boosts your match rate →
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                {projects.map((proj, index) => (
                  <div key={index} className="p-5 bg-slate-50 rounded-xl border border-slate-200">
                    <h3 className="font-bold text-gray-900 text-base mb-2">{proj.name || 'Project'}</h3>
                    {proj.description && (
                      <p className="text-sm text-gray-600 leading-relaxed mb-4">{proj.description}</p>
                    )}
                    {proj.technologies && proj.technologies.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-3 border-t border-slate-200">
                        <span className="text-xs font-semibold text-gray-500 mr-1 flex items-center gap-1">
                          <Cpu className="w-3.5 h-3.5 text-indigo-500" /> Tech Stack:
                        </span>
                        {proj.technologies.map((tech, tIdx) => (
                          <span
                            key={tIdx}
                            className="text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Education, Certifications & Skills */}
        <div className="space-y-8">
          {/* Education Timeline */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-emerald-600" />
              Education ({education.length})
            </h2>

            {education.length === 0 ? (
              <p className="text-gray-500 text-sm italic">No education entries detected.</p>
            ) : (
              <div className="relative pl-5 space-y-4 before:absolute before:left-1.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-emerald-200">
                {education.map((edu, idx) => (
                  <div key={idx} className="relative">
                    <div className="absolute -left-[19px] top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-600 ring-2 ring-emerald-100" />
                    <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100">
                      <h4 className="font-semibold text-gray-900 text-sm">{edu.degree || 'Degree'}</h4>
                      {edu.institution && (
                        <p className="text-xs text-gray-600 mt-1">{edu.institution}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs font-medium text-emerald-800">
                        {edu.graduation_year && <span>Year: {edu.graduation_year}</span>}
                        {edu.cgpa && <span>CGPA: {edu.cgpa}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Certifications */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              Certifications ({certifications.length})
            </h2>

            {certifications.length === 0 ? (
              <p className="text-gray-500 text-sm italic">No certifications detected.</p>
            ) : (
              <ul className="space-y-2">
                {certifications.map((cert, idx) => (
                  <li key={idx} className="text-xs text-gray-700 bg-amber-50/60 border border-amber-200/60 px-3 py-2 rounded-lg">
                    {cert}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Extracted Skills Preview (Phase 4) */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-600" />
                Skills Extracted ({data.skills_analysis?.total_skills || 0})
              </h2>
              <span className="text-[11px] font-semibold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md border border-indigo-200">
                Phase 4
              </span>
            </div>

            {(!data.skills_analysis || (data.skills_analysis.skills || []).length === 0) ? (
              <p className="text-gray-500 text-sm italic">No skills extracted.</p>
            ) : (
              <div>
                <div className="flex flex-wrap gap-1.5 mb-4 max-h-48 overflow-y-auto pr-1">
                  {(data.skills_analysis.skills || []).slice(0, 15).map((skill, sIdx) => {
                    const isAdv = skill.proficiency === 'Advanced';
                    const isInt = skill.proficiency === 'Intermediate';
                    return (
                      <span
                        key={sIdx}
                        className={`text-xs px-2.5 py-1 rounded-lg border font-medium flex items-center gap-1.5 ${
                          isAdv
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                            : isInt
                            ? 'bg-indigo-50 text-indigo-800 border-indigo-200'
                            : 'bg-slate-50 text-slate-700 border-slate-200'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            isAdv ? 'bg-emerald-500' : isInt ? 'bg-indigo-500' : 'bg-slate-400'
                          }`}
                        />
                        {skill.name}
                      </span>
                    );
                  })}
                  {(data.skills_analysis.skills || []).length > 15 && (
                    <span className="text-xs text-gray-500 self-center pl-1">
                      +{(data.skills_analysis.skills || []).length - 15} more
                    </span>
                  )}
                </div>

                <Link
                  to={`/skills/${fileId}`}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-bold transition"
                >
                  Explore Full Skills Matrix & Evidence <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </div>

          {/* Integrated Actions Card */}
          <div className="bg-gradient-to-br from-slate-900 to-indigo-950 rounded-2xl p-6 text-white shadow-md border border-slate-800">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <h3 className="text-base font-bold">End-to-End System Navigation</h3>
            </div>
            <p className="text-slate-300 text-xs mb-5 leading-relaxed">
              Resume parsing and multi-dimensional analysis complete. Explore matching career paths, identify skill gaps, and view actionable suggestions.
            </p>
            <div className="flex flex-col gap-2.5">
              <Link
                to={`/recommendations/${fileId}`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                <Briefcase className="w-3.5 h-3.5" /> View Job Recommendations <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                to={`/improvements/${fileId}`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5" /> Actionable Improvements ({suggestions.length})
              </Link>
              <Link
                to={`/skills/${fileId}`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                Inspect Skills Engine <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                to={`/dashboard/${fileId}`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-xs font-semibold transition"
              >
                Go to Dashboard
              </Link>
              <Link
                to="/upload"
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-transparent text-slate-400 hover:text-white text-xs font-medium transition"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Upload Another Resume
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
