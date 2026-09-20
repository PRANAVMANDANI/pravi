import { useQuery } from '@tanstack/react-query';
import { getChangeRequests } from '../../services/api';
import { Link } from 'react-router-dom';
import { Plus, Clock, CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

export default function CitizenRequests() {
  const { data: res } = useQuery({ queryKey: ['requests'], queryFn: () => getChangeRequests() });
  const requests = res?.data?.data || [];

  const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
    submitted: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100' },
    under_review: { icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
    more_info_required: { icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-100' },
    approved: { icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-100' },
    rejected: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' },
  };

  return (
    <div className="max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-800">My Change Requests</h1>
          <p className="text-sm text-slate-500 mt-1">Track requests to correct or update your family information</p>
        </div>
        <Link to="/citizen/requests/new"
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> New Request
        </Link>
      </div>

      {requests.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-10 text-center">
          <Info className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-slate-500">No requests submitted yet.</p>
          <Link to="/citizen/requests/new" className="text-amber-600 text-sm underline mt-2 inline-block">Submit your first request</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {requests.map((r: any) => {
            const st = statusConfig[r.status] || statusConfig.submitted;
            const Icon = st.icon;
            return (
              <div key={r.request_id} className="bg-white rounded-xl border border-slate-200 p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-slate-800">{r.request_id}</span>
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-[10px] rounded-full uppercase">{r.request_type.replace('_', ' ')}</span>
                    </div>
                    <div className="text-sm text-slate-600 mt-1">
                      {r.current_value && <span>Current: <strong>{r.current_value}</strong></span>}
                      {r.requested_value && <span> → Requested: <strong>{r.requested_value}</strong></span>}
                    </div>
                    {r.reason && <div className="text-xs text-slate-500 mt-1">Reason: {r.reason}</div>}
                    {r.rejection_reason && <div className="text-xs text-red-500 mt-1">Rejection: {r.rejection_reason}</div>}
                    {r.review_notes && <div className="text-xs text-amber-600 mt-1">Officer notes: {r.review_notes}</div>}
                  </div>
                  <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${st.bg} ${st.color}`}>
                    <Icon className="w-3.5 h-3.5" />
                    {r.status.replace('_', ' ')}
                  </div>
                </div>
                <div className="text-xs text-slate-400 mt-2">Submitted: {new Date(r.created_at).toLocaleDateString()}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
