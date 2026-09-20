import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getNotifications, markNotificationRead, markAllRead } from '../../services/api';
import { Bell, Check, CheckCheck } from 'lucide-react';

export default function CitizenNotifications() {
  const qc = useQueryClient();
  const { data: res } = useQuery({ queryKey: ['notifications'], queryFn: () => getNotifications() });
  const notifications = res?.data?.data?.notifications || [];
  const unread = res?.data?.data?.unread_count || 0;

  const readMut = useMutation({ mutationFn: markNotificationRead, onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }) });
  const readAllMut = useMutation({ mutationFn: markAllRead, onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }) });

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Notifications</h1>
          <p className="text-sm text-slate-500">{unread} unread</p>
        </div>
        {unread > 0 && (
          <button onClick={() => readAllMut.mutate()} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-amber-600 hover:bg-amber-50 rounded-lg">
            <CheckCheck className="w-4 h-4" /> Mark all read
          </button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.map((n: any) => (
          <div key={n.notification_id}
            className={`bg-white rounded-xl border p-4 flex items-start gap-3 ${n.is_read ? 'border-slate-200' : 'border-amber-200 bg-amber-50/30'}`}>
            <Bell className={`w-4 h-4 mt-1 ${n.is_read ? 'text-slate-400' : 'text-amber-500'}`} />
            <div className="flex-1">
              <div className="text-sm font-medium text-slate-800">{n.title}</div>
              {n.message && <div className="text-xs text-slate-500 mt-1">{n.message}</div>}
              <div className="text-xs text-slate-400 mt-1">{new Date(n.created_at).toLocaleString()}</div>
            </div>
            {!n.is_read && (
              <button onClick={() => readMut.mutate(n.notification_id)} className="p-1 hover:bg-slate-100 rounded">
                <Check className="w-4 h-4 text-slate-400" />
              </button>
            )}
          </div>
        ))}
        {notifications.length === 0 && (
          <div className="text-center py-10 text-slate-500">No notifications yet.</div>
        )}
      </div>
    </div>
  );
}
