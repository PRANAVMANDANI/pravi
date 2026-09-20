import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLifeEvents, approveLifeEvent, rejectLifeEvent } from '../../services/api';
import { useState } from 'react';
import { Calendar, CheckCircle, XCircle } from 'lucide-react';

export default function AdminEvents() {
  const qc = useQueryClient();
  const [status, setStatus] = useState('');
  const { data: res } = useQuery({ queryKey: ['admin-events', status], queryFn: () => getLifeEvents({ status: status || undefined, limit: 100 }) });
  const events = res?.data?.data || [];

  const approveMut = useMutation({ mutationFn: (id: string) => approveLifeEvent(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-events'] }) });
  const rejectMut = useMutation({ mutationFn: (id: string) => rejectLifeEvent(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-events'] }) });

  const statusBadge: Record<string, string> = {
    submitted: 'bg-blue-500/20 text-blue-400', approved: 'bg-emerald-500/20 text-emerald-400', rejected: 'bg-red-500/20 text-red-400',
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Life Events</h1>
      <div className="flex gap-3 mb-4">
        <select value={status} onChange={(e) => setStatus(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
          <option value="">All Status</option><option value="submitted">Submitted</option>
          <option value="approved">Approved</option><option value="rejected">Rejected</option>
        </select>
      </div>

      <div className="space-y-3">
        {events.map((e: any) => (
          <div key={e.event_id} className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-indigo-400" />
                <div>
                  <div className="text-white font-medium capitalize">{e.event_type.replace('_', ' ')}</div>
                  <div className="text-xs text-slate-400">{e.event_id} · Family: {e.family_id}</div>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[e.status]}`}>{e.status}</span>
            </div>
            {e.description && <div className="text-sm text-slate-300 mt-2">{e.description}</div>}
            {e.new_member_name && <div className="text-xs text-slate-400 mt-1">New member: {e.new_member_name} ({e.new_member_gender}, {e.new_member_relationship})</div>}
            {e.status === 'submitted' && (
              <div className="flex gap-2 mt-3">
                <button onClick={() => approveMut.mutate(e.event_id)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs">
                  <CheckCircle className="w-3.5 h-3.5" /> Approve
                </button>
                <button onClick={() => rejectMut.mutate(e.event_id)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs">
                  <XCircle className="w-3.5 h-3.5" /> Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
