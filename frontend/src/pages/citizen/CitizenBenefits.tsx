import { useQuery } from '@tanstack/react-query';
import { getBenefits } from '../../services/api';
import { Award, IndianRupee } from 'lucide-react';

export default function CitizenBenefits() {
  const { data: res } = useQuery({ queryKey: ['benefits'], queryFn: () => getBenefits() });
  const benefits = res?.data?.data || [];

  const statusColor: Record<string, string> = {
    active: 'bg-emerald-100 text-emerald-700', completed: 'bg-blue-100 text-blue-700',
    suspended: 'bg-amber-100 text-amber-700', cancelled: 'bg-red-100 text-red-700',
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-xl font-bold text-slate-800 mb-2">My Benefits</h1>
      <p className="text-sm text-slate-500 mb-6">History of government benefits received by your family</p>

      {benefits.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-10 text-center text-slate-500">No benefits recorded yet.</div>
      ) : (
        <div className="space-y-3">
          {benefits.map((b: any) => (
            <div key={b.benefit_id} className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-100 flex items-center justify-center">
                    <Award className="w-5 h-5 text-violet-600" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-800">{b.description || b.scheme_id}</div>
                    <div className="text-xs text-slate-500">{b.benefit_id} · {b.department_name || '—'}</div>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColor[b.status] || 'bg-slate-100'}`}>{b.status}</span>
              </div>
              <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-600">
                {b.amount && <span className="flex items-center gap-1"><IndianRupee className="w-3.5 h-3.5" />₹{b.amount.toLocaleString()}</span>}
                <span>Type: {b.benefit_type}</span>
                <span>Frequency: {b.frequency}</span>
                {b.period_start && <span>From: {new Date(b.period_start).toLocaleDateString()}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
