import { useQuery } from '@tanstack/react-query';
import { getSchemes } from '../../services/api';
import { Gift } from 'lucide-react';

export default function AdminSchemes() {
  const { data: res } = useQuery({ queryKey: ['schemes'], queryFn: () => getSchemes() });
  const schemes = res?.data?.data || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Scheme Catalogue</h1>
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 mb-6 text-sm text-amber-400">
        ⚠️ DEMO SCHEMES — SYNTHETIC RULES. These are fictional schemes for demonstration purposes.
      </div>

      <div className="space-y-4">
        {schemes.map((s: any) => (
          <div key={s.scheme_id} className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                  <Gift className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">{s.name}</h3>
                  <div className="text-xs text-slate-400">{s.scheme_id} · {s.department_name}</div>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${s.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-500/20 text-slate-400'}`}>{s.status}</span>
            </div>
            <p className="text-sm text-slate-300 mt-3">{s.description}</p>
            <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-400">
              <span>💰 {s.benefit_value}</span>
              <span>📅 {s.benefit_frequency}</span>
              <span>🎯 {s.target_group}</span>
              <span>👥 {s.current_beneficiaries} beneficiaries</span>
            </div>

            {/* Rules */}
            {s.rules && s.rules.length > 0 && (
              <div className="mt-4">
                <div className="text-xs text-slate-400 mb-2">ELIGIBILITY RULES</div>
                <div className="space-y-1">
                  {s.rules.filter((r: any) => r.is_active).map((r: any) => (
                    <div key={r.id} className="bg-slate-700/50 rounded px-3 py-2 text-xs text-slate-300 flex items-center gap-2">
                      <span className="text-amber-400 font-mono">{r.entity}.{r.field}</span>
                      <span className="text-slate-500">{r.operator}</span>
                      <span className="text-white">{r.value}</span>
                      {r.description && <span className="text-slate-500 ml-2">— {r.description}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
