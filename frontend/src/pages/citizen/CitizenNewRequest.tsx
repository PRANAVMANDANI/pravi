import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { createChangeRequest } from '../../services/api';
import { CheckCircle, Send } from 'lucide-react';

const REQUEST_TYPES = [
  { value: 'name', label: 'Name Correction' },
  { value: 'dob', label: 'Date of Birth Correction' },
  { value: 'gender', label: 'Gender Correction' },
  { value: 'address', label: 'Address Change' },
  { value: 'occupation', label: 'Occupation Update' },
  { value: 'income', label: 'Income Update' },
  { value: 'member_addition', label: 'Add Family Member' },
  { value: 'member_removal', label: 'Remove Family Member' },
  { value: 'relationship', label: 'Relationship Correction' },
  { value: 'marriage', label: 'Marriage Related' },
  { value: 'birth', label: 'Birth Related' },
  { value: 'death', label: 'Death Related' },
  { value: 'other', label: 'Other Correction' },
];

export default function CitizenNewRequest() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    request_type: '', field_name: '', current_value: '', requested_value: '', reason: '',
  });
  const [success, setSuccess] = useState(false);
  const [resultId, setResultId] = useState('');

  const mutation = useMutation({
    mutationFn: (data: any) => createChangeRequest(data),
    onSuccess: (res) => {
      setSuccess(true);
      setResultId(res.data.data.request_id);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      family_id: user?.family_id,
      ...form,
      field_name: form.field_name || form.request_type,
    });
  };

  if (success) {
    return (
      <div className="max-w-lg mx-auto mt-10">
        <div className="bg-white rounded-xl border border-emerald-200 p-8 text-center">
          <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-800 mb-2">Request Submitted</h2>
          <p className="text-sm text-slate-600 mb-4">
            Your request <strong>{resultId}</strong> has been submitted successfully.<br />
            A verification officer will review it.
          </p>
          <p className="text-xs text-slate-500 mb-6">
            ℹ️ Your data has <strong>NOT</strong> been changed. Only after government approval will the authoritative record be updated.
          </p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => navigate('/citizen/requests')} className="px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600">
              Track Requests
            </button>
            <button onClick={() => { setSuccess(false); setForm({ request_type: '', field_name: '', current_value: '', requested_value: '', reason: '' }); }}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200">
              New Request
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-xl font-bold text-slate-800 mb-2">Submit a Change Request</h1>
      <p className="text-sm text-slate-500 mb-6">
        Request a correction or update to your family information. A government officer will review and verify your request.
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">What would you like to change?</label>
          <select value={form.request_type} onChange={(e) => setForm({ ...form, request_type: e.target.value })}
            required className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500">
            <option value="">Select type...</option>
            {REQUEST_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Current Value</label>
          <input type="text" value={form.current_value} onChange={(e) => setForm({ ...form, current_value: e.target.value })}
            placeholder="What is currently recorded" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Requested Value</label>
          <input type="text" value={form.requested_value} onChange={(e) => setForm({ ...form, requested_value: e.target.value })}
            required placeholder="What it should be changed to" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Reason</label>
          <textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })}
            required rows={3} placeholder="Why this change is needed" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500" />
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-700">
          ⚠️ Submitting this request will NOT directly change your records. A government verification officer will review your request and supporting documents before any changes are made.
        </div>

        <button type="submit" disabled={mutation.isPending || !form.request_type}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-300 text-white rounded-lg text-sm font-medium transition-colors">
          <Send className="w-4 h-4" />
          {mutation.isPending ? 'Submitting...' : 'Submit Request'}
        </button>

        {mutation.isError && (
          <div className="text-sm text-red-600 bg-red-50 rounded-lg p-3">
            {(mutation.error as any)?.response?.data?.detail || 'Failed to submit request'}
          </div>
        )}
      </form>
    </div>
  );
}
