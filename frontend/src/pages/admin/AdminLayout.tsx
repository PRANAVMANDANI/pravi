import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, Users, FileText, GitMerge, Calendar, Gift, Award, Building2,
  ScrollText, BarChart3, LogOut, Shield
} from 'lucide-react';

const NAV = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/families', icon: Users, label: 'Families' },
  { to: '/admin/requests', icon: FileText, label: 'Change Requests' },
  { to: '/admin/matches', icon: GitMerge, label: 'Duplicate Matches' },
  { to: '/admin/events', icon: Calendar, label: 'Life Events' },
  { to: '/admin/schemes', icon: Gift, label: 'Schemes' },
  { to: '/admin/benefits', icon: Award, label: 'Benefits' },
  { to: '/admin/departments', icon: Building2, label: 'Data Access' },
  { to: '/admin/audit', icon: ScrollText, label: 'Audit Logs' },
  { to: '/admin/analytics', icon: BarChart3, label: 'Analytics' },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const roleLabel: Record<string, string> = {
    verification_officer: 'Verification Officer',
    scheme_officer: 'Scheme Officer',
    department_officer: 'Department Officer',
    state_admin: 'State Administrator',
    assisted_operator: 'Assisted Operator',
  };

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <aside className="w-60 bg-slate-800 border-r border-slate-700 flex flex-col fixed h-screen">
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Pravi ID</div>
              <div className="text-[10px] text-slate-400">Government Portal</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-amber-500/20 text-amber-400 font-medium' : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`
              }>
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-slate-700">
          <div className="px-3 py-1.5 text-xs text-slate-400 truncate">{user?.full_name}</div>
          <div className="px-3 py-0.5 text-[10px] text-amber-400/80">{roleLabel[user?.role || ''] || user?.role}</div>
          <button onClick={() => { logout(); navigate('/'); }}
            className="flex items-center gap-2 w-full px-3 py-2 mt-1 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 ml-60 p-6">
        <Outlet />
      </main>
    </div>
  );
}
