import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Users, Building2, UserCheck, BarChart3, Headphones } from 'lucide-react';

const DEMO_ACCOUNTS = [
  { username: 'citizen', label: 'Citizen', icon: Users, desc: 'View family data, submit change requests', color: 'from-emerald-500 to-teal-600' },
  { username: 'verifier', label: 'Verification Officer', icon: UserCheck, desc: 'Review requests, verify families, resolve duplicates', color: 'from-blue-500 to-indigo-600' },
  { username: 'scheme_officer', label: 'Scheme Officer', icon: BarChart3, desc: 'Manage schemes, configure eligibility rules', color: 'from-violet-500 to-purple-600' },
  { username: 'dept_officer', label: 'Department Officer', icon: Building2, desc: 'Access controlled family data for department', color: 'from-amber-500 to-orange-600' },
  { username: 'admin', label: 'State Administrator', icon: Shield, desc: 'Full system access, analytics, audit', color: 'from-rose-500 to-red-600' },
  { username: 'operator', label: 'Assisted Service Operator', icon: Headphones, desc: 'Help citizens submit requests', color: 'from-cyan-500 to-blue-600' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

  const handleLogin = async (username: string) => {
    setLoading(username);
    setError('');
    try {
      await login(username, 'demo123');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-sm bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Pravi ID</h1>
            <p className="text-xs text-slate-400">Gujarat Family Identity Platform</p>
          </div>
          <span className="ml-auto px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-400 rounded-full border border-amber-500/30">
            Hackathon Demo
          </span>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-2">Government-Centric Family Identity</h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            Unified household identity, scheme eligibility, and beneficiary management.
            Select a demo role to explore the platform.
          </p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl w-full">
          {DEMO_ACCOUNTS.map(({ username, label, icon: Icon, desc, color }) => (
            <button
              key={username}
              onClick={() => handleLogin(username)}
              disabled={loading !== null}
              className="group relative bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-xl p-5 text-left transition-all duration-200 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20 disabled:opacity-50"
            >
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold text-white text-sm mb-1">{label}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
              {loading === username && (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 rounded-xl">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                </div>
              )}
            </button>
          ))}
        </div>

        <div className="mt-10 text-center text-xs text-slate-500 max-w-lg">
          <p className="mb-1 font-medium text-slate-400">⚠️ DEMO PROTOTYPE — SYNTHETIC DATA</p>
          <p>All data is synthetic. Not connected to live government systems. Password for all accounts: <code className="px-1.5 py-0.5 bg-slate-700 rounded text-slate-300">demo123</code></p>
        </div>
      </main>
    </div>
  );
}
