import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getFamily360 } from '../../services/api';
import { User, MapPin, CheckCircle, XCircle, AlertTriangle, Clock, Shield, ScrollText, GitMerge } from 'lucide-react';

export default function AdminFamily360() {
  const { familyId } = useParams<{ familyId: string }>();
  const { data: res, isLoading } = useQuery({ queryKey: ['family360', familyId], queryFn: () => getFamily360(familyId!), enabled: !!familyId });

  if (isLoading) return <div className="text-slate-400 text-center py-20">Loading Family 360...</div>;
  const d = res?.data?.data;
  if (!d) return <div className="text-slate-400 text-center py-20">Family not found</div>;

  const { family, members, benefits, eligibility, change_requests, life_events, audit_logs, duplicate_matches, data_quality } = d;

  const statusBadge: Record<string, string> = {
    verified: 'bg-emerald-500/20 text-emerald-400', pending: 'bg-amber-500/20 text-amber-400',
    partially_verified: 'bg-blue-500/20 text-blue-400',
    eligible: 'bg-emerald-500/20 text-emerald-400', not_eligible: 'bg-red-500/20 text-red-400',
    needs_verification: 'bg-amber-500/20 text-amber-400',
    active: 'bg-emerald-500/20 text-emerald-400', completed: 'bg-blue-500/20 text-blue-400',
    submitted: 'bg-blue-500/20 text-blue-400', approved: 'bg-emerald-500/20 text-emerald-400',
    rejected: 'bg-red-500/20 text-red-400',
  };

  return (
    <div>
      {/* Header */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Pravi ID — Family 360</div>
            <div className="text-2xl font-bold font-mono text-white">{family.family_id}</div>
            <div className="flex items-center gap-4 mt-2 text-sm text-slate-400">
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{family.address_line || '—'}</span>
              <span>{family.district}, {family.taluka}</span>
            </div>
          </div>
          <div className="text-right">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge[family.verification_status]}`}>
              {family.verification_status?.replace('_', ' ')?.toUpperCase()}
            </span>
            <div className="mt-2 text-xs text-slate-400">Income: <strong className="text-white">{family.income_band || '—'}</strong></div>
            <div className="text-xs text-slate-400">Category: <strong className="text-white">{family.category || '—'}</strong></div>
          </div>
        </div>

        {/* Data Quality */}
        <div className="mt-4 flex items-center gap-3">
          <div className="text-xs text-slate-400">Data Quality:</div>
          <div className="flex-1 max-w-xs bg-slate-700 rounded-full h-2.5">
            <div className={`h-full rounded-full ${data_quality.score >= 80 ? 'bg-emerald-500' : data_quality.score >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
              style={{ width: `${data_quality.score}%` }} />
          </div>
          <span className={`text-sm font-bold ${data_quality.score >= 80 ? 'text-emerald-400' : data_quality.score >= 60 ? 'text-amber-400' : 'text-red-400'}`}>
            {data_quality.score}%
          </span>
          {data_quality.issue_count > 0 && <span className="text-xs text-red-400">({data_quality.issue_count} issues)</span>}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Members */}
        <div className="lg:col-span-2 space-y-6">
          {/* Members */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-blue-400" /> Family Members ({members.filter((m: any) => m.is_active).length})
            </h3>
            <div className="space-y-3">
              {members.filter((m: any) => m.is_active).map((m: any) => (
                <div key={m.member_id} className="bg-slate-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-white">{m.name} {m.is_head ? '👑' : ''}</div>
                      <div className="text-xs text-slate-400">{m.member_id} · {m.relationship_to_head} · {m.gender}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[m.verification_status]}`}>{m.verification_status}</span>
                  </div>
                  <div className="flex gap-4 mt-2 text-xs text-slate-400">
                    <span>DOB: {m.dob || '—'}</span>
                    <span>Age: {m.age ?? '—'}</span>
                    <span>Occupation: {m.occupation || '—'}</span>
                    <span>ID: {m.aadhaar_masked || '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Eligibility */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" /> Scheme Eligibility
            </h3>
            <div className="space-y-2">
              {eligibility.map((e: any) => {
                const icon = e.status === 'eligible' ? '✓' : e.status === 'not_eligible' ? '✕' : '?';
                return (
                  <div key={e.scheme_id} className="flex items-center justify-between bg-slate-700/50 rounded-lg px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-lg ${e.status === 'eligible' ? 'text-emerald-400' : e.status === 'not_eligible' ? 'text-red-400' : 'text-amber-400'}`}>{icon}</span>
                      <span className="text-sm text-white">{e.scheme_id}</span>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[e.status]}`}>{e.status.replace('_', ' ')}</span>
                      {e.explanation && <div className="text-[10px] text-slate-400 mt-1 max-w-xs text-right">{e.explanation}</div>}
                    </div>
                  </div>
                );
              })}
              {eligibility.length === 0 && <div className="text-xs text-slate-500 text-center py-4">No eligibility results</div>}
            </div>
          </div>

          {/* Benefits */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Benefits ({benefits.length})</h3>
            {benefits.length === 0 ? <div className="text-xs text-slate-500 text-center py-4">No benefits</div> : (
              <div className="space-y-2">
                {benefits.map((b: any) => (
                  <div key={b.benefit_id} className="flex items-center justify-between bg-slate-700/50 rounded-lg px-4 py-3">
                    <div>
                      <div className="text-sm text-white">{b.description || b.scheme_id}</div>
                      <div className="text-xs text-slate-400">{b.benefit_id} · {b.department_name || '—'}</div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[b.status]}`}>{b.status}</span>
                      {b.amount && <div className="text-xs text-emerald-400 mt-1">₹{b.amount.toLocaleString()}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right sidebar */}
        <div className="space-y-6">
          {/* Change Requests */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" /> Change Requests ({change_requests.length})
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {change_requests.map((r: any) => (
                <div key={r.request_id} className="bg-slate-700/50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-white">{r.request_id}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] ${statusBadge[r.status]}`}>{r.status}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1 capitalize">{r.request_type.replace('_', ' ')}</div>
                </div>
              ))}
              {change_requests.length === 0 && <div className="text-xs text-slate-500 text-center py-2">None</div>}
            </div>
          </div>

          {/* Life Events */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Life Events ({life_events.length})</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {life_events.map((e: any) => (
                <div key={e.event_id} className="bg-slate-700/50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-white capitalize">{e.event_type.replace('_', ' ')}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] ${statusBadge[e.status]}`}>{e.status}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">{e.event_id}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Duplicate Matches */}
          {duplicate_matches.length > 0 && (
            <div className="bg-slate-800 border border-red-500/30 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                <GitMerge className="w-4 h-4" /> Duplicate Warnings ({duplicate_matches.length})
              </h3>
              {duplicate_matches.map((m: any) => (
                <div key={m.match_id} className="bg-red-500/10 rounded-lg p-3 mb-2">
                  <div className="text-xs text-white">{m.record_a_name} ↔ {m.record_b_name}</div>
                  <div className="text-[10px] text-red-300">Confidence: {m.confidence_score}%</div>
                </div>
              ))}
            </div>
          )}

          {/* Audit Timeline */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <ScrollText className="w-4 h-4 text-indigo-400" /> Audit Trail
            </h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {audit_logs.slice(0, 15).map((a: any) => (
                <div key={a.audit_id} className="border-l-2 border-slate-600 pl-3 py-1">
                  <div className="text-xs text-white">{a.action}</div>
                  <div className="text-[10px] text-slate-400">{a.actor_name} · {a.actor_role}</div>
                  <div className="text-[10px] text-slate-500">{new Date(a.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Data Quality Issues */}
          {data_quality.issues.length > 0 && (
            <div className="bg-slate-800 border border-amber-500/30 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Data Quality Issues
              </h3>
              {data_quality.issues.slice(0, 8).map((i: any, idx: number) => (
                <div key={idx} className="text-xs text-slate-300 py-1 border-b border-slate-700 last:border-0">
                  <span className={`inline-block w-2 h-2 rounded-full mr-2 ${i.severity === 'high' ? 'bg-red-400' : i.severity === 'medium' ? 'bg-amber-400' : 'bg-blue-400'}`} />
                  {i.issue}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
