import { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { extractSkills, analyzeResume } from '../services/api';
import {
  Code2,
  Database,
  Server,
  Cpu,
  Cloud,
  Wrench,
  HeartHandshake,
  Layout,
  Search,
  CheckCircle2,
  Sparkles,
  ArrowLeft,
  FileText,
  Briefcase,
  FolderGit2,
  AlertCircle,
  HelpCircle,
  X,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

const CATEGORY_CONFIG = {
  programming_languages: {
    label: 'Programming Languages',
    icon: Code2,
    color: 'blue',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
    badge: 'bg-blue-100 text-blue-800'
  },
  frontend: {
    label: 'Frontend Development',
    icon: Layout,
    color: 'cyan',
    bg: 'bg-cyan-50',
    border: 'border-cyan-200',
    text: 'text-cyan-700',
    badge: 'bg-cyan-100 text-cyan-800'
  },
  backend: {
    label: 'Backend Frameworks',
    icon: Server,
    color: 'emerald',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
    badge: 'bg-emerald-100 text-emerald-800'
  },
  databases: {
    label: 'Databases & Storage',
    icon: Database,
    color: 'amber',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    badge: 'bg-amber-100 text-amber-800'
  },
  machine_learning: {
    label: 'Machine Learning & AI',
    icon: Cpu,
    color: 'purple',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    text: 'text-purple-700',
    badge: 'bg-purple-100 text-purple-800'
  },
  cloud_devops: {
    label: 'Cloud & DevOps',
    icon: Cloud,
    color: 'sky',
    bg: 'bg-sky-50',
    border: 'border-sky-200',
    text: 'text-sky-700',
    badge: 'bg-sky-100 text-sky-800'
  },
  development_tools: {
    label: 'Development Tools',
    icon: Wrench,
    color: 'orange',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-700',
    badge: 'bg-orange-100 text-orange-800'
  },
  soft_skills: {
    label: 'Soft Skills & Leadership',
    icon: HeartHandshake,
    color: 'rose',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    text: 'text-rose-700',
    badge: 'bg-rose-100 text-rose-800'
  }
};

const PROFICIENCY_CONFIG = {
  Advanced: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-300',
    dot: 'bg-emerald-500',
    desc: 'Demonstrated in real work experience / employment records'
  },
  Intermediate: {
    bg: 'bg-indigo-50',
    text: 'text-indigo-700',
    border: 'border-indigo-300',
    dot: 'bg-indigo-500',
    desc: 'Implemented in hands-on projects or tech stacks'
  },
  Beginner: {
    bg: 'bg-sky-50',
    text: 'text-sky-700',
    border: 'border-sky-300',
    dot: 'bg-sky-500',
    desc: 'Mentioned in skills list or profile summary'
  },
  Unknown: {
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    border: 'border-gray-300',
    dot: 'bg-gray-400',
    desc: 'General keyword mention'
  }
};

const SkillsPage = () => {
  const { fileId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skillData, setSkillData] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedProficiency, setSelectedProficiency] = useState('all');

  useEffect(() => {
    let isMounted = true;

    const fetchSkillData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Call the Phase 4 dedicated skill extraction endpoint
        const response = await extractSkills(fileId);

        if (isMounted) {
          setSkillData(response);
          if (response.skills && response.skills.length > 0) {
            setSelectedSkill(response.skills[0]);
          }
        }
      } catch (err) {
        console.warn('Dedicated extractSkills failed, attempting fallback to analyzeResume:', err);
        try {
          const analysis = await analyzeResume(fileId);
          if (isMounted && analysis?.skills_analysis) {
            setSkillData({
              file_id: fileId,
              total_skills: analysis.skills_analysis.total_skills,
              categorized_skills: analysis.skills_analysis.categorized_skills,
              skills: analysis.skills_analysis.skills,
              message: 'Skills loaded from analysis.'
            });
            if (analysis.skills_analysis.skills?.length > 0) {
              setSelectedSkill(analysis.skills_analysis.skills[0]);
            }
          } else {
            throw err;
          }
        } catch (fallbackErr) {
          if (isMounted) {
            setError(
              fallbackErr.response?.data?.detail ||
              'Failed to retrieve skill extraction analysis. Please ensure the backend is running and the resume exists.'
            );
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (fileId) {
      fetchSkillData();
    }
    return () => {
      isMounted = false;
    };
  }, [fileId]);

  // Filter skills based on search, category, proficiency
  const filteredSkills = useMemo(() => {
    if (!skillData || !skillData.skills) return [];

    return skillData.skills.filter((skill) => {
      const matchesSearch =
        skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        skill.category.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory =
        selectedCategory === 'all' || skill.category === selectedCategory;
      const matchesProficiency =
        selectedProficiency === 'all' || skill.proficiency === selectedProficiency;

      return matchesSearch && matchesCategory && matchesProficiency;
    });
  }, [skillData, searchQuery, selectedCategory, selectedProficiency]);

  // Compute breakdown stats
  const stats = useMemo(() => {
    if (!skillData || !skillData.skills) {
      return { total: 0, advanced: 0, intermediate: 0, beginner: 0, activeCategories: 0 };
    }
    const skills = skillData.skills;
    const advanced = skills.filter((s) => s.proficiency === 'Advanced').length;
    const intermediate = skills.filter((s) => s.proficiency === 'Intermediate').length;
    const beginner = skills.filter((s) => s.proficiency === 'Beginner').length;

    const catCounts = Object.keys(skillData.categorized_skills || {}).filter(
      (cat) => (skillData.categorized_skills[cat] || []).length > 0
    ).length;

    return {
      total: skills.length,
      advanced,
      intermediate,
      beginner,
      activeCategories: catCounts
    };
  }, [skillData]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <LoadingSpinner message="Extracting and normalizing technical skills..." />
        <p className="text-gray-500 text-sm mt-3">
          Matching aliases, classifying taxonomy domains, and scoring evidence-based proficiency...
        </p>
      </div>
    );
  }

  if (error || !skillData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="p-8 bg-red-50 border border-red-200 rounded-2xl inline-block max-w-lg shadow-sm">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-800 mb-2">Skill Extraction Error</h2>
          <p className="text-red-700 text-sm mb-6">{error || 'Skill analysis data could not be retrieved.'}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate('/upload')}
              className="px-5 py-2.5 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition text-sm"
            >
              Upload New Resume
            </button>
            <Link
              to={`/analysis/${fileId}`}
              className="px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition text-sm"
            >
              Back to Overview
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Top Breadcrumb & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <Link
          to={`/analysis/${fileId}`}
          className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-800 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Resume Overview
        </Link>
        <div className="flex items-center gap-3">
          <span className="text-xs bg-slate-100 text-slate-700 font-mono px-3 py-1 rounded-md border border-slate-200">
            ID: {fileId.slice(0, 8)}...
          </span>
          <Link
            to={`/dashboard/${fileId}`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Main Title & Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white rounded-2xl p-8 mb-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 bg-indigo-500/20 border border-indigo-400/30 px-3 py-1 rounded-full text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-3">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Phase 4 Skill Extraction Engine
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">Structured Skills & Competency Matrix</h1>
            <p className="text-slate-300 text-sm mt-2 max-w-2xl leading-relaxed">
              Canonical skill taxonomy mapping across 8 technical domains. Proficiency levels are evaluated
              from real evidence in employment roles, project implementations, and skills profiles.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm border border-white/15 rounded-xl p-4 text-center min-w-[160px]">
            <span className="text-xs text-indigo-200 font-medium uppercase tracking-wider">Total Extracted</span>
            <div className="text-4xl font-extrabold text-white mt-1">{stats.total}</div>
            <span className="text-xs text-indigo-300">canonical skills</span>
          </div>
        </div>

        {/* Metric Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <span className="text-xs text-slate-300 font-medium">Advanced (Experience)</span>
            <div className="text-2xl font-bold text-emerald-400 mt-0.5">{stats.advanced}</div>
          </div>
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <span className="text-xs text-slate-300 font-medium">Intermediate (Projects)</span>
            <div className="text-2xl font-bold text-indigo-300 mt-0.5">{stats.intermediate}</div>
          </div>
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <span className="text-xs text-slate-300 font-medium">Beginner (Listed)</span>
            <div className="text-2xl font-bold text-sky-300 mt-0.5">{stats.beginner}</div>
          </div>
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <span className="text-xs text-slate-300 font-medium">Active Domains</span>
            <div className="text-2xl font-bold text-amber-300 mt-0.5">{stats.activeCategories} / 8</div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm mb-8 space-y-4">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search Input */}
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search skills (e.g. Python, Docker, React)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Proficiency Filter */}
          <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider shrink-0">Level:</span>
            {['all', 'Advanced', 'Intermediate', 'Beginner'].map((level) => (
              <button
                key={level}
                onClick={() => setSelectedProficiency(level)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                  selectedProficiency === level
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {level === 'all' ? 'All Levels' : level}
              </button>
            ))}
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pt-3 border-t border-gray-100 pb-1">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
              selectedCategory === 'all'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All Categories ({skillData.skills?.length || 0})
          </button>
          {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
            const count = (skillData.categorized_skills?.[key] || []).length;
            const Icon = config.icon;
            return (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
                  selectedCategory === key
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {config.label}
                <span className="ml-1 text-[11px] opacity-80">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Layout: Two Columns on Large Screens */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Categorized Groups (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">
          {Object.entries(CATEGORY_CONFIG)
            .filter(([key]) => selectedCategory === 'all' || selectedCategory === key)
            .map(([catKey, config]) => {
              const Icon = config.icon;
              const catSkills = filteredSkills.filter((s) => s.category === catKey);

              // Don't show category card if empty when searching or filtering
              if (catSkills.length === 0 && (searchQuery || selectedCategory !== 'all' || selectedProficiency !== 'all')) {
                return null;
              }

              return (
                <div
                  key={catKey}
                  className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm transition hover:shadow-md"
                >
                  {/* Category Header */}
                  <div className="flex items-center justify-between pb-4 mb-5 border-b border-gray-100">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl ${config.bg} ${config.border} border flex items-center justify-center ${config.text}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-gray-900">{config.label}</h3>
                        <p className="text-xs text-gray-500">
                          {catSkills.length} skill{catSkills.length !== 1 ? 's' : ''} detected
                        </p>
                      </div>
                    </div>
                    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${config.badge}`}>
                      {catSkills.length}
                    </span>
                  </div>

                  {/* Skills Grid */}
                  {catSkills.length === 0 ? (
                    <p className="text-gray-400 text-xs italic py-2">
                      No skills detected in this category.
                    </p>
                  ) : (
                    <div className="flex flex-wrap gap-2.5">
                      {catSkills.map((skill, index) => {
                        const prof = PROFICIENCY_CONFIG[skill.proficiency] || PROFICIENCY_CONFIG.Unknown;
                        const isSelected = selectedSkill?.name === skill.name;

                        return (
                          <button
                            key={index}
                            onClick={() => setSelectedSkill(skill)}
                            className={`group relative flex items-center gap-2 px-3.5 py-2 rounded-xl border text-sm font-medium transition cursor-pointer ${
                              isSelected
                                ? 'bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-slate-900 ring-offset-2'
                                : 'bg-slate-50 text-slate-800 border-slate-200 hover:border-slate-300 hover:bg-slate-100'
                            }`}
                          >
                            <span className={`w-2 h-2 rounded-full ${prof.dot}`} />
                            <span>{skill.name}</span>
                            {skill.occurrences > 1 && (
                              <span
                                className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                                  isSelected ? 'bg-slate-800 text-slate-300' : 'bg-slate-200 text-slate-600'
                                }`}
                              >
                                {skill.occurrences}x
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}

          {filteredSkills.length === 0 && (
            <div className="bg-white rounded-2xl p-12 border border-gray-200 text-center shadow-sm">
              <Search className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <h3 className="text-base font-bold text-gray-800">No matching skills found</h3>
              <p className="text-gray-500 text-xs mt-1">
                Try modifying your search term or clearing the active filters.
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                  setSelectedProficiency('all');
                }}
                className="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition"
              >
                Reset Filters
              </button>
            </div>
          )}
        </div>

        {/* Right Column: Skill Detail & Evidence Inspector (1 Col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm sticky top-6">
            <div className="flex items-center justify-between pb-4 border-b border-gray-100 mb-5">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <h3 className="text-base font-bold text-gray-900">Skill Details & Evidence</h3>
              </div>
              {selectedSkill && (
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                  Inspector
                </span>
              )}
            </div>

            {selectedSkill ? (
              <div className="space-y-5">
                {/* Skill Name & Canonical Status */}
                <div>
                  <div className="flex items-center justify-between">
                    <h4 className="text-2xl font-black text-gray-900">{selectedSkill.name}</h4>
                    <span className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold px-2.5 py-1 rounded-md">
                      {CATEGORY_CONFIG[selectedSkill.category]?.label || selectedSkill.category}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Canonicalized and normalized via Phase 4 taxonomy mapping.
                  </p>
                </div>

                {/* Proficiency Evaluation */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">Proficiency Level</span>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        PROFICIENCY_CONFIG[selectedSkill.proficiency]?.bg
                      } ${PROFICIENCY_CONFIG[selectedSkill.proficiency]?.text} ${
                        PROFICIENCY_CONFIG[selectedSkill.proficiency]?.border
                      }`}
                    >
                      {selectedSkill.proficiency}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    {selectedSkill.proficiency_reason}
                  </p>
                </div>

                {/* Extraction Sources */}
                <div>
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">
                    Detected In Sections ({selectedSkill.sources?.length || 0})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {(selectedSkill.sources || []).map((source, sIdx) => {
                      let IconComp = FileText;
                      let label = source;
                      if (source === 'experience') {
                        IconComp = Briefcase;
                        label = 'Work Experience';
                      } else if (source === 'projects') {
                        IconComp = FolderGit2;
                        label = 'Projects';
                      } else if (source === 'skills_section') {
                        IconComp = Code2;
                        label = 'Skills Section';
                      }

                      return (
                        <span
                          key={sIdx}
                          className="inline-flex items-center gap-1.5 text-xs font-medium bg-slate-100 text-slate-700 px-3 py-1 rounded-lg border border-slate-200"
                        >
                          <IconComp className="w-3.5 h-3.5 text-slate-500" />
                          {label}
                        </span>
                      );
                    })}
                  </div>
                </div>

                {/* Occurrence Count */}
                <div className="flex items-center justify-between text-xs py-2 px-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="font-medium text-slate-600">Total Mention Frequency:</span>
                  <span className="font-bold text-slate-900 font-mono">{selectedSkill.occurrences} time(s)</span>
                </div>

                {/* Evidence Snippets */}
                <div>
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">
                    Evidence Context
                  </span>
                  {selectedSkill.evidence && selectedSkill.evidence.length > 0 ? (
                    <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                      {selectedSkill.evidence.map((snippet, evIdx) => (
                        <div
                          key={evIdx}
                          className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-xl text-xs text-amber-950 font-serif italic leading-relaxed"
                        >
                          "{snippet}"
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-400 italic">
                      Identified directly from technical skills profile list.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-gray-400">
                <HelpCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-xs">Click any skill chip on the left to inspect its evidence and proficiency level.</p>
              </div>
            )}
          </div>

          {/* Explainable AI Note */}
          <div className="bg-indigo-50/60 rounded-2xl p-5 border border-indigo-100">
            <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-indigo-600" /> Explainable Heuristics
            </h4>
            <p className="text-xs text-indigo-800/80 leading-relaxed">
              Unlike black-box models, each skill match is explainable. The engine uses strict word-boundary matching,
              canonical taxonomy aliases, and multi-section evidence scoring so you can verify why each skill was extracted.
            </p>
          </div>

          {/* Job Recommendation Link */}
          <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-5 text-white shadow-sm border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5 text-indigo-300">
              <Sparkles className="w-4 h-4 text-indigo-400" /> Phase 6: Job Recommendations
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Match your extracted skills against 255 verified technology job openings using TF-IDF and Cosine Similarity.
            </p>
            <Link
              to={`/recommendations/${fileId}`}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
            >
              <Briefcase className="w-3.5 h-3.5" /> View Matching Jobs <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillsPage;
