import { useState, useEffect } from 'react';
import {
  Briefcase,
  Search,
  Filter,
  MapPin,
  Building2,
  Clock,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  GraduationCap,
  IndianRupee,
  Layers,
  X,
  CheckCircle2,
  Code2,
  RefreshCw,
  SlidersHorizontal,
  Info,
  Laptop
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { getJobs, getJobCategories, getJobStats, seedJobs } from '../services/api';

const EXPERIENCE_LEVELS = ['All', 'Entry-level', 'Junior', 'Intermediate', 'Senior'];
const WORK_MODES = ['All', 'Remote', 'Hybrid', 'On-site'];
const EMPLOYMENT_TYPES = ['All', 'Full-time', 'Internship', 'Contract'];
const LOCATIONS = [
  'All',
  'Bengaluru, Karnataka',
  'Hyderabad, Telangana',
  'Pune, Maharashtra',
  'Gurugram, Haryana',
  'Noida, Uttar Pradesh',
  'Chennai, Tamil Nadu',
  'Mumbai, Maharashtra',
  'Mysuru, Karnataka',
  'Remote - India',
  'Remote - Global'
];

const JobExplorerPage = () => {
  const [jobs, setJobs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [totalJobs, setTotalJobs] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [seeding, setSeeding] = useState(false);
  const [seedNotification, setSeedNotification] = useState(null);

  // Filter States
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedLocation, setSelectedLocation] = useState('All');
  const [selectedExperience, setSelectedExperience] = useState('All');
  const [selectedWorkMode, setSelectedWorkMode] = useState('All');
  const [selectedEmploymentType, setSelectedEmploymentType] = useState('All');
  const [selectedJob, setSelectedJob] = useState(null);

  // Fetch Categories and Stats on Mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [catData, statsData] = await Promise.all([
          getJobCategories(),
          getJobStats()
        ]);
        setCategories(catData || []);
        setStats(statsData || null);
      } catch (err) {
        console.warn('Failed to fetch categories or stats:', err);
      }
    };
    fetchMetadata();
  }, []);

  // Fetch Jobs when filters or page changes
  useEffect(() => {
    let isMounted = true;

    const fetchJobListings = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          page: currentPage,
          limit: 12
        };

        if (search.trim()) params.search = search.trim();
        if (selectedCategory !== 'All') params.category = selectedCategory;
        if (selectedLocation !== 'All') params.location = selectedLocation;
        if (selectedExperience !== 'All') params.experience_level = selectedExperience;
        if (selectedWorkMode !== 'All') params.work_mode = selectedWorkMode;
        if (selectedEmploymentType !== 'All') params.employment_type = selectedEmploymentType;

        const data = await getJobs(params);

        if (isMounted) {
          setJobs(data.jobs || []);
          setTotalJobs(data.total || 0);
          setTotalPages(data.pages || 1);
          if (data.jobs && data.jobs.length > 0 && !selectedJob) {
            setSelectedJob(data.jobs[0]);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
            'Failed to fetch job opportunities. Please ensure the backend is running.'
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchJobListings();

    return () => {
      isMounted = false;
    };
  }, [
    currentPage,
    search,
    selectedCategory,
    selectedLocation,
    selectedExperience,
    selectedWorkMode,
    selectedEmploymentType
  ]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    setSearch('');
    setSelectedCategory('All');
    setSelectedLocation('All');
    setSelectedExperience('All');
    setSelectedWorkMode('All');
    setSelectedEmploymentType('All');
    setCurrentPage(1);
  };

  const handleTriggerSeed = async () => {
    try {
      setSeeding(true);
      setSeedNotification(null);
      const res = await seedJobs();
      setSeedNotification({
        type: 'success',
        text: `Dataset synchronized! ${res.total_in_db} jobs available (${res.inserted} inserted, ${res.updated} updated).`
      });

      // Refresh listings and stats
      const [jobsData, statsData] = await Promise.all([
        getJobs({ page: 1, limit: 12 }),
        getJobStats()
      ]);
      setJobs(jobsData.jobs || []);
      setTotalJobs(jobsData.total || 0);
      setStats(statsData || null);
      if (jobsData.jobs && jobsData.jobs.length > 0) {
        setSelectedJob(jobsData.jobs[0]);
      }
      setCurrentPage(1);
    } catch (err) {
      setSeedNotification({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to synchronize dataset.'
      });
    } finally {
      setSeeding(false);
      setTimeout(() => setSeedNotification(null), 5000);
    }
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

  const getLevelBadge = (level) => {
    switch (level) {
      case 'Entry-level':
        return 'bg-sky-50 text-sky-700 border-sky-200';
      case 'Junior':
        return 'bg-teal-50 text-teal-700 border-teal-200';
      case 'Intermediate':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'Senior':
        return 'bg-amber-50 text-amber-700 border-amber-200';
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
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Phase 5: Job Dataset & Explorer
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight">Explore Tech Opportunities</h1>
            <p className="text-slate-300 text-sm mt-2 max-w-2xl leading-relaxed">
              Browse our curated database of verified technology positions spanning software engineering,
              machine learning, AI, data, cloud, and cybersecurity. Powered by dynamic multi-criteria search.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              onClick={handleTriggerSeed}
              disabled={seeding}
              className="inline-flex items-center justify-center gap-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 px-4 py-2.5 rounded-xl text-xs font-medium text-slate-200 transition shadow-sm disabled:opacity-50"
              title="Resynchronize synthetic dataset with database"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${seeding ? 'animate-spin' : ''}`} />
              {seeding ? 'Syncing...' : 'Sync Dataset'}
            </button>
          </div>
        </div>

        {/* Live Notification Banner */}
        {seedNotification && (
          <div
            className={`mt-4 p-3 rounded-xl text-xs font-medium border flex items-center justify-between ${
              seedNotification.type === 'success'
                ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800'
                : 'bg-red-950/60 text-red-300 border-red-800'
            }`}
          >
            <span>{seedNotification.text}</span>
            <button onClick={() => setSeedNotification(null)}>
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Dataset Statistics Strip */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800">
            <div className="bg-slate-800/50 backdrop-blur-xs p-3.5 rounded-2xl border border-slate-700/50">
              <p className="text-xs text-slate-400 font-medium">Total Opportunities</p>
              <p className="text-xl sm:text-2xl font-bold text-white mt-0.5">{stats.total_jobs}</p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-xs p-3.5 rounded-2xl border border-slate-700/50">
              <p className="text-xs text-slate-400 font-medium">Domain Categories</p>
              <p className="text-xl sm:text-2xl font-bold text-indigo-400 mt-0.5">{stats.total_categories}</p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-xs p-3.5 rounded-2xl border border-slate-700/50">
              <p className="text-xs text-slate-400 font-medium">Remote Roles</p>
              <p className="text-xl sm:text-2xl font-bold text-emerald-400 mt-0.5">
                {stats.work_modes?.Remote || 0}
              </p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-xs p-3.5 rounded-2xl border border-slate-700/50">
              <p className="text-xs text-slate-400 font-medium">Entry-Level & Junior</p>
              <p className="text-xl sm:text-2xl font-bold text-sky-400 mt-0.5">
                {(stats.experience_levels?.['Entry-level'] || 0) + (stats.experience_levels?.Junior || 0)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Search and Filters Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-5 mb-8 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search jobs by title, skills (e.g. Python, PyTorch), company, or category..."
              className="w-full pl-11 pr-4 py-3 bg-slate-50 hover:bg-slate-100/60 focus:bg-white text-slate-900 placeholder:text-slate-400 text-sm rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/10 transition outline-none"
            />
          </div>

          {/* Filters Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 pt-1">
            {/* Category Filter */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                <option value="All">All Categories ({stats?.total_jobs || 'All'})</option>
                {categories.map((c) => (
                  <option key={c.category} value={c.category}>
                    {c.category} ({c.count})
                  </option>
                ))}
              </select>
            </div>

            {/* Location Filter */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Location</label>
              <select
                value={selectedLocation}
                onChange={(e) => {
                  setSelectedLocation(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                {LOCATIONS.map((loc) => (
                  <option key={loc} value={loc}>
                    {loc}
                  </option>
                ))}
              </select>
            </div>

            {/* Experience Filter */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Experience</label>
              <select
                value={selectedExperience}
                onChange={(e) => {
                  setSelectedExperience(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                {EXPERIENCE_LEVELS.map((exp) => (
                  <option key={exp} value={exp}>
                    {exp}
                  </option>
                ))}
              </select>
            </div>

            {/* Work Mode */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Work Mode</label>
              <select
                value={selectedWorkMode}
                onChange={(e) => {
                  setSelectedWorkMode(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                {WORK_MODES.map((mode) => (
                  <option key={mode} value={mode}>
                    {mode}
                  </option>
                ))}
              </select>
            </div>

            {/* Employment Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Type</label>
              <select
                value={selectedEmploymentType}
                onChange={(e) => {
                  setSelectedEmploymentType(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg px-3 py-2 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 outline-none"
              >
                {EMPLOYMENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Status & Reset */}
          {(search ||
            selectedCategory !== 'All' ||
            selectedLocation !== 'All' ||
            selectedExperience !== 'All' ||
            selectedWorkMode !== 'All' ||
            selectedEmploymentType !== 'All') && (
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
              <span className="flex items-center gap-1.5 font-medium text-slate-700">
                <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-600" /> Filtered results:{' '}
                {totalJobs} matches
              </span>
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center gap-1"
              >
                <X className="w-3 h-3" /> Clear all filters
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-24 text-center">
          <LoadingSpinner message="Querying active job opportunities..." />
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <X className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-red-900 mb-1">Failed to Load Opportunities</h3>
          <p className="text-xs text-red-700 mb-4">{error}</p>
          <button
            onClick={() => setCurrentPage(1)}
            className="px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
          >
            Retry Connection
          </button>
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-md mx-auto">
          <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-3">
            <Briefcase className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800 mb-1">No Jobs Found</h3>
          <p className="text-xs text-slate-500 mb-5">
            We couldn't find any opportunities matching your selected filter criteria.
          </p>
          <button
            onClick={handleResetFilters}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Job List Column (5 Cols) */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-500 px-1 mb-1">
              <span>
                Showing <strong className="text-slate-800">{jobs.length}</strong> of{' '}
                <strong className="text-slate-800">{totalJobs}</strong> jobs
              </span>
              <span>
                Page {currentPage} of {totalPages}
              </span>
            </div>

            <div className="space-y-3">
              {jobs.map((job) => {
                const isSelected = selectedJob && selectedJob.id === job.id;
                return (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`p-4 rounded-xl cursor-pointer transition border ${
                      isSelected
                        ? 'bg-indigo-50/70 border-indigo-400 shadow-sm ring-2 ring-indigo-500/20'
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-xs'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-bold text-slate-900 text-sm leading-snug hover:text-indigo-600 transition">
                          {job.title}
                        </h3>
                        <p className="text-xs text-slate-600 font-medium flex items-center gap-1.5 mt-0.5">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          {job.company}
                        </p>
                      </div>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border whitespace-nowrap ${getLevelBadge(
                          job.experience_level
                        )}`}
                      >
                        {job.experience_level}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 mt-3 text-[11px] text-slate-500">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        {job.location}
                      </span>
                      <span>•</span>
                      <span
                        className={`px-1.5 py-0.5 rounded-sm text-[10px] font-medium border ${getWorkModeBadge(
                          job.work_mode
                        )}`}
                      >
                        {job.work_mode}
                      </span>
                      {job.salary_range && (
                        <>
                          <span>•</span>
                          <span className="text-emerald-700 font-semibold">{job.salary_range}</span>
                        </>
                      )}
                    </div>

                    {/* Skill Tags Preview */}
                    <div className="flex flex-wrap gap-1 mt-3">
                      {job.required_skills?.slice(0, 4).map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-slate-100 text-slate-700 text-[10px] px-2 py-0.5 rounded-md font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                      {job.required_skills?.length > 4 && (
                        <span className="text-[10px] text-slate-400 font-medium self-center">
                          +{job.required_skills.length - 4} more
                        </span>
                      )}
                    </div>

                    {job.date_posted && (
                      <p className="text-[10px] text-slate-400 mt-2 text-right">
                        Posted {job.date_posted}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <span className="text-xs text-slate-500 font-medium">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Job Detail Sticky Inspector (7 Cols) */}
          <div className="lg:col-span-7 sticky top-6">
            {selectedJob ? (
              <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-6">
                {/* Header */}
                <div>
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-[11px] font-mono font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md">
                      {selectedJob.job_id}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      Posted: {selectedJob.date_posted || selectedJob.created_at || 'Recently'}
                    </span>
                  </div>

                  <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mt-2">
                    {selectedJob.title}
                  </h2>

                  <div className="flex items-center gap-2 mt-1.5">
                    <p className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                      <Building2 className="w-4 h-4 text-indigo-600" />
                      {selectedJob.company}
                    </p>
                    <span className="text-[10px] bg-indigo-50 text-indigo-700 font-semibold px-2 py-0.5 rounded-full border border-indigo-200">
                      Sample Company
                    </span>
                  </div>
                </div>

                {/* Quick Details Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Category
                    </span>
                    <span className="font-semibold text-slate-800">{selectedJob.category}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Experience
                    </span>
                    <span className="font-semibold text-slate-800">
                      {selectedJob.min_experience} - {selectedJob.max_experience || '5+'} yrs
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Work Mode
                    </span>
                    <span className="font-semibold text-slate-800">{selectedJob.work_mode}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Location
                    </span>
                    <span className="font-semibold text-slate-800">{selectedJob.location}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Employment
                    </span>
                    <span className="font-semibold text-slate-800">
                      {selectedJob.employment_type}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Compensation
                    </span>
                    <span className="font-semibold text-emerald-700">
                      {selectedJob.salary_range || 'Competitive'}
                    </span>
                  </div>
                </div>

                {/* Core Responsibilities */}
                {selectedJob.responsibilities && selectedJob.responsibilities.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Key Responsibilities
                    </h3>
                    <ul className="space-y-2">
                      {selectedJob.responsibilities.map((resp, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 leading-relaxed">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                          <span>{resp}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Required Skills */}
                <div>
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Code2 className="w-4 h-4 text-indigo-600" /> Required Technical Skills
                  </h3>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJob.required_skills?.map((skill, idx) => (
                      <span
                        key={idx}
                        className="bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs px-2.5 py-1 rounded-lg font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Preferred Skills */}
                {selectedJob.preferred_skills && selectedJob.preferred_skills.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-amber-500" /> Preferred / Nice-to-Have
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedJob.preferred_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-slate-100 text-slate-600 border border-slate-200 text-xs px-2.5 py-1 rounded-lg font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Education Requirements */}
                {selectedJob.education && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                      <GraduationCap className="w-4 h-4 text-slate-600" /> Required Education
                    </h3>
                    <p className="text-xs text-slate-600">{selectedJob.education}</p>
                  </div>
                )}

                {/* Overview & Disclaimer */}
                <div className="border-t border-slate-100 pt-4">
                  <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-[11px] text-slate-500 flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>Synthetic Dataset Notice:</strong> This position is part of the
                      verified Phase 5 demonstration catalog used to train and test the upcoming
                      Machine Learning TF-IDF recommendation engine (Phase 6).
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400">
                <p className="text-xs">Select any job from the list to view complete details.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobExplorerPage;
