import { useQuery } from '@tanstack/react-query';
import { getAnalytics } from '../../services/api';
import { Users, CheckCircle, Clock, FileText, GitMerge, Award, Calendar, AlertTriangle, BarChart3 } from 'lucide-react';

export default function AdminDashboard() {
  const { data: res } = useQuery({ queryKey: ['analytics'], queryFn: getAnalytics });
  const d = res?.data?.data;
  const overview = d?.overview || {};
  const requests = d?.requests || {};
  const charts = d?.charts || {};

  const stats = [
    { label: 'Total Families', value: overview.total_families, icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Verified', value: overview.verified_families, icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Pending Verification', value: overview.pending_verification, icon: Clock, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { label: 'Total Members', value: overview.total_members, icon: Users, color: 'text-violet-500', bg: 'bg-violet-500/10' },
    { label: 'Active Schemes', value: overview.total_schemes, icon: Award, color: 'text-indigo-500', bg: 'bg-indigo-500/10' },
    { label: 'Active Benefits', value: overview.active_benefits, icon: Award, color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { label: 'Pending Requests', value: requests.pending, icon: FileText, color: 'text-orange-500', bg: 'bg-orange-500/10' },
    { label: 'Duplicate Matches', value: overview.duplicate_matches, icon: GitMerge, color: 'text-rose-500', bg: 'bg-rose-500/10' },
    { label: 'Life Events', value: overview.total_life_events, icon: Calendar, color: 'text-cyan-500', bg: 'bg-cyan-500/10' },
    { label: 'Data Quality Issues', value: overview.data_quality_issues, icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10' },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Government Dashboard</h1>
        <p className="text-sm text-slate-400">Pravi ID — Statewide Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-8">
        {stats.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-2`}>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
            <div className="text-xs text-slate-400">{label}</div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Families by District */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-400" /> Families by District
          </h3>
          <div className="space-y-2">
            {(charts.families_by_district || []).map((d: any) => (
              <div key={d.district} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-24 truncate">{d.district}</span>
                <div className="flex-1 bg-slate-700 rounded-full h-4 overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all"
                    style={{ width: `${Math.min(100, (d.count / (overview.total_families || 1)) * 100)}%` }} />
                </div>
                <span className="text-xs text-slate-300 w-8 text-right">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Request Status */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-400" /> Change Requests
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Total', value: requests.total, color: 'text-white' },
              { label: 'Pending', value: requests.pending, color: 'text-amber-400' },
              { label: 'Approved', value: requests.approved, color: 'text-emerald-400' },
              { label: 'Rejected', value: requests.rejected, color: 'text-red-400' },
            ].map((s) => (
              <div key={s.label} className="bg-slate-700/50 rounded-lg p-3">
                <div className={`text-xl font-bold ${s.color}`}>{s.value ?? 0}</div>
                <div className="text-xs text-slate-400">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Request Types */}
          <div className="mt-4 space-y-1.5">
            {(charts.request_types || []).slice(0, 5).map((r: any) => (
              <div key={r.type} className="flex items-center justify-between text-xs">
                <span className="text-slate-400 capitalize">{r.type.replace('_', ' ')}</span>
                <span className="text-slate-300">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Income Distribution */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Income Distribution</h3>
          <div className="space-y-2">
            {(charts.income_distribution || []).map((i: any) => (
              <div key={i.band} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-16">{i.band}</span>
                <div className="flex-1 bg-slate-700 rounded-full h-3 overflow-hidden">
                  <div className="bg-gradient-to-r from-amber-500 to-orange-500 h-full rounded-full"
                    style={{ width: `${Math.min(100, (i.count / (overview.total_families || 1)) * 100)}%` }} />
                </div>
                <span className="text-xs text-slate-300 w-8 text-right">{i.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Verification */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Verification Status</h3>
          <div className="space-y-2">
            {(charts.verification_distribution || []).map((v: any) => {
              const colors: Record<string, string> = { verified: 'from-emerald-500 to-green-500', pending: 'from-amber-500 to-yellow-500', partially_verified: 'from-blue-500 to-indigo-500' };
              return (
                <div key={v.status} className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 w-28 capitalize">{v.status.replace('_', ' ')}</span>
                  <div className="flex-1 bg-slate-700 rounded-full h-3 overflow-hidden">
                    <div className={`bg-gradient-to-r ${colors[v.status] || 'from-slate-500 to-slate-400'} h-full rounded-full`}
                      style={{ width: `${Math.min(100, (v.count / (overview.total_families || 1)) * 100)}%` }} />
                  </div>
                  <span className="text-xs text-slate-300 w-8 text-right">{v.count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="mt-6 text-center text-xs text-slate-500">
        DEMO PROTOTYPE — All data is synthetic. Not connected to live government systems.
      </div>
    </div>
  );
}
