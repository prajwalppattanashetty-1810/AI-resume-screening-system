import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Sparkles,
  Briefcase,
  Building2,
  MapPin,
  Clock,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Filter,
  SlidersHorizontal,
  RefreshCw,
  ExternalLink,
  ArrowRight,
  TrendingUp,
  Award,
  Layers,
  Info,
  Laptop,
  Target
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { getRecommendations, getJobCategories } from '../services/api';

const LOCATIONS = [
  'All',
  'Bengaluru, Karnataka',
  'Hyderabad, Telangana',
  'Pune, Maharashtra',
  'Gurugram, Haryana',
  'Noida, Uttar Pradesh',
  'Chennai, Tamil Nadu',
  'Mumbai, Maharashtra',
  'Remote - India',
  'Remote - Global'
];

const RecommendationsPage = () => {
  const { fileId } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [totalJobsAnalyzed, setTotalJobsAnalyzed] = useState(0);
  const [candidateSkillsUsed, setCandidateSkillsUsed] = useState([]);
  const [disclaimer, setDisclaimer] = useState('');

  // Filters
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedLocation, setSelectedLocation] = useState('All');
  const [topN, setTopN] = useState(10);
  const [expandedJobId, setExpandedJobId] = useState(null);

  // Fetch Categories on mount
  useEffect(() => {
    const fetchCats = async () => {
      try {
        const catData = await getJobCategories();
        setCategories(catData || []);
      } catch (err) {
        console.warn('Failed to fetch categories:', err);
      }
    };
    fetchCats();
  }, []);

  // Fetch Recommendations
  useEffect(() => {
    let isMounted = true;

    const fetchRecs = async () => {
      if (!fileId) {
        setLoading(false);
        setError('No resume file ID provided. Please upload or analyze a resume first.');
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const params = {
          file_id: fileId,
          top_n: topN,
          tfidf_weight: 0.7,
          skill_weight: 0.3
        };

        if (selectedCategory !== 'All') params.category = selectedCategory;
        if (selectedLocation !== 'All') params.location = selectedLocation;

        const data = await getRecommendations(params);

        if (isMounted) {
          setRecommendations(data.recommendations || []);
          setTotalJobsAnalyzed(data.total_jobs_analyzed || 0);
          setCandidateSkillsUsed(data.candidate_skills_used || []);
          setDisclaimer(data.disclaimer || '');
          if (data.recommendations && data.recommendations.length > 0) {
            setExpandedJobId(data.recommendations[0].job_id);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
            'Failed to generate job recommendations. Please verify the backend is running.'
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchRecs();

    return () => {
      isMounted = false;
    };
  }, [fileId, selectedCategory, selectedLocation, topN]);

  const toggleExpand = (jobId) => {
    setExpandedJobId((prev) => (prev === jobId ? null : jobId));
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
    if (score >= 50) return 'text-indigo-700 bg-indigo-50 border-indigo-200';
    if (score >= 30) return 'text-amber-700 bg-amber-50 border-amber-200';
    return 'text-rose-700 bg-rose-50 border-rose-200';
  };

  const getWorkModeBadge = (mode) => {
    switch (mode) {
      case 'Remote':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Hybrid':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'On-site':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-8 mb-8 shadow-sm border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 bg-indigo-500/20 border border-indigo-400/30 px-3 py-1 rounded-full text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-3">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Phase 6: AI Job Recommendation Engine
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight">Personalized Career Matches</h1>
            <p className="text-slate-300 text-sm mt-2 max-w-2xl leading-relaxed">
              Powered by hybrid machine learning: <strong>TF-IDF vector cosine similarity (70%)</strong> and{' '}
              <strong>required technical skill coverage (30%)</strong>. Ranked against our verified job database.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {fileId && (
              <Link
                to={`/improvements/${fileId}`}
                className="inline-flex items-center gap-1.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/40 px-3.5 py-2 rounded-xl text-xs font-bold text-amber-300 transition"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Improvements
              </Link>
            )}
            {fileId && (
              <Link
                to={`/skills/${fileId}`}
                className="inline-flex items-center gap-1.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-200 transition"
              >
                <Layers className="w-3.5 h-3.5 text-indigo-400" /> Skills Matrix
              </Link>
            )}
            {fileId && (
              <Link
                to={`/dashboard/${fileId}`}
                className="inline-flex items-center gap-1.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-200 transition"
              >
                Dashboard
              </Link>
            )}
            {fileId && (
              <Link
                to={`/analysis/${fileId}`}
                className="inline-flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-2 rounded-xl text-xs font-semibold transition shadow-sm"
              >
                Analysis <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>
        </div>

        {/* Candidate Skills Used Strip */}
        {candidateSkillsUsed && candidateSkillsUsed.length > 0 && (
          <div className="mt-6 pt-6 border-t border-slate-800">
            <p className="text-xs text-slate-400 font-medium mb-2 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-indigo-400" />
              Matched using {candidateSkillsUsed.length} extracted candidate skills:
            </p>
            <div className="flex flex-wrap gap-1.5 max-h-16 overflow-y-auto pr-2">
              {candidateSkillsUsed.map((skill, idx) => (
                <span
                  key={idx}
                  className="bg-indigo-900/40 border border-indigo-700/50 text-indigo-200 text-[11px] px-2.5 py-0.5 rounded-full font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer / Model Metrics */}
        <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-slate-500" />
            Analyzed {totalJobsAnalyzed} database jobs • Formula: 70% TF-IDF Cosine + 30% Skill Match
          </span>
          <span className="italic text-[11px] text-slate-500">
            Experimental matching score for exploratory recommendations. Not a hiring guarantee.
          </span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 mb-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Filter className="w-4 h-4 text-indigo-600" /> Filter Recommendations
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full md:w-auto">
            {/* Category Filter */}
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                <option value="All">All Categories ({totalJobsAnalyzed})</option>
                {categories.map((c) => (
                  <option key={c.category} value={c.category}>
                    {c.category}
                  </option>
                ))}
              </select>
            </div>

            {/* Location Filter */}
            <div>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                {LOCATIONS.map((loc) => (
                  <option key={loc} value={loc}>
                    {loc}
                  </option>
                ))}
              </select>
            </div>

            {/* Top N */}
            <div>
              <select
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                <option value={5}>Top 5 Recommendations</option>
                <option value={10}>Top 10 Recommendations</option>
                <option value={15}>Top 15 Recommendations</option>
                <option value={20}>Top 20 Recommendations</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main State Handling */}
      {loading ? (
        <div className="py-24 text-center">
          <LoadingSpinner message="Calculating TF-IDF vectors and ranking matches..." />
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center max-w-lg mx-auto">
          <AlertCircle className="w-10 h-10 text-red-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-red-900 mb-1">Recommendation Error</h3>
          <p className="text-xs text-red-700 mb-5">{error}</p>
          <div className="flex justify-center gap-3">
            <Link
              to="/upload"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
            >
              Upload Resume
            </Link>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-50 transition"
            >
              Retry
            </button>
          </div>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-md mx-auto">
          <Briefcase className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800 mb-1">No Matching Jobs Found</h3>
          <p className="text-xs text-slate-500 mb-5">
            No job records match the selected category or location filters for your resume.
          </p>
          <button
            onClick={() => {
              setSelectedCategory('All');
              setSelectedLocation('All');
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between px-1">
            <p className="text-xs font-semibold text-slate-500">
              Showing top <strong className="text-slate-800">{recommendations.length}</strong> ranked
              job opportunities
            </p>
            <span className="text-xs text-slate-400 font-mono">Sorted by Combined Match Score</span>
          </div>

          {/* Recommendations List */}
          <div className="space-y-5">
            {recommendations.map((rec, rankIdx) => {
              const isExpanded = expandedJobId === rec.job_id;
              const rank = rankIdx + 1;

              return (
                <div
                  key={rec.job_id}
                  className="bg-white rounded-2xl border border-slate-200/90 hover:border-slate-300 shadow-xs transition overflow-hidden"
                >
                  {/* Card Header & Primary Info */}
                  <div className="p-6">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      {/* Left: Title, Company, Meta */}
                      <div className="flex items-start gap-3.5">
                        <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 font-black text-sm flex items-center justify-center shrink-0 mt-0.5">
                          #{rank}
                        </div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h2 className="text-lg font-bold text-slate-900 hover:text-indigo-600 transition">
                              {rec.title}
                            </h2>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                              {rec.job_id}
                            </span>
                          </div>

                          <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-600">
                            <span className="font-semibold flex items-center gap-1.5 text-slate-800">
                              <Building2 className="w-3.5 h-3.5 text-indigo-600" />
                              {rec.company}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1 text-slate-500">
                              <MapPin className="w-3.5 h-3.5 text-slate-400" />
                              {rec.location}
                            </span>
                            <span>•</span>
                            <span
                              className={`px-2 py-0.5 rounded-sm text-[10px] font-medium border ${getWorkModeBadge(
                                rec.work_mode
                              )}`}
                            >
                              {rec.work_mode}
                            </span>
                            {rec.salary_range && (
                              <>
                                <span>•</span>
                                <span className="text-emerald-700 font-semibold">{rec.salary_range}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right: Score Badges & Skill Gap Action */}
                      <div className="flex flex-col sm:flex-row items-end sm:items-center gap-3 shrink-0">
                        {/* Analyze Skill Gap Button */}
                        <Link
                          to={`/skill-gap/${fileId}/${rec.job?.job_id || rec.job_id}`}
                          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition hover:scale-[1.02]"
                        >
                          <Target className="w-3.5 h-3.5" />
                          <span>Analyze Skill Gap</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>

                        {/* Overall Combined Score Pill */}
                        <div
                          className={`px-4 py-2 rounded-2xl border text-center font-black ${getScoreColor(
                            rec.match_score
                          )}`}
                        >
                          <div className="text-2xl leading-none">{rec.match_score}%</div>
                          <div className="text-[10px] uppercase font-bold tracking-wider mt-1">
                            Match Score
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Metric Breakdown Strip */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-5 bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                          TF-IDF Similarity
                        </span>
                        <span className="font-bold text-slate-800">
                          {(rec.tfidf_similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                          Required Skill Match
                        </span>
                        <span className="font-bold text-indigo-700">
                          {rec.skill_match_percentage.toFixed(0)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                          Category
                        </span>
                        <span className="font-medium text-slate-800">{rec.category}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                          Experience Level
                        </span>
                        <span className="font-medium text-slate-800">{rec.experience_level}</span>
                      </div>
                    </div>

                    {/* Explanation Box */}
                    {rec.explanation && (
                      <div className="mt-4 p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl text-xs text-indigo-900 leading-relaxed flex items-start gap-2.5">
                        <Sparkles className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                        <div>
                          <strong className="font-semibold">Why this matches:</strong> {rec.explanation}
                        </div>
                      </div>
                    )}

                    {/* Skills Summary Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5 pt-5 border-t border-slate-100">
                      {/* Matched Required Skills */}
                      <div>
                        <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          Matched Skills ({rec.matched_skills?.length || 0})
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {rec.matched_skills && rec.matched_skills.length > 0 ? (
                            rec.matched_skills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] px-2 py-0.5 rounded-md font-medium"
                              >
                                {skill}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-400 italic">No direct skill overlap</span>
                          )}
                        </div>
                      </div>

                      {/* Missing Required Skills */}
                      <div>
                        <span className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                          Missing Skills ({rec.missing_skills?.length || 0})
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {rec.missing_skills && rec.missing_skills.length > 0 ? (
                            rec.missing_skills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-amber-50 text-amber-800 border border-amber-200 text-[11px] px-2 py-0.5 rounded-md font-medium"
                              >
                                {skill}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-emerald-600 font-medium">All required skills met!</span>
                          )}
                        </div>
                      </div>

                      {/* Preferred Skill Matches */}
                      <div>
                        <span className="text-xs font-bold text-purple-800 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                          <Award className="w-3.5 h-3.5 text-purple-600" />
                          Preferred Bonus ({rec.preferred_skill_matches?.length || 0})
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {rec.preferred_skill_matches && rec.preferred_skill_matches.length > 0 ? (
                            rec.preferred_skill_matches.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-purple-50 text-purple-800 border border-purple-200 text-[11px] px-2 py-0.5 rounded-md font-medium"
                              >
                                {skill}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-400 italic">No preferred matches</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Action Bar */}
                  <div className="w-full py-2.5 px-6 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <button
                      onClick={() => toggleExpand(rec.job_id)}
                      className="font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition"
                    >
                      <span>
                        {isExpanded ? 'Hide Full Role Description & Duties' : 'View Full Job Overview & Responsibilities'}
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      )}
                    </button>

                    <Link
                      to={`/skill-gap/${fileId}/${rec.job?.job_id || rec.job_id}`}
                      className="font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 transition"
                    >
                      <Target className="w-3.5 h-3.5" />
                      Detailed Skill Gap Roadmap
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>

                  {/* Expanded Role Details */}
                  {isExpanded && rec.job && (
                    <div className="p-6 bg-slate-50/70 border-t border-slate-200 space-y-5 text-xs text-slate-700 animate-fadeIn">
                      {/* Responsibilities */}
                      {rec.job.responsibilities && rec.job.responsibilities.length > 0 && (
                        <div>
                          <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">
                            Key Responsibilities
                          </h4>
                          <ul className="space-y-1.5 list-disc list-inside text-slate-600">
                            {rec.job.responsibilities.map((resp, idx) => (
                              <li key={idx} className="leading-relaxed">
                                {resp}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Description Markdown Overview */}
                      <div>
                        <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">
                          Complete Position Overview
                        </h4>
                        <div className="bg-white p-4 rounded-xl border border-slate-200 text-slate-600 leading-relaxed whitespace-pre-line font-sans">
                          {rec.job.description}
                        </div>
                      </div>

                      {/* Education & Employment */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                        <div>
                          <span className="font-semibold text-slate-800">Education Requirement:</span>{' '}
                          {rec.job.education || "Bachelor's Degree"}
                        </div>
                        <div>
                          <span className="font-semibold text-slate-800">Employment Type:</span>{' '}
                          {rec.job.employment_type || 'Full-time'}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;
