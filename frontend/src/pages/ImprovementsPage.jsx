import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { getResumeImprovements } from '../services/api';
import {
  Sparkles,
  TrendingUp,
  Award,
  CheckCircle2,
  AlertTriangle,
  Code,
  Briefcase,
  FolderGit2,
  GraduationCap,
  FileText,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  Layers,
  ChevronRight,
  ShieldCheck,
  Check
} from 'lucide-react';

const ImprovementsPage = () => {
  const { fileId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await getResumeImprovements(fileId);
        if (isMounted) {
          setData(res);
        }
      } catch (err) {
        console.error('Failed to load improvements:', err);
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
            'Failed to compute improvement suggestions. Ensure the resume has been uploaded and analyzed.'
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (fileId) {
      fetchData();
    }

    return () => {
      isMounted = false;
    };
  }, [fileId]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <LoadingSpinner message="Evaluating resume dimensions and generating improvement roadmap..." />
        <p className="text-gray-500 text-sm mt-3">Computing ATS scores across skills, projects, experience, and completeness...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="p-8 bg-red-50 border border-red-200 rounded-2xl inline-block max-w-lg shadow-sm">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-800 mb-2">Unable to Load Improvements</h2>
          <p className="text-red-700 text-sm mb-6">{error || 'Data could not be retrieved.'}</p>
          <div className="flex justify-center gap-3">
            <button
              onClick={() => navigate('/upload')}
              className="px-5 py-2.5 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition"
            >
              Upload Resume
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const scores = data.scores || {};
  const suggestions = data.suggestions || [];
  const profileSummary = data.profile_summary || {};
  const overall = scores.overall ?? 0;

  const getScoreColor = (val) => {
    if (val >= 80) return 'text-emerald-600';
    if (val >= 60) return 'text-amber-600';
    return 'text-rose-600';
  };

  const getScoreBg = (val) => {
    if (val >= 80) return 'bg-emerald-500';
    if (val >= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getScoreBadge = (val) => {
    if (val >= 85) return { text: 'Strong Profile', bg: 'bg-emerald-100 text-emerald-800 border-emerald-300' };
    if (val >= 70) return { text: 'Competitive', bg: 'bg-blue-100 text-blue-800 border-blue-300' };
    if (val >= 50) return { text: 'Moderate Match', bg: 'bg-amber-100 text-amber-800 border-amber-300' };
    return { text: 'Needs Enhancement', bg: 'bg-rose-100 text-rose-800 border-rose-300' };
  };

  const badge = getScoreBadge(overall);

  const dimensionCards = [
    {
      title: 'Technical Skills',
      score: scores.skills ?? 0,
      icon: Code,
      desc: `${profileSummary.skills_count || 0} skills detected across domains`,
      color: 'indigo'
    },
    {
      title: 'Projects & Stack',
      score: scores.projects ?? 0,
      icon: FolderGit2,
      desc: `${profileSummary.projects_count || 0} projects with tech stack`,
      color: 'blue'
    },
    {
      title: 'Experience & Impact',
      score: scores.experience ?? 0,
      icon: Briefcase,
      desc: `${profileSummary.experience_count || 0} professional roles listed`,
      color: 'emerald'
    },
    {
      title: 'Education & Academics',
      score: scores.education ?? 0,
      icon: GraduationCap,
      desc: `${profileSummary.education_count || 0} academic degree entries`,
      color: 'purple'
    },
    {
      title: 'ATS Completeness',
      score: scores.completeness ?? 0,
      icon: ShieldCheck,
      desc: 'Contact info & structural sections',
      color: 'cyan'
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-gray-100">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-extrabold text-gray-900">Resume Strength & Improvements</h1>
                <p className="text-sm text-gray-500 mt-1">
                  Candidate: <span className="font-semibold text-gray-700">{data.candidate_name}</span> | File ID: {fileId}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to={`/analysis/${fileId}`}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition"
            >
              View Full Analysis
            </Link>
            <Link
              to={`/recommendations/${fileId}`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
            >
              Job Recommendations <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Overall Score Highlight */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6 items-center">
          <div className="md:col-span-1 flex items-center gap-5 p-5 bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl shadow-sm">
            <div className="relative flex items-center justify-center">
              <div className="w-20 h-20 rounded-full border-4 border-slate-700 flex items-center justify-center bg-slate-800/80">
                <span className="text-2xl font-black text-white">{Math.round(overall)}%</span>
              </div>
            </div>
            <div>
              <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold border mb-1.5 ${badge.bg}`}>
                {badge.text}
              </span>
              <h3 className="text-base font-bold text-white">Overall ATS Score</h3>
              <p className="text-xs text-slate-300 mt-0.5">Weighted composite benchmark</p>
            </div>
          </div>

          <div className="md:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <span className="text-xs text-slate-500 font-semibold uppercase">Total Skills</span>
              <p className="text-xl font-bold text-slate-900 mt-1">{profileSummary.skills_count || 0}</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <span className="text-xs text-slate-500 font-semibold uppercase">Projects</span>
              <p className="text-xl font-bold text-slate-900 mt-1">{profileSummary.projects_count || 0}</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <span className="text-xs text-slate-500 font-semibold uppercase">Experience</span>
              <p className="text-xl font-bold text-slate-900 mt-1">{profileSummary.experience_count || 0}</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <span className="text-xs text-slate-500 font-semibold uppercase">Suggestions</span>
              <p className="text-xl font-bold text-amber-600 mt-1">{suggestions.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 5 Dimensional Score Cards */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-600" />
          Dimensional Strength Breakdown
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {dimensionCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className={`text-lg font-black ${getScoreColor(card.score)}`}>
                      {Math.round(card.score)}%
                    </span>
                  </div>
                  <h3 className="font-bold text-gray-900 text-sm">{card.title}</h3>
                  <p className="text-xs text-gray-500 mt-1 leading-snug">{card.desc}</p>
                </div>

                <div className="w-full bg-gray-100 rounded-full h-2 mt-4 overflow-hidden">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getScoreBg(card.score)}`}
                    style={{ width: `${Math.max(5, Math.min(100, card.score))}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actionable Improvement Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2.5">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Actionable Recommendations ({suggestions.length})
              </h2>
              <span className="text-xs text-gray-500">Prioritized by impact</span>
            </div>

            {suggestions.length === 0 ? (
              <div className="p-8 bg-emerald-50 border border-emerald-200 rounded-2xl text-center">
                <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-emerald-900 mb-1">Exceptional Profile Coverage!</h3>
                <p className="text-emerald-700 text-sm max-w-md mx-auto">
                  Your resume effectively covers all key structural criteria including contact info, extensive skills, project implementations, and professional formatting.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {suggestions.map((item, index) => {
                  const isHigh = item.priority === 'High';
                  const isMed = item.priority === 'Medium';
                  return (
                    <div
                      key={index}
                      className={`p-5 rounded-xl border transition-all ${
                        isHigh
                          ? 'bg-rose-50/60 border-rose-200'
                          : isMed
                          ? 'bg-amber-50/60 border-amber-200'
                          : 'bg-blue-50/60 border-blue-200'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isHigh ? 'bg-rose-500' : isMed ? 'bg-amber-500' : 'bg-blue-500'
                            }`}
                          />
                          <h4 className="font-bold text-gray-900 text-sm">{item.category}</h4>
                        </div>
                        <span
                          className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                            isHigh
                              ? 'bg-rose-100 text-rose-800 border-rose-300'
                              : isMed
                              ? 'bg-amber-100 text-amber-800 border-amber-300'
                              : 'bg-blue-100 text-blue-800 border-blue-300'
                          }`}
                        >
                          {item.priority} Priority
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 leading-relaxed pl-4">
                        {item.suggestion}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: ATS Optimization Best Practices */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              ATS Optimization Checklist
            </h3>

            <div className="space-y-3">
              {[
                { title: 'Standard Section Headers', desc: 'Use clear headings like EDUCATION, SKILLS, and WORK EXPERIENCE.' },
                { title: 'Quantified Accomplishments', desc: 'Include numerical metrics, percentages, and volume numbers.' },
                { title: 'Technology Attribution', desc: 'Explicitly label frameworks and libraries under each project.' },
                { title: 'Keyword Consistency', desc: 'Align resume terminology with target job requirements.' },
                { title: 'Clean Single/Double Column', desc: 'Avoid complex nested tables or graphics that hinder PDF text extraction.' }
              ].map((tip, tIdx) => (
                <div key={tIdx} className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-gray-800">{tip.title}</h5>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-snug">{tip.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Links Card */}
          <div className="bg-gradient-to-br from-slate-900 to-indigo-950 rounded-2xl p-6 text-white shadow-md">
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-2">Next Steps</h4>
            <h3 className="text-lg font-bold text-white mb-2">Maximize Match Potential</h3>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              Explore job recommendations tailored to your profile and analyze skill gaps for specific job targets.
            </p>
            <div className="space-y-2">
              <Link
                to={`/recommendations/${fileId}`}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition"
              >
                <span>View Job Recommendations</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
              <Link
                to={`/dashboard/${fileId}`}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-semibold transition border border-white/10"
              >
                <span>Go to Insights Dashboard</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImprovementsPage;
