import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuditLogs } from '../../services/api';
import { Shield, Filter, Clock } from 'lucide-react';

export default function AdminAudit() {
  const [entityType, setEntityType] = useState('');
  const { data: res, isLoading } = useQuery({
    queryKey: ['admin-audit', entityType],
    queryFn: () => getAuditLogs(entityType ? { entity_type: entityType } : undefined),
  });

  const rawLogs = res?.data?.data || res?.data;
  const logs = Array.isArray(rawLogs) ? rawLogs : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Shield className="w-7 h-7 text-indigo-600" /> Immutable Audit Ledger
          </h1>
          <p className="text-slate-500">Government compliance and tamper-evident audit trail for all operations</p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Entity Types</option>
            <option value="FAMILY">FAMILY</option>
            <option value="MEMBER">MEMBER</option>
            <option value="CHANGE_REQUEST">CHANGE_REQUEST</option>
            <option value="IDENTITY_MATCH">IDENTITY_MATCH</option>
            <option value="LIFE_EVENT">LIFE_EVENT</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading audit ledger...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No audit records found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="p-4">Timestamp</th>
                  <th className="p-4">Actor</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Action</th>
                  <th className="p-4">Entity</th>
                  <th className="p-4">Entity ID</th>
                  <th className="p-4">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {logs.map((log: any, idx: number) => {
                  const dateStr = log.created_at || log.timestamp;
                  const formattedDate = dateStr ? new Date(dateStr).toLocaleString() : '-';
                  const entityIdStr = log.entity_id ? String(log.entity_id) : '-';
                  const detailsText = log.description || log.reason || (log.changes ? JSON.stringify(log.changes) : log.metadata ? JSON.stringify(log.metadata) : '-');

                  return (
                    <tr key={log.audit_id || log.id || idx} className="hover:bg-slate-50/80 transition">
                      <td className="p-4 whitespace-nowrap text-slate-500 font-mono text-xs flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        {formattedDate}
                      </td>
                      <td className="p-4 font-medium text-slate-800">{log.actor_name || (log.actor_id ? `User #${log.actor_id}` : 'System')}</td>
                      <td className="p-4">
                        <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-100 text-slate-700 uppercase">
                          {log.actor_role || 'SYSTEM'}
                        </span>
                      </td>
                      <td className="p-4 font-mono text-xs text-indigo-700 font-semibold">{log.action || '-'}</td>
                      <td className="p-4 font-mono text-xs text-slate-600">{log.entity_type || '-'}</td>
                      <td className="p-4 font-mono text-xs text-slate-500 truncate max-w-[120px]" title={entityIdStr}>
                        {entityIdStr}
                      </td>
                      <td className="p-4 text-xs font-mono text-slate-600 max-w-xs truncate" title={detailsText}>
                        {detailsText}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

