import { useQuery } from '@tanstack/react-query';
import { getLifeEvents } from '../../services/api';
import { Calendar, CheckCircle, Clock, XCircle } from 'lucide-react';

export default function CitizenEvents() {
  const { data: res } = useQuery({ queryKey: ['events'], queryFn: () => getLifeEvents() });
  const events = res?.data?.data || [];

  const statusIcon: Record<string, { icon: any; color: string }> = {
    submitted: { icon: Clock, color: 'text-blue-500' },
    approved: { icon: CheckCircle, color: 'text-emerald-500' },
    rejected: { icon: XCircle, color: 'text-red-500' },
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-xl font-bold text-slate-800 mb-2">Life Events</h1>
      <p className="text-sm text-slate-500 mb-6">Tracked life events for your family</p>

      {events.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-10 text-center text-slate-500">No life events recorded.</div>
      ) : (
        <div className="space-y-3">
          {events.map((e: any) => {
            const st = statusIcon[e.status] || statusIcon.submitted;
            const Icon = st.icon;
            return (
              <div key={e.event_id} className="bg-white rounded-xl border border-slate-200 p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <div className="font-medium text-slate-800 capitalize">{e.event_type.replace('_', ' ')}</div>
                      <div className="text-xs text-slate-500">{e.event_id} · {e.description || '—'}</div>
                    </div>
                  </div>
                  <div className={`flex items-center gap-1 ${st.color}`}>
                    <Icon className="w-4 h-4" />
                    <span className="text-xs font-medium">{e.status}</span>
                  </div>
                </div>
                {e.new_member_name && <div className="text-sm text-slate-600 mt-2">New member: {e.new_member_name}</div>}
                <div className="text-xs text-slate-400 mt-2">{e.event_date ? new Date(e.event_date).toLocaleDateString() : ''}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
