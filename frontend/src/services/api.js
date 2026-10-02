import axios from 'axios';

// Support configurable backend API URL in production (e.g. Vercel/Netlify -> Render/Railway)
// Defaults to relative '/api' for Docker Compose (Nginx proxy) and local Vite dev proxy
const apiBaseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api`
  : '/api';

const api = axios.create({
  baseURL: apiBaseURL,
});

export const uploadResume = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const analyzeResume = async (fileId) => {
  try {
    const response = await api.post(`/resume/analyze`, { file_id: fileId, fileId });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const extractSkills = async (fileId, profile = null) => {
  try {
    const response = await api.post('/resume/extract-skills', {
      file_id: fileId,
      fileId,
      profile
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getJobs = async (params = {}) => {
  try {
    const response = await api.get('/jobs', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getJobById = async (jobId) => {
  try {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getJobCategories = async () => {
  try {
    const response = await api.get('/jobs/categories');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getJobSkills = async () => {
  try {
    const response = await api.get('/jobs/skills');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getJobStats = async () => {
  try {
    const response = await api.get('/jobs/stats');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const seedJobs = async () => {
  try {
    const response = await api.post('/jobs/seed');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const searchJobs = async (params = {}) => {
  try {
    const response = await api.get('/jobs/search', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};


export const getRecommendations = async (paramOrResumeText, maybeSkills) => {
  try {
    let payload = {};
    if (typeof paramOrResumeText === 'object' && paramOrResumeText !== null) {
      payload = paramOrResumeText;
    } else {
      payload = {
        resume_text: paramOrResumeText,
        skills: maybeSkills || []
      };
    }
    const response = await api.post('/jobs/recommend', payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const analyzeSkills = async (resumeSkills, jobSkills) => {
  try {
    const response = await api.post('/skills/analyze', { resume_skills: resumeSkills, job_skills: jobSkills });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const analyzeSkillGap = async (fileId, jobId, candidateSkills = null) => {
  try {
    const payload = {
      job_id: String(jobId)
    };
    if (fileId) {
      payload.file_id = String(fileId);
    }
    if (candidateSkills && Array.isArray(candidateSkills)) {
      payload.candidate_skills = candidateSkills;
    }
    const response = await api.post('/skill-gap/analyze', payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getDashboardStats = async (fileId = null) => {
  try {
    const params = fileId && fileId !== 'sample' ? { file_id: fileId } : {};
    const response = await api.get('/resume/dashboard-stats', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getResumeImprovements = async (fileId) => {
  try {
    const response = await api.get(`/resume/improvements/${fileId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getResumeHistory = async (limit = 25) => {
  try {
    const response = await api.get('/resume/history', { params: { limit } });
    return response.data;
  } catch (error) {
    throw error;
  }
};

