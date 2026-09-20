import { useQuery } from '@tanstack/react-query';
import { getChangeRequests } from '../../services/api';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Eye, Filter } from 'lucide-react';

export default function AdminRequests() {
  const [status, setStatus] = useState('');
  const [type, setType] = useState('');
  const { data: res } = useQuery({
    queryKey: ['admin-requests', status, type],
    queryFn: () => getChangeRequests({ status: status || undefined, request_type: type || undefined, limit: 100 }),
  });
  const requests = res?.data?.data || [];

  const statusBadge: Record<string, string> = {
    submitted: 'bg-blue-500/20 text-blue-400', under_review: 'bg-amber-500/20 text-amber-400',
    more_info_required: 'bg-orange-500/20 text-orange-400', approved: 'bg-emerald-500/20 text-emerald-400',
    rejected: 'bg-red-500/20 text-red-400',
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Change Requests</h1>
      <div className="flex gap-3 mb-4">
        <select value={status} onChange={(e) => setStatus(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
          <option value="">All Status</option>
          <option value="submitted">Submitted</option><option value="under_review">Under Review</option>
          <option value="approved">Approved</option><option value="rejected">Rejected</option>
          <option value="more_info_required">More Info Required</option>
        </select>
        <select value={type} onChange={(e) => setType(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
          <option value="">All Types</option>
          {['name','dob','gender','address','occupation','income','member_addition','member_removal','relationship'].map(t =>
            <option key={t} value={t}>{t.replace('_',' ')}</option>
          )}
        </select>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
            <th className="text-left px-4 py-3">Request ID</th><th className="text-left px-4 py-3">Family</th>
            <th className="text-left px-4 py-3">Type</th><th className="text-left px-4 py-3">Current → Requested</th>
            <th className="text-left px-4 py-3">Status</th><th className="text-left px-4 py-3">Date</th><th className="px-4 py-3"></th>
          </tr></thead>
          <tbody>
            {requests.map((r: any) => (
              <tr key={r.request_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-4 py-3 font-mono text-white text-xs">{r.request_id}</td>
                <td className="px-4 py-3 text-slate-400 text-xs">{r.family_id}</td>
                <td className="px-4 py-3 text-slate-300 capitalize text-xs">{r.request_type.replace('_',' ')}</td>
                <td className="px-4 py-3 text-xs"><span className="text-slate-400">{r.current_value || '—'}</span> → <span className="text-white">{r.requested_value || '—'}</span></td>
                <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[r.status]}`}>{r.status.replace('_',' ')}</span></td>
                <td className="px-4 py-3 text-slate-500 text-xs">{r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}</td>
                <td className="px-4 py-3"><Link to={`/admin/requests/${r.request_id}`} className="text-amber-400 hover:text-amber-300"><Eye className="w-4 h-4" /></Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
