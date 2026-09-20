import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getFamilies } from '../../services/api';
import { Link } from 'react-router-dom';
import { Search, Eye, ChevronLeft, ChevronRight } from 'lucide-react';

export default function AdminFamilies() {
  const [search, setSearch] = useState('');
  const [district, setDistrict] = useState('');
  const [verification, setVerification] = useState('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data: res, isLoading } = useQuery({
    queryKey: ['families', search, district, verification, page],
    queryFn: () => getFamilies({ q: search || undefined, district: district || undefined, verification: verification || undefined, limit, offset: page * limit }),
  });

  const families = res?.data?.data?.families || [];
  const total = res?.data?.data?.total || 0;

  const statusBadge: Record<string, string> = {
    verified: 'bg-emerald-500/20 text-emerald-400', pending: 'bg-amber-500/20 text-amber-400',
    partially_verified: 'bg-blue-500/20 text-blue-400', rejected: 'bg-red-500/20 text-red-400',
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Family Search</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            placeholder="Search by Family ID, Member ID, or Name..."
            className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-400 focus:ring-2 focus:ring-amber-500 focus:border-amber-500" />
        </div>
        <select value={district} onChange={(e) => { setDistrict(e.target.value); setPage(0); }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
          <option value="">All Districts</option>
          {['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Gandhinagar'].map((d) => <option key={d}>{d}</option>)}
        </select>
        <select value={verification} onChange={(e) => { setVerification(e.target.value); setPage(0); }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
          <option value="">All Status</option>
          <option value="verified">Verified</option>
          <option value="pending">Pending</option>
          <option value="partially_verified">Partially Verified</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3">Pravi ID</th>
              <th className="text-left px-4 py-3">District</th>
              <th className="text-left px-4 py-3">Taluka</th>
              <th className="text-left px-4 py-3">Members</th>
              <th className="text-left px-4 py-3">Income</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Quality</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={8} className="text-center py-8 text-slate-500">Loading...</td></tr>
            ) : families.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-8 text-slate-500">No families found</td></tr>
            ) : families.map((f: any) => (
              <tr key={f.family_id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                <td className="px-4 py-3 font-mono text-white text-xs">{f.family_id}</td>
                <td className="px-4 py-3 text-slate-300">{f.district}</td>
                <td className="px-4 py-3 text-slate-400">{f.taluka}</td>
                <td className="px-4 py-3 text-slate-300">{f.member_count}</td>
                <td className="px-4 py-3 text-slate-400">{f.income_band || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusBadge[f.verification_status] || ''}`}>
                    {f.verification_status?.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs ${f.data_quality_score >= 80 ? 'text-emerald-400' : f.data_quality_score >= 60 ? 'text-amber-400' : 'text-red-400'}`}>
                    {f.data_quality_score}%
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Link to={`/admin/families/${f.family_id}`}
                    className="flex items-center gap-1 text-amber-400 hover:text-amber-300 text-xs">
                    <Eye className="w-3.5 h-3.5" /> View 360
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
        <span>Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
            className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg disabled:opacity-50 hover:bg-slate-700">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button onClick={() => setPage(page + 1)} disabled={(page + 1) * limit >= total}
            className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg disabled:opacity-50 hover:bg-slate-700">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
