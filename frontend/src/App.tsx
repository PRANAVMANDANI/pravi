import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import CitizenLayout from './pages/citizen/CitizenLayout';
import CitizenDashboard from './pages/citizen/CitizenDashboard';
import CitizenFamily from './pages/citizen/CitizenFamily';
import CitizenSchemes from './pages/citizen/CitizenSchemes';
import CitizenBenefits from './pages/citizen/CitizenBenefits';
import CitizenRequests from './pages/citizen/CitizenRequests';
import CitizenNewRequest from './pages/citizen/CitizenNewRequest';
import CitizenEvents from './pages/citizen/CitizenEvents';
import CitizenNotifications from './pages/citizen/CitizenNotifications';
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminFamilies from './pages/admin/AdminFamilies';
import AdminFamily360 from './pages/admin/AdminFamily360';
import AdminRequests from './pages/admin/AdminRequests';
import AdminRequestDetail from './pages/admin/AdminRequestDetail';
import AdminMatches from './pages/admin/AdminMatches';
import AdminEvents from './pages/admin/AdminEvents';
import AdminSchemes from './pages/admin/AdminSchemes';
import AdminBenefits from './pages/admin/AdminBenefits';
import AdminDepartments from './pages/admin/AdminDepartments';
import AdminAudit from './pages/admin/AdminAudit';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">Loading...</div>;
  if (!user) return <Navigate to="/" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to={user.role === 'citizen' ? '/citizen/dashboard' : '/admin/dashboard'} replace /> : <LoginPage />} />
      {/* Citizen Routes */}
      <Route path="/citizen" element={<ProtectedRoute allowedRoles={['citizen']}><CitizenLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<CitizenDashboard />} />
        <Route path="family" element={<CitizenFamily />} />
        <Route path="schemes" element={<CitizenSchemes />} />
        <Route path="benefits" element={<CitizenBenefits />} />
        <Route path="requests" element={<CitizenRequests />} />
        <Route path="requests/new" element={<CitizenNewRequest />} />
        <Route path="events" element={<CitizenEvents />} />
        <Route path="notifications" element={<CitizenNotifications />} />
      </Route>
      {/* Admin/Government Routes */}
      <Route path="/admin" element={<ProtectedRoute allowedRoles={['verification_officer','scheme_officer','department_officer','state_admin','assisted_operator']}><AdminLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="families" element={<AdminFamilies />} />
        <Route path="families/:familyId" element={<AdminFamily360 />} />
        <Route path="requests" element={<AdminRequests />} />
        <Route path="requests/:requestId" element={<AdminRequestDetail />} />
        <Route path="matches" element={<AdminMatches />} />
        <Route path="events" element={<AdminEvents />} />
        <Route path="schemes" element={<AdminSchemes />} />
        <Route path="benefits" element={<AdminBenefits />} />
        <Route path="departments" element={<AdminDepartments />} />
        <Route path="audit" element={<AdminAudit />} />
        <Route path="analytics" element={<AdminAnalytics />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
