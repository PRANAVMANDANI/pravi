import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { getFamily, getFamilyMembers } from '../../services/api';
import { User, MapPin, Briefcase, GraduationCap, Calendar } from 'lucide-react';

export default function CitizenFamily() {
  const { user } = useAuth();
  const fid = user?.family_id || '';
  const { data: familyRes } = useQuery({ queryKey: ['family', fid], queryFn: () => getFamily(fid), enabled: !!fid });
  const { data: membersRes } = useQuery({ queryKey: ['members', fid], queryFn: () => getFamilyMembers(fid), enabled: !!fid });

  const family = familyRes?.data?.data;
  const members = membersRes?.data?.data || [];

  const statusBadge: Record<string, string> = {
    verified: 'bg-emerald-100 text-emerald-700', pending: 'bg-amber-100 text-amber-700',
    partially_verified: 'bg-blue-100 text-blue-700',
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-xl font-bold text-slate-800 mb-6">My Family</h1>

      {family && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="text-xs text-slate-500 uppercase tracking-wider">Pravi ID</div>
              <div className="text-lg font-bold font-mono text-slate-800">{family.family_id}</div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge[family.verification_status] || 'bg-slate-100'}`}>
              {family.verification_status?.replace('_', ' ')?.toUpperCase()}
            </span>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div><span className="text-slate-500">District</span><div className="font-medium text-slate-800">{family.district || '—'}</div></div>
            <div><span className="text-slate-500">Taluka</span><div className="font-medium text-slate-800">{family.taluka || '—'}</div></div>
            <div><span className="text-slate-500">Village/City</span><div className="font-medium text-slate-800">{family.village_city || '—'}</div></div>
            <div><span className="text-slate-500">Income Band</span><div className="font-medium text-slate-800">{family.income_band || '—'}</div></div>
          </div>
          {family.address_line && (
            <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
              <MapPin className="w-4 h-4 text-slate-400" />
              {family.address_line}
            </div>
          )}
        </div>
      )}

      <h2 className="text-lg font-semibold text-slate-800 mb-4">Family Members ({members.filter((m: any) => m.is_active).length})</h2>
      <div className="space-y-3">
        {members.filter((m: any) => m.is_active).map((m: any) => (
          <div key={m.member_id} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                  <User className="w-5 h-5 text-slate-500" />
                </div>
                <div>
                  <div className="font-semibold text-slate-800">{m.name}</div>
                  <div className="text-xs text-slate-500">{m.member_id} · {m.relationship_to_head || '—'}{m.is_head ? ' (Head)' : ''}</div>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusBadge[m.verification_status] || 'bg-slate-100 text-slate-600'}`}>
                {m.verification_status}
              </span>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-3 text-sm">
              <div className="flex items-center gap-1.5 text-slate-600">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                {m.dob ? `${m.dob} (Age: ${m.age})` : 'DOB not set'}
              </div>
              <div className="text-slate-600">{m.gender ? m.gender.charAt(0).toUpperCase() + m.gender.slice(1) : '—'}</div>
              <div className="flex items-center gap-1.5 text-slate-600">
                <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                {m.occupation || '—'}
              </div>
              <div className="flex items-center gap-1.5 text-slate-600">
                <GraduationCap className="w-3.5 h-3.5 text-slate-400" />
                {m.education || '—'}
              </div>
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-400 mt-6">
        ℹ️ This data is maintained by the government. If any information is incorrect, please <a href="/citizen/requests/new" className="text-amber-600 underline">submit a change request</a>.
      </p>
    </div>
  );
}
