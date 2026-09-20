import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pravi_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('pravi_token');
      localStorage.removeItem('pravi_user');
      window.location.href = '/';
    }
    return Promise.reject(err);
  }
);

export default api;

// Auth
export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password });
export const getMe = () => api.get('/auth/me');

// Families
export const getFamilies = (params?: any) => api.get('/families', { params });
export const getFamily = (id: string) => api.get(`/families/${id}`);
export const getFamily360 = (id: string) => api.get(`/families/${id}/360`);
export const getFamilyMembers = (id: string) => api.get(`/families/${id}/members`);
export const getFamilyRelationships = (id: string) => api.get(`/families/${id}/relationships`);

// Change Requests
export const getChangeRequests = (params?: any) => api.get('/change-requests', { params });
export const getChangeRequest = (id: string) => api.get(`/change-requests/${id}`);
export const createChangeRequest = (data: any) => api.post('/change-requests', data);
export const approveRequest = (id: string, data?: any) => api.post(`/change-requests/${id}/approve`, data || {});
export const rejectRequest = (id: string, data?: any) => api.post(`/change-requests/${id}/reject`, data || {});
export const requestMoreInfo = (id: string, data: any) => api.post(`/change-requests/${id}/request-information`, data);

// Life Events
export const getLifeEvents = (params?: any) => api.get('/life-events', { params });
export const createLifeEvent = (data: any) => api.post('/life-events', data);
export const approveLifeEvent = (id: string, data?: any) => api.post(`/life-events/${id}/approve`, data || {});
export const rejectLifeEvent = (id: string, data?: any) => api.post(`/life-events/${id}/reject`, data || {});

// Schemes
export const getSchemes = (params?: any) => api.get('/schemes', { params });
export const getScheme = (id: string) => api.get(`/schemes/${id}`);

// Eligibility
export const getEligibility = (familyId: string) => api.get(`/eligibility/${familyId}`);
export const evaluateEligibility = (familyId: string) => api.post(`/eligibility/${familyId}/evaluate`);

// Benefits
export const getBenefits = (params?: any) => api.get('/benefits', { params });

// Identity
export const findMatches = (data: any) => api.post('/identity/match', data);
export const getPendingMatches = () => api.get('/identity/matches');
export const confirmMatch = (id: string) => api.post(`/identity/matches/${id}/confirm`);
export const rejectMatch = (id: string, data?: any) => api.post(`/identity/matches/${id}/reject`, data || {});
export const mergeRecords = (data: any) => api.post('/identity/merge', data);

// Departments
export const getDepartments = () => api.get('/departments');
export const requestDataAccess = (data: any) => api.post('/departments/data-access', data);
export const getAccessLogs = (params?: any) => api.get('/departments/data-access/logs', { params });

// Audit
export const getAuditLogs = (params?: any) => api.get('/audit', { params });

// Analytics
export const getAnalytics = () => api.get('/analytics');

// Notifications
export const getNotifications = (params?: any) => api.get('/notifications', { params });
export const markNotificationRead = (id: string) => api.post(`/notifications/${id}/read`);
export const markAllRead = () => api.post('/notifications/read-all');
