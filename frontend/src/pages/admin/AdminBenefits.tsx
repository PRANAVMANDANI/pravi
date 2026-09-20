import { useQuery } from '@tanstack/react-query';
import { getBenefits } from '../../services/api';
import { Award } from 'lucide-react';

export default function AdminBenefits() {
  const { data: res } = useQuery({ queryKey: ['admin-benefits'], queryFn: () => getBenefits({ limit: 100 }) });
  const benefits = res?.data?.data || [];

  const statusBadge: Record<string, string> = {
    active: 'bg-emerald-500/20 text-emerald-400', completed: 'bg-blue-500/20 text-blue-400',
    suspended: 'bg-amber-500/20 text-amber-400', cancelled: 'bg-red-500/20 text-red-400',
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Benefit Ledger</h1>
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
            <th className="text-left px-4 py-3">Benefit ID</th><th className="text-left px-4 py-3">Family</th>
            <th className="text-left px-4 py-3">Scheme</th><th className="text-left px-4 py-3">Type</th>
            <th className="text-left px-4 py-3">Amount</th><th className="text-left px-4 py-3">Status</th>
            <th className="text-left px-4 py-3">Department</th>
          </tr></thead>
          <tbody>
            {benefits.map((b: any) => (
              <tr key={b.benefit_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-4 py-3 font-mono text-white text-xs">{b.benefit_id}</td>
                <td className="px-4 py-3 text-slate-400 text-xs">{b.family_id}</td>
                <td className="px-4 py-3 text-slate-300 text-xs">{b.scheme_id}</td>
                <td className="px-4 py-3 text-slate-400 text-xs">{b.benefit_type}</td>
                <td className="px-4 py-3 text-emerald-400 text-xs">{b.amount ? `₹${b.amount.toLocaleString()}` : '—'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge[b.status]}`}>{b.status}</span></td>
                <td className="px-4 py-3 text-slate-500 text-xs">{b.department_name || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
