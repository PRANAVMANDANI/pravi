import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Home, Users, Gift, FileText, Calendar, Bell, PlusCircle, LogOut, Shield } from 'lucide-react';

const NAV = [
  { to: '/citizen/dashboard', icon: Home, label: 'Dashboard' },
  { to: '/citizen/family', icon: Users, label: 'My Family' },
  { to: '/citizen/schemes', icon: Gift, label: 'Schemes' },
  { to: '/citizen/benefits', icon: FileText, label: 'Benefits' },
  { to: '/citizen/requests', icon: PlusCircle, label: 'Requests' },
  { to: '/citizen/events', icon: Calendar, label: 'Life Events' },
  { to: '/citizen/notifications', icon: Bell, label: 'Notifications' },
];

export default function CitizenLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col fixed h-screen">
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-800">Pravi ID</div>
              <div className="text-[10px] text-slate-500">Citizen Portal</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-amber-50 text-amber-700 font-medium' : 'text-slate-600 hover:bg-slate-100'
                }`
              }>
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-slate-200">
          <div className="px-3 py-2 text-xs text-slate-500 mb-1 truncate">{user?.full_name}</div>
          <button onClick={() => { logout(); navigate('/'); }}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>
      {/* Main */}
      <main className="flex-1 ml-60 p-6">
        <Outlet />
      </main>
    </div>
  );
}
