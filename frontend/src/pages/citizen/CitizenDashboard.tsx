import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { getFamily360, getNotifications } from '../../services/api';
import { Link } from 'react-router-dom';
import { Users, Gift, Award, FileText, Calendar, Bell, CheckCircle, Clock, AlertTriangle, XCircle } from 'lucide-react';

export default function CitizenDashboard() {
  const { user } = useAuth();
  const familyId = user?.family_id || '';

  const { data: f360 } = useQuery({ queryKey: ['family360', familyId], queryFn: () => getFamily360(familyId), enabled: !!familyId });
  const { data: notifData } = useQuery({ queryKey: ['notifications'], queryFn: () => getNotifications({ limit: 5 }) });

  const family = f360?.data?.data?.family;
  const members = f360?.data?.data?.members || [];
  const eligibility = f360?.data?.data?.eligibility || [];
  const benefits = f360?.data?.data?.benefits || [];
  const requests = f360?.data?.data?.change_requests || [];
  const notifications = notifData?.data?.data?.notifications || [];
  const unread = notifData?.data?.data?.unread_count || 0;

  const eligible = eligibility.filter((e: any) => e.status === 'eligible').length;
  const needsVerification = eligibility.filter((e: any) => e.status === 'needs_verification').length;
  const activeBenefits = benefits.filter((b: any) => b.status === 'active').length;
  const pendingRequests = requests.filter((r: any) => ['submitted', 'under_review'].includes(r.status)).length;

  const statusColor: Record<string, string> = {
    verified: 'bg-emerald-100 text-emerald-700', pending: 'bg-amber-100 text-amber-700',
    partially_verified: 'bg-blue-100 text-blue-700', rejected: 'bg-red-100 text-red-700',
  };

  return (
    <div className="max-w-5xl">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.full_name}</h1>
            <p className="text-sm text-slate-500 mt-1">Your Pravi ID family dashboard</p>
          </div>
          <Link to="/citizen/notifications" className="relative p-2 hover:bg-slate-100 rounded-lg">
            <Bell className="w-5 h-5 text-slate-600" />
            {unread > 0 && <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">{unread}</span>}
          </Link>
        </div>

        {/* Family ID Card */}
        <div className="mt-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-amber-600 font-medium uppercase tracking-wider">My Pravi ID</div>
              <div className="text-xl font-bold text-slate-800 mt-1 font-mono">{familyId}</div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor[family?.verification_status] || 'bg-slate-100 text-slate-600'}`}>
              {family?.verification_status?.replace('_', ' ')?.toUpperCase() || 'LOADING'}
            </span>
          </div>
          <div className="flex gap-6 mt-3 text-sm text-slate-600">
            <span>📍 {family?.district || '—'}, {family?.taluka || '—'}</span>
            <span>👥 {members.filter((m: any) => m.is_active).length} members</span>
          </div>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Link to="/citizen/family" className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
          <Users className="w-5 h-5 text-blue-500 mb-2" />
          <div className="text-2xl font-bold text-slate-800">{members.filter((m: any) => m.is_active).length}</div>
          <div className="text-xs text-slate-500">Family Members</div>
        </Link>
        <Link to="/citizen/schemes" className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
          <Gift className="w-5 h-5 text-emerald-500 mb-2" />
          <div className="text-2xl font-bold text-slate-800">{eligible}</div>
          <div className="text-xs text-slate-500">Eligible Schemes</div>
          {needsVerification > 0 && <div className="text-[10px] text-amber-600 mt-1">{needsVerification} need verification</div>}
        </Link>
        <Link to="/citizen/benefits" className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
          <Award className="w-5 h-5 text-violet-500 mb-2" />
          <div className="text-2xl font-bold text-slate-800">{activeBenefits}</div>
          <div className="text-xs text-slate-500">Active Benefits</div>
        </Link>
        <Link to="/citizen/requests" className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
          <FileText className="w-5 h-5 text-amber-500 mb-2" />
          <div className="text-2xl font-bold text-slate-800">{pendingRequests}</div>
          <div className="text-xs text-slate-500">Pending Requests</div>
        </Link>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
        {[
          { to: '/citizen/family', label: 'View Family', icon: Users },
          { to: '/citizen/schemes', label: 'View Schemes', icon: Gift },
          { to: '/citizen/benefits', label: 'View Benefits', icon: Award },
          { to: '/citizen/requests/new', label: 'Request a Change', icon: FileText },
          { to: '/citizen/events', label: 'Life Events', icon: Calendar },
          { to: '/citizen/requests', label: 'Track Requests', icon: Clock },
        ].map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to}
            className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3 hover:bg-slate-50 hover:shadow-sm transition-all text-sm font-medium text-slate-700">
            <Icon className="w-4 h-4 text-slate-400" /> {label}
          </Link>
        ))}
      </div>

      {/* Recent Notifications */}
      {notifications.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Recent Notifications</h3>
          <div className="space-y-2">
            {notifications.slice(0, 4).map((n: any) => (
              <div key={n.notification_id} className={`flex items-start gap-3 p-3 rounded-lg ${n.is_read ? 'bg-slate-50' : 'bg-amber-50 border border-amber-100'}`}>
                <Bell className={`w-4 h-4 mt-0.5 ${n.is_read ? 'text-slate-400' : 'text-amber-500'}`} />
                <div>
                  <div className="text-sm text-slate-700">{n.title}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{new Date(n.created_at).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
