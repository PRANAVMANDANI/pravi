import { useQuery } from '@tanstack/react-query';
import { getDepartments } from '../../services/api';
import { Building2, Shield, Eye, Lock } from 'lucide-react';

export default function AdminDepartments() {
  const { data: res, isLoading } = useQuery({
    queryKey: ['admin-departments'],
    queryFn: () => getDepartments(),
  });

  const rawDepts = res?.data?.data || res?.data;
  const departments = Array.isArray(rawDepts) ? rawDepts : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Inter-Department Access Governance</h1>
        <p className="text-slate-500">Government departments and scope-restricted access controls</p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-slate-500">Loading departments...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {departments.map((dept: any) => (
            <div key={dept.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                    <Building2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 text-lg">{dept.name}</h3>
                    <span className="text-xs font-mono text-slate-400">Code: {dept.code}</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Active Access
                </span>
              </div>

              <div className="space-y-3 border-t border-slate-100 pt-4 text-sm text-slate-600">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Eye className="w-4 h-4 text-slate-400" /> Read Scope
                  </span>
                  <span className="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                    {dept.allowed_read_fields?.join(', ') || 'Demographics, Income'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Lock className="w-4 h-4 text-amber-500" /> Restricted Fields
                  </span>
                  <span className="font-mono text-xs bg-amber-50 text-amber-800 px-2 py-0.5 rounded">
                    Bank Accounts, Aadhaar Numbers
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
