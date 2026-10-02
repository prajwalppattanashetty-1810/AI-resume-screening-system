import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Target,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  XCircle,
  ArrowLeft,
  ArrowRight,
  Sparkles,
  BookOpen,
  Code,
  Clock,
  ExternalLink,
  Award,
  Layers,
  Briefcase,
  Building2,
  MapPin,
  TrendingUp,
  ShieldCheck,
  ChevronRight,
  Filter,
  RefreshCw,
  Info
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { analyzeSkillGap } from '../services/api';

const SkillGapPage = () => {
  const { fileId, jobId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  // Filter States
  const [activeTab, setActiveTab] = useState('required'); // 'required' | 'preferred' | 'all'
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'matched' | 'partial' | 'missing'
  const [priorityFilter, setPriorityFilter] = useState('all'); // 'all' | 'High' | 'Medium' | 'Low'
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch skill gap data
  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      if (!fileId || !jobId) {
        setError('Missing resume file ID or job ID.');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await analyzeSkillGap(fileId, jobId);
        if (isMounted) {
          setAnalysisData(data);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          console.error('Skill gap fetch error:', err);
          const detail = err.response?.data?.detail || err.message || 'Failed to analyze skill gap.';
          setError(detail);
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [fileId, jobId]);

  // Filtered Skill Items
  const filteredSkillItems = useMemo(() => {
    if (!analysisData) return [];

    let pool = [];
    if (activeTab === 'required') {
      pool = analysisData.required_skills_analysis || [];
    } else if (activeTab === 'preferred') {
      pool = analysisData.preferred_skills_analysis || [];
    } else {
      pool = [
        ...(analysisData.required_skills_analysis || []),
        ...(analysisData.preferred_skills_analysis || [])
      ];
    }

    return pool.filter((item) => {
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
      const matchesSearch =
        !searchQuery ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [analysisData, activeTab, statusFilter, searchQuery]);

  // Filtered Learning Recommendations
  const filteredRecommendations = useMemo(() => {
    if (!analysisData) return [];
    const recs = analysisData.learning_recommendations || [];

    return recs.filter((rec) => {
      const matchesPriority = priorityFilter === 'all' || rec.priority === priorityFilter;
      const matchesSearch =
        !searchQuery ||
        rec.skill_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rec.category.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesPriority && matchesSearch;
    });
  }, [analysisData, priorityFilter, searchQuery]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center py-20">
        <LoadingSpinner message="Evaluating skill compatibility and generating personalized learning roadmap..." />
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-slate-50 py-16 px-4">
        <div className="max-w-2xl mx-auto bg-white rounded-2xl p-8 border border-red-200 shadow-sm text-center">
          <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Skill Gap Analysis Failed</h2>
          <p className="text-slate-600 text-sm mb-6">{error || 'Unable to retrieve analysis details.'}</p>
          <div className="flex justify-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold rounded-xl transition"
            >
              Go Back
            </button>
            <Link
              to={`/recommendations/${fileId}`}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition"
            >
              Back to Recommendations
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { metrics } = analysisData;

  // Rating badge helper
  const getCoverageBadge = (pct) => {
    if (pct >= 80) {
      return {
        label: 'Strong Match',
        bg: 'bg-emerald-50',
        text: 'text-emerald-700',
        border: 'border-emerald-200',
        meter: 'bg-emerald-500'
      };
    }
    if (pct >= 50) {
      return {
        label: 'Moderate Match',
        bg: 'bg-amber-50',
        text: 'text-amber-700',
        border: 'border-amber-200',
        meter: 'bg-amber-500'
      };
    }
    return {
      label: 'Skill Gap Detected',
      bg: 'bg-rose-50',
      text: 'text-rose-700',
      border: 'border-rose-200',
      meter: 'bg-rose-500'
    };
  };

  const badgeStyle = getCoverageBadge(metrics.overall_coverage_percentage);

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Navigation Breadcrumb / Top Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Link
              to={`/recommendations/${fileId}`}
              className="inline-flex items-center gap-1.5 text-slate-600 hover:text-indigo-600 font-semibold transition"
            >
              <ArrowLeft className="w-4 h-4" />
              Recommendations
            </Link>
            <span>/</span>
            <span className="text-slate-900 font-medium">Skill Gap Analysis</span>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to={`/skills/${fileId}`}
              className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-xs transition inline-flex items-center gap-1.5"
            >
              <Layers className="w-3.5 h-3.5 text-indigo-600" />
              Candidate Skills Matrix
            </Link>
            <Link
              to={`/improvements/${fileId}`}
              className="px-3 py-1.5 bg-amber-50 border border-amber-200 hover:bg-amber-100 text-amber-800 text-xs font-semibold rounded-lg shadow-xs transition inline-flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              Improvements
            </Link>
            <Link
              to="/jobs"
              className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-xs transition inline-flex items-center gap-1.5"
            >
              <Briefcase className="w-3.5 h-3.5 text-slate-500" />
              Job Explorer
            </Link>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* A. HEADER SECTION: Role Overview & Candidate Fit */}
        {/* ==================================================================== */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            {/* Left: Role Info */}
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-bold rounded-md">
                  {analysisData.job_id}
                </span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-md">
                  {analysisData.category}
                </span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded-md">
                  {analysisData.experience_level}
                </span>
              </div>

              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  {analysisData.job_title}
                </h1>
                <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 mt-1.5">
                  <span className="flex items-center gap-1 font-medium text-slate-800">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    {analysisData.company}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    {analysisData.location}
                  </span>
                  {analysisData.candidate_name && (
                    <>
                      <span>•</span>
                      <span className="text-indigo-600 font-semibold">
                        Candidate: {analysisData.candidate_name}
                      </span>
                    </>
                  )}
                </div>
              </div>

              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-3xl">
                {analysisData.summary}
              </p>
            </div>

            {/* Right: Overall Coverage Badge */}
            <div className="shrink-0 flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t lg:border-t-0 lg:border-l border-slate-100 pt-4 lg:pt-0 lg:pl-8">
              <div className="text-left sm:text-right">
                <span className="text-xs uppercase font-bold text-slate-400 tracking-wider block">
                  Overall Skill Fit
                </span>
                <div className="text-3xl sm:text-4xl font-black text-slate-900 leading-tight">
                  {metrics.overall_coverage_percentage}%
                </div>
              </div>
              <div
                className={`mt-2 px-3 py-1 rounded-full text-xs font-bold border inline-flex items-center gap-1.5 ${badgeStyle.bg} ${badgeStyle.text} ${badgeStyle.border}`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                {badgeStyle.label}
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* B. SKILL GAP OVERVIEW STAT CARDS */}
        {/* ==================================================================== */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Matched Required Skills */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-100">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 leading-none">
                {metrics.matched_required}
                <span className="text-xs text-slate-400 font-normal"> / {metrics.total_required}</span>
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Matched Required</div>
            </div>
          </div>

          {/* Partial Skills */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 border border-amber-100">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 leading-none">
                {metrics.partial_required + metrics.partial_preferred}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Partial / Transferable</div>
            </div>
          </div>

          {/* Missing Skills */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0 border border-rose-100">
              <XCircle className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 leading-none">
                {metrics.missing_required + metrics.missing_preferred}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Skills to Develop</div>
            </div>
          </div>

          {/* Required Skill Match % */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 border border-indigo-100">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-indigo-700 leading-none">
                {metrics.required_match_percentage}%
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Required Match %</div>
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* D. SKILL COVERAGE VISUALIZATION BARS */}
        {/* ==================================================================== */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-600" />
              Skill Qualification Breakdown
            </h3>
            <span className="text-xs text-slate-400">
              Weighted Formula: 75% Required + 25% Preferred
            </span>
          </div>

          <div className="space-y-4">
            {/* Required Skills Progress */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">
                  Required Skill Requirements ({metrics.matched_required} of {metrics.total_required} met)
                </span>
                <span className="font-bold text-slate-900">{metrics.required_match_percentage}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-indigo-600 h-full rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${Math.min(100, Math.max(0, metrics.required_match_percentage))}%` }}
                />
              </div>
            </div>

            {/* Preferred Skills Progress */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">
                  Preferred / Bonus Qualifications ({metrics.matched_preferred} of {metrics.total_preferred} met)
                </span>
                <span className="font-bold text-slate-900">{metrics.preferred_coverage_percentage}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-purple-600 h-full rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${Math.min(100, Math.max(0, metrics.preferred_coverage_percentage))}%` }}
                />
              </div>
            </div>

            {/* Overall Progress */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Overall Qualification Readiness</span>
                <span className="font-bold text-slate-900">{metrics.overall_coverage_percentage}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${badgeStyle.meter}`}
                  style={{ width: `${Math.min(100, Math.max(0, metrics.overall_coverage_percentage))}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* C. SKILL COMPARISON SECTION */}
        {/* ==================================================================== */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          {/* Section Header with Tabs & Filters */}
          <div className="p-6 border-b border-slate-200 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Target className="w-5 h-5 text-indigo-600" />
                  Skill-by-Skill Requirements Audit
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Canonical comparison against candidate resume evidence and proficiency classifications.
                </p>
              </div>

              {/* Requirement Type Tabs */}
              <div className="flex p-1 bg-slate-100 rounded-xl text-xs font-semibold text-slate-600 shrink-0">
                <button
                  onClick={() => setActiveTab('required')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    activeTab === 'required'
                      ? 'bg-white text-indigo-700 shadow-xs'
                      : 'hover:text-slate-900'
                  }`}
                >
                  Required ({metrics.total_required})
                </button>
                <button
                  onClick={() => setActiveTab('preferred')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    activeTab === 'preferred'
                      ? 'bg-white text-indigo-700 shadow-xs'
                      : 'hover:text-slate-900'
                  }`}
                >
                  Preferred ({metrics.total_preferred})
                </button>
                <button
                  onClick={() => setActiveTab('all')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    activeTab === 'all'
                      ? 'bg-white text-indigo-700 shadow-xs'
                      : 'hover:text-slate-900'
                  }`}
                >
                  All ({metrics.total_required + metrics.total_preferred})
                </button>
              </div>
            </div>

            {/* Filter Pills */}
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <span className="text-xs text-slate-400 flex items-center gap-1 font-medium mr-1">
                <Filter className="w-3.5 h-3.5" /> Filter:
              </span>
              {[
                { id: 'all', label: 'All Statuses' },
                { id: 'matched', label: '✓ Matched' },
                { id: 'partial', label: '▲ Partial' },
                { id: 'missing', label: '✕ Missing' }
              ].map((btn) => (
                <button
                  key={btn.id}
                  onClick={() => setStatusFilter(btn.id)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium border transition ${
                    statusFilter === btn.id
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>

          {/* Skill Items List */}
          <div className="divide-y divide-slate-100">
            {filteredSkillItems.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs italic">
                No skills match your active filters.
              </div>
            ) : (
              filteredSkillItems.map((item, idx) => {
                const isMatched = item.status === 'matched';
                const isPartial = item.status === 'partial';
                const isMissing = item.status === 'missing';

                return (
                  <div
                    key={idx}
                    className="p-4 sm:p-5 hover:bg-slate-50/70 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                  >
                    <div className="space-y-1.5 max-w-2xl">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">{item.name}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-sm bg-slate-100 text-slate-600 font-medium">
                          {item.category.replace('_', ' ')}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-sm bg-slate-100 text-slate-500 uppercase tracking-wider font-semibold">
                          {item.requirement_type}
                        </span>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed">{item.reason}</p>

                      {/* Evidence / Transferable info snippet */}
                      {item.proficiency_evidence && item.proficiency_evidence.length > 0 && (
                        <div className="text-[11px] text-slate-500 bg-slate-100/70 p-2 rounded-lg border border-slate-200/50">
                          <strong className="text-slate-700">Extracted Context:</strong>{' '}
                          {item.proficiency_evidence[0]}
                        </div>
                      )}
                    </div>

                    {/* Status Badge */}
                    <div className="shrink-0 flex items-center sm:flex-col sm:items-end gap-2">
                      {isMatched && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-bold">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Matched
                        </span>
                      )}
                      {isPartial && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-full text-xs font-bold">
                          <AlertCircle className="w-3.5 h-3.5" />
                          Partial Match
                        </span>
                      )}
                      {isMissing && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-50 text-rose-700 border border-rose-200 rounded-full text-xs font-bold">
                          <XCircle className="w-3.5 h-3.5" />
                          Missing
                        </span>
                      )}

                      {item.current_proficiency && (
                        <span className="text-[11px] text-slate-500 font-medium">
                          Level: {item.current_proficiency}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* ==================================================================== */}
        {/* E. PERSONALIZED LEARNING ROADMAP SECTION */}
        {/* ==================================================================== */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                  Personalized Learning Roadmap
                </h2>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Targeted upskilling curriculum structured by priority to maximize qualification readiness.
              </p>
            </div>

            {/* Priority Filter Buttons */}
            <div className="flex flex-wrap items-center gap-1.5">
              {[
                { id: 'all', label: 'All Priorities' },
                { id: 'High', label: '🔥 High Priority' },
                { id: 'Medium', label: '⚡ Medium Priority' },
                { id: 'Low', label: '📘 Low Priority' }
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPriorityFilter(p.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
                    priorityFilter === p.id
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Recommendation Cards Grid */}
          {filteredRecommendations.length === 0 ? (
            <div className="p-12 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
              <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-800">No Learning Gaps in this Filter</h4>
              <p className="text-xs text-slate-500 mt-1">
                You satisfy all requirements under the selected priority level.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredRecommendations.map((rec, idx) => {
                const isHigh = rec.priority === 'High';
                const isMedium = rec.priority === 'Medium';

                const priorityBadge = isHigh
                  ? 'bg-rose-50 text-rose-700 border-rose-200'
                  : isMedium
                  ? 'bg-amber-50 text-amber-800 border-amber-200'
                  : 'bg-blue-50 text-blue-700 border-blue-200';

                return (
                  <div
                    key={idx}
                    className="bg-white rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition p-5 sm:p-6 flex flex-col justify-between space-y-4"
                  >
                    <div className="space-y-3">
                      {/* Top Header */}
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-bold text-slate-900">{rec.skill_name}</h3>
                            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-sm bg-slate-100 text-slate-600">
                              {rec.category.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-2">
                            <span>Target: <strong className="text-slate-800">{rec.target_proficiency}</strong></span>
                            {rec.current_proficiency && (
                              <>
                                <span>•</span>
                                <span>Current: <strong className="text-slate-700">{rec.current_proficiency}</strong></span>
                              </>
                            )}
                          </div>
                        </div>

                        {/* Priority Badge */}
                        <div className="shrink-0 flex items-center gap-1.5">
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-bold border ${priorityBadge}`}
                          >
                            {rec.priority} Priority
                          </span>
                        </div>
                      </div>

                      {/* Reason Quote */}
                      <p className="text-xs text-slate-600 italic bg-slate-50 p-2.5 rounded-xl border border-slate-100 leading-relaxed">
                        "{rec.reason}"
                      </p>

                      {/* Learning Topics */}
                      {rec.learning_topics && rec.learning_topics.length > 0 && (
                        <div>
                          <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                            <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
                            Core Syllabus & Focus Topics
                          </span>
                          <ul className="space-y-1 text-xs text-slate-600 list-inside">
                            {rec.learning_topics.map((top, tIdx) => (
                              <li key={tIdx} className="flex items-start gap-1.5">
                                <span className="text-indigo-500 font-bold shrink-0 mt-0.5">•</span>
                                <span className="leading-relaxed">{top}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Project Ideas */}
                      {rec.project_ideas && rec.project_ideas.length > 0 && (
                        <div>
                          <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                            <Code className="w-3.5 h-3.5 text-emerald-600" />
                            Practical Project Exercise
                          </span>
                          <div className="bg-emerald-50/50 border border-emerald-100 p-2.5 rounded-xl text-xs text-emerald-900 leading-relaxed">
                            {rec.project_ideas[0]}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Card Footer: Duration & Official Resources */}
                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3 text-xs">
                      <div className="flex items-center gap-1.5 text-slate-500 font-medium">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>Est. Duration: <strong className="text-slate-700">{rec.estimated_duration}</strong></span>
                      </div>

                      {rec.resources && rec.resources.length > 0 && rec.resources[0].url ? (
                        <a
                          href={rec.resources[0].url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-semibold hover:underline"
                        >
                          Official Docs
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-slate-400 italic text-[11px]">Curriculum Guide</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Bottom Navigation */}
        <div className="flex justify-between items-center pt-4">
          <Link
            to={`/recommendations/${fileId}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-semibold rounded-xl shadow-xs transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Recommendations
          </Link>

          <Link
            to={`/skills/${fileId}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl shadow-xs transition"
          >
            Explore Full Skills Matrix
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SkillGapPage;
