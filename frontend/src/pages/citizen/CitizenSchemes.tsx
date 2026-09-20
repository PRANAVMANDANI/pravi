import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { getSchemes, getEligibility } from '../../services/api';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

export default function CitizenSchemes() {
  const { user } = useAuth();
  const fid = user?.family_id || '';
  const { data: schemesRes } = useQuery({ queryKey: ['schemes'], queryFn: () => getSchemes() });
  const { data: eligRes } = useQuery({ queryKey: ['eligibility', fid], queryFn: () => getEligibility(fid), enabled: !!fid });

  const schemes = schemesRes?.data?.data || [];
  const eligibility = eligRes?.data?.data || [];

  const getElig = (schemeId: string) => eligibility.find((e: any) => e.scheme_id === schemeId);

  const statusIcon: Record<string, any> = {
    eligible: { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-50 border-emerald-200', label: 'Eligible' },
    not_eligible: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-50 border-red-200', label: 'Not Eligible' },
    needs_verification: { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-50 border-amber-200', label: 'Verification Required' },
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-xl font-bold text-slate-800 mb-2">Government Schemes</h1>
      <p className="text-sm text-slate-500 mb-6">Available welfare schemes and your family's eligibility status</p>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-6 flex items-center gap-2 text-sm text-amber-700">
        <Info className="w-4 h-4 shrink-0" />
        DEMO SCHEMES — SYNTHETIC RULES. Not actual government scheme criteria.
      </div>

      <div className="space-y-4">
        {schemes.map((s: any) => {
          const elig = getElig(s.scheme_id);
          const st = statusIcon[elig?.status] || statusIcon.needs_verification;
          const Icon = st.icon;

          return (
            <div key={s.scheme_id} className={`bg-white rounded-xl border p-5 ${elig ? st.bg : 'border-slate-200'}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-slate-800">{s.name}</h3>
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-500 text-[10px] rounded-full">DEMO</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{s.description}</p>
                  <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-500">
                    <span>🏛️ {s.department_name}</span>
                    <span>💰 {s.benefit_value}</span>
                    <span>📅 {s.benefit_frequency}</span>
                    <span>👥 {s.target_group}</span>
                  </div>
                </div>
                {elig && (
                  <div className="flex items-center gap-1.5 ml-4 shrink-0">
                    <Icon className={`w-5 h-5 ${st.color}`} />
                    <span className={`text-sm font-medium ${st.color}`}>{st.label}</span>
                  </div>
                )}
              </div>
              {elig?.explanation && (
                <div className="mt-3 px-3 py-2 bg-white/50 rounded-lg text-xs text-slate-600">
                  💡 {elig.explanation}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
