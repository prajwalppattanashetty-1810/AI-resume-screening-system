import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { getDashboardStats } from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import {
  FileText,
  Briefcase,
  TrendingUp,
  Cpu,
  Layers,
  ArrowRight,
  User,
  Sparkles,
  AlertCircle,
  RefreshCw,
  Search,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Award
} from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#6366F1'];

const DashboardPage = () => {
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
        const res = await getDashboardStats(fileId);
        if (isMounted) {
          setData(res);
        }
      } catch (err) {
        console.error('Failed to load dashboard:', err);
        if (isMounted) {
          setError('Failed to fetch dashboard metrics. Please ensure backend is running.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [fileId]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <LoadingSpinner message="Aggregating platform intelligence and analytics..." />
        <p className="text-gray-500 text-sm mt-3">Compiling real-time dataset distributions and candidate scores...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="p-8 bg-red-50 border border-red-200 rounded-2xl inline-block max-w-lg shadow-sm">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-800 mb-2">Dashboard Error</h2>
          <p className="text-red-700 text-sm mb-6">{error || 'Metrics unavailable.'}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const {
    total_resumes = 0,
    total_jobs = 0,
    avg_resume_score = 0,
    total_skills_catalog = 0,
    category_distribution = [],
    experience_distribution = [],
    work_mode_distribution = [],
    score_distribution = [],
    recent_resumes = [],
    candidate_summary = null
  } = data;

  // Format top 7 categories for clean chart rendering
  const topCategories = category_distribution.slice(0, 7).map(c => ({
    name: c.category.length > 18 ? c.category.substring(0, 16) + '...' : c.category,
    fullName: c.category,
    count: c.count
  }));

  const candidateScores = candidate_summary?.scores || {};

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
                <Layers className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-extrabold text-gray-900">System Analytics Dashboard</h1>
                <p className="text-sm text-gray-500 mt-1">
                  Enterprise recruitment telemetry, ML recommendation metrics & screening benchmarks
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/upload"
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
            >
              Upload Resume <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              to="/jobs"
              className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-1.5"
            >
              Job Explorer <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* 4 High-Level KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
          <div className="p-5 bg-gradient-to-br from-blue-50 to-indigo-50/50 rounded-2xl border border-blue-100 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600">Resumes Analyzed</span>
              <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center text-blue-700">
                <FileText className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-black text-gray-900 mt-2">{total_resumes}</p>
            <p className="text-xs text-blue-600/80 mt-1">Persisted in SQLite database</p>
          </div>

          <div className="p-5 bg-gradient-to-br from-emerald-50 to-teal-50/50 rounded-2xl border border-emerald-100 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600">Active Jobs</span>
              <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700">
                <Briefcase className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-black text-gray-900 mt-2">{total_jobs}</p>
            <p className="text-xs text-emerald-600/80 mt-1">17 technology sectors</p>
          </div>

          <div className="p-5 bg-gradient-to-br from-amber-50 to-orange-50/50 rounded-2xl border border-amber-100 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-600">Average ATS Score</span>
              <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center text-amber-700">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-black text-gray-900 mt-2">{avg_resume_score}%</p>
            <p className="text-xs text-amber-600/80 mt-1">Across all candidates</p>
          </div>

          <div className="p-5 bg-gradient-to-br from-purple-50 to-pink-50/50 rounded-2xl border border-purple-100 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-purple-600">Skills Catalog</span>
              <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center text-purple-700">
                <Cpu className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-black text-gray-900 mt-2">{total_skills_catalog}</p>
            <p className="text-xs text-purple-600/80 mt-1">Unique industry technologies</p>
          </div>
        </div>
      </div>

      {/* Candidate Spotlight (When fileId is active) */}
      {candidate_summary && (
        <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-md mb-8 border border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400">
                <User className="w-7 h-7" />
              </div>
              <div>
                <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30 mb-1">
                  Active Candidate Focus
                </span>
                <h2 className="text-2xl font-black text-white">{candidate_summary.name}</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  ID: {candidate_summary.file_id} {candidate_summary.email && `| ${candidate_summary.email}`}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <Link
                to={`/analysis/${candidate_summary.file_id}`}
                className="px-3.5 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-semibold transition border border-white/10"
              >
                Profile Analysis
              </Link>
              <Link
                to={`/recommendations/${candidate_summary.file_id}`}
                className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                Recommendations
              </Link>
              <Link
                to={`/skills/${candidate_summary.file_id}`}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                Skills Matrix
              </Link>
              <Link
                to={`/improvements/${candidate_summary.file_id}`}
                className="px-3.5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                Improvements
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mt-6">
            <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-center">
              <span className="text-xs text-slate-400 uppercase font-semibold">Overall ATS</span>
              <p className="text-2xl font-black text-emerald-400 mt-1">
                {Math.round(candidateScores.overall ?? 0)}%
              </p>
            </div>
            <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-center">
              <span className="text-xs text-slate-400 uppercase font-semibold">Skills Score</span>
              <p className="text-2xl font-black text-indigo-400 mt-1">
                {Math.round(candidateScores.skills ?? 0)}%
              </p>
            </div>
            <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-center">
              <span className="text-xs text-slate-400 uppercase font-semibold">Projects</span>
              <p className="text-2xl font-black text-blue-400 mt-1">
                {Math.round(candidateScores.projects ?? 0)}%
              </p>
            </div>
            <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-center">
              <span className="text-xs text-slate-400 uppercase font-semibold">Experience</span>
              <p className="text-2xl font-black text-amber-400 mt-1">
                {Math.round(candidateScores.experience ?? 0)}%
              </p>
            </div>
            <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-center col-span-2 sm:col-span-1">
              <span className="text-xs text-slate-400 uppercase font-semibold">Completeness</span>
              <p className="text-2xl font-black text-teal-400 mt-1">
                {Math.round(candidateScores.completeness ?? 0)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Chart 1: Job Categories Distribution */}
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Job Dataset Distribution</h2>
              <p className="text-xs text-gray-500">Top employment sectors by active listings</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200">
              Phase 5
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topCategories} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val, name, props) => [val, props.payload.fullName]}
                  contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Resume Score Bands */}
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Resume Quality Distribution</h2>
              <p className="text-xs text-gray-500">Candidate score brackets across database</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-200">
              Phase 8
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={score_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="band" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#10B981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Work Modes & Experience Levels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-base font-bold text-gray-900 mb-1">Work Modes</h3>
          <p className="text-xs text-gray-500 mb-4">Workplace arrangement breakdown</p>

          <div className="h-60 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={work_mode_distribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  dataKey="count"
                  nameKey="mode"
                  label={({ mode, percent }) => `${mode} (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {work_mode_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-base font-bold text-gray-900 mb-1">Experience Levels</h3>
          <p className="text-xs text-gray-500 mb-4">Required seniority distributions</p>

          <div className="h-60 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={experience_distribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  dataKey="count"
                  nameKey="level"
                  label={({ level, percent }) => `${level} (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {experience_distribution.map((entry, index) => (
                    <Cell key={`cell-exp-${index}`} fill={COLORS[(index + 3) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Resumes Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Recently Processed Resumes ({recent_resumes.length})
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">Historical candidates parsed by NLP Information Extraction</p>
          </div>

          <Link
            to="/upload"
            className="px-3.5 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-xl text-xs font-semibold transition border border-blue-200 w-fit"
          >
            + Upload New
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-slate-50 text-xs font-bold text-slate-700 uppercase tracking-wider border-b border-gray-200">
              <tr>
                <th className="px-6 py-4">Candidate / File</th>
                <th className="px-6 py-4">ATS Score</th>
                <th className="px-6 py-4">Skills Extracted</th>
                <th className="px-6 py-4">Analyzed At</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {recent_resumes.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500 italic">
                    No resumes analyzed yet. Upload a PDF resume to get started.
                  </td>
                </tr>
              ) : (
                recent_resumes.map((item, idx) => {
                  const score = item.score !== null ? Math.round(item.score) : 75;
                  const isCurrent = item.file_id === fileId;
                  return (
                    <tr
                      key={idx}
                      className={`hover:bg-slate-50/80 transition ${
                        isCurrent ? 'bg-blue-50/40 font-medium' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                            {item.name ? item.name.charAt(0) : 'R'}
                          </div>
                          <div>
                            <span className="font-bold text-gray-900 block">{item.name}</span>
                            <span className="text-xs text-gray-400 block font-mono">
                              {item.file_id.substring(0, 8)}...
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                            score >= 80
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : score >= 60
                              ? 'bg-amber-50 text-amber-700 border-amber-200'
                              : 'bg-rose-50 text-rose-700 border-rose-200'
                          }`}
                        >
                          {score}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md">
                          {item.skills_count} skills
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-gray-500">
                        {item.created_at || 'Recent'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/dashboard/${item.file_id}`}
                            className="text-xs font-semibold text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50 transition"
                          >
                            Focus
                          </Link>
                          <Link
                            to={`/analysis/${item.file_id}`}
                            className="text-xs font-semibold text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-100 transition"
                          >
                            Profile
                          </Link>
                          <Link
                            to={`/recommendations/${item.file_id}`}
                            className="text-xs font-semibold text-emerald-600 hover:text-emerald-800 px-2 py-1 rounded hover:bg-emerald-50 transition"
                          >
                            Jobs
                          </Link>
                          <Link
                            to={`/improvements/${item.file_id}`}
                            className="text-xs font-semibold text-amber-600 hover:text-amber-800 px-2 py-1 rounded hover:bg-amber-50 transition"
                          >
                            Tips
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
