import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPendingMatches, confirmMatch, rejectMatch } from '../../services/api';
import { GitMerge, Check, X } from 'lucide-react';

export default function AdminMatches() {
  const qc = useQueryClient();
  const { data: res } = useQuery({ queryKey: ['matches'], queryFn: getPendingMatches });
  const matches = res?.data?.data || [];

  const confirmMut = useMutation({ mutationFn: confirmMatch, onSuccess: () => qc.invalidateQueries({ queryKey: ['matches'] }) });
  const rejectMut = useMutation({ mutationFn: (id: string) => rejectMatch(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['matches'] }) });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-2">Duplicate Identity Matches</h1>
      <p className="text-sm text-slate-400 mb-6">Review potential duplicate records detected by the identity resolution engine</p>

      {matches.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-10 text-center text-slate-500">No pending matches</div>
      ) : (
        <div className="space-y-4">
          {matches.map((m: any) => (
            <div key={m.match_id} className="bg-slate-800 border border-slate-700 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <GitMerge className="w-5 h-5 text-amber-400" />
                  <span className="font-mono text-sm text-white">{m.match_id}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                    m.confidence_score >= 90 ? 'bg-red-500/20 text-red-400' : m.confidence_score >= 80 ? 'bg-amber-500/20 text-amber-400' : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {m.confidence_score}% confidence
                  </span>
                  <span className="px-2 py-0.5 bg-slate-700 text-slate-300 text-[10px] rounded-full">{m.match_type}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="text-xs text-slate-400 mb-1">RECORD A</div>
                  <div className="text-white font-medium">{m.record_a_name}</div>
                  <div className="text-xs text-slate-400">{m.record_a_id} · Source: {m.record_a_source}</div>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="text-xs text-slate-400 mb-1">RECORD B</div>
                  <div className="text-white font-medium">{m.record_b_name}</div>
                  <div className="text-xs text-slate-400">{m.record_b_id} · Source: {m.record_b_source}</div>
                </div>
              </div>

              {m.match_reasons && (
                <div className="text-xs text-slate-400 mb-4">
                  Match reasons: {typeof m.match_reasons === 'string' ? JSON.parse(m.match_reasons).join(', ') : '—'}
                </div>
              )}

              <div className="flex gap-2">
                <button onClick={() => confirmMut.mutate(m.match_id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium">
                  <Check className="w-3.5 h-3.5" /> Confirm Match
                </button>
                <button onClick={() => rejectMut.mutate(m.match_id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-medium">
                  <X className="w-3.5 h-3.5" /> Reject Match
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
