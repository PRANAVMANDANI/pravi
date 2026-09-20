import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getChangeRequest, approveRequest, rejectRequest, requestMoreInfo } from '../../services/api';
import { useState } from 'react';
import { CheckCircle, XCircle, MessageSquare, ArrowLeft } from 'lucide-react';

export default function AdminRequestDetail() {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [notes, setNotes] = useState('');
  const [reason, setReason] = useState('');

  const { data: res } = useQuery({ queryKey: ['request', requestId], queryFn: () => getChangeRequest(requestId!), enabled: !!requestId });
  const r = res?.data?.data;

  const approveMut = useMutation({
    mutationFn: () => approveRequest(requestId!, { notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['request'] }); },
  });
  const rejectMut = useMutation({
    mutationFn: () => rejectRequest(requestId!, { reason }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['request'] }); },
  });
  const infoMut = useMutation({
    mutationFn: () => requestMoreInfo(requestId!, { notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['request'] }); },
  });

  if (!r) return <div className="text-slate-400 text-center py-20">Loading...</div>;

  const isPending = ['submitted', 'under_review', 'more_info_required'].includes(r.status);

  const statusColor: Record<string, string> = {
    submitted: 'bg-blue-500/20 text-blue-400', under_review: 'bg-amber-500/20 text-amber-400',
    approved: 'bg-emerald-500/20 text-emerald-400', rejected: 'bg-red-500/20 text-red-400',
    more_info_required: 'bg-orange-500/20 text-orange-400',
  };

  return (
    <div className="max-w-3xl">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-slate-400 hover:text-white text-sm mb-4">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wider">Change Request</div>
            <div className="text-xl font-bold font-mono text-white">{r.request_id}</div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor[r.status]}`}>{r.status.replace('_', ' ').toUpperCase()}</span>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm mb-6">
          <div><span className="text-slate-400">Family ID</span><div className="text-white font-mono">{r.family_id}</div></div>
          <div><span className="text-slate-400">Member ID</span><div className="text-white font-mono">{r.member_id || '—'}</div></div>
          <div><span className="text-slate-400">Request Type</span><div className="text-white capitalize">{r.request_type.replace('_', ' ')}</div></div>
          <div><span className="text-slate-400">Priority</span><div className="text-white capitalize">{r.priority}</div></div>
          <div><span className="text-slate-400">Submitted</span><div className="text-white">{r.created_at ? new Date(r.created_at).toLocaleString() : '—'}</div></div>
          {r.reviewed_at && <div><span className="text-slate-400">Reviewed</span><div className="text-white">{new Date(r.reviewed_at).toLocaleString()}</div></div>}
        </div>

        {/* Current vs Requested */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="text-xs text-red-400 mb-1">CURRENT VALUE</div>
            <div className="text-white">{r.current_value || '—'}</div>
          </div>
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
            <div className="text-xs text-emerald-400 mb-1">REQUESTED VALUE</div>
            <div className="text-white">{r.requested_value || '—'}</div>
          </div>
        </div>

        <div className="mb-4">
          <div className="text-xs text-slate-400 mb-1">REASON</div>
          <div className="text-sm text-slate-300 bg-slate-700/50 rounded-lg p-3">{r.reason || 'No reason provided'}</div>
        </div>

        {r.rejection_reason && (
          <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <div className="text-xs text-red-400 mb-1">REJECTION REASON</div>
            <div className="text-sm text-white">{r.rejection_reason}</div>
          </div>
        )}
        {r.review_notes && (
          <div className="mb-4 bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <div className="text-xs text-amber-400 mb-1">OFFICER NOTES</div>
            <div className="text-sm text-white">{r.review_notes}</div>
          </div>
        )}
      </div>

      {/* Actions */}
      {isPending && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-white mb-4">Officer Actions</h3>
          <div className="space-y-3 mb-4">
            <textarea value={notes} onChange={(e) => { setNotes(e.target.value); setReason(e.target.value); }}
              placeholder="Review notes / rejection reason..."
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-400 focus:ring-2 focus:ring-amber-500"
              rows={3} />
          </div>
          <div className="flex gap-3">
            <button onClick={() => approveMut.mutate()} disabled={approveMut.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
              <CheckCircle className="w-4 h-4" /> {approveMut.isPending ? 'Approving...' : 'Approve'}
            </button>
            <button onClick={() => rejectMut.mutate()} disabled={rejectMut.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
              <XCircle className="w-4 h-4" /> {rejectMut.isPending ? 'Rejecting...' : 'Reject'}
            </button>
            <button onClick={() => infoMut.mutate()} disabled={infoMut.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
              <MessageSquare className="w-4 h-4" /> Request More Info
            </button>
          </div>
          {(approveMut.isSuccess || rejectMut.isSuccess || infoMut.isSuccess) && (
            <div className="mt-3 text-sm text-emerald-400">✓ Action completed successfully. Record updated.</div>
          )}
        </div>
      )}
    </div>
  );
}
