"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Loader2, CheckCircle2, XCircle, ExternalLink, Terminal, Copy, Check } from 'lucide-react';

interface PendingRequest {
  id: string;
  title: string;
  language: string;
  description: string;
  referenceUrl: string;
  requestedByEmail: string;
  status: string;
  createdAt: string;
}

export default function AdminPage() {
  const { user, loading, getFreshToken } = useAuth();
  const router = useRouter();
  
  const [activeTab, setActiveTab] = useState<'cli' | 'requests'>('requests');
  
  // Pending requests state
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([]);
  const [loadingRequests, setLoadingRequests] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Protect Admin Route
  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
      } else if (user.uid !== process.env.NEXT_PUBLIC_ADMIN_UID) {
        router.push('/');
      }
    }
  }, [user, loading, router]);

  const fetchPendingRequests = async () => {
    setLoadingRequests(true);
    try {
      const token = await getFreshToken();
      const baseUrl = process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL !== "undefined" ? process.env.NEXT_PUBLIC_API_URL : "https://sanatanagpt-api-gqx2jph6nq-uc.a.run.app";
      const res = await fetch(`${baseUrl}/api/requests/all`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setPendingRequests(data.requests || []);
    } catch (e) {
      console.error("Failed to fetch requests", e);
    } finally {
      setLoadingRequests(false);
    }
  };

  // Fetch pending requests when tab is active
  useEffect(() => {
    if (activeTab === 'requests' && user) {
      fetchPendingRequests();
    }
  }, [activeTab, user]);

  if (loading || !user || user.uid !== process.env.NEXT_PUBLIC_ADMIN_UID) {
    return <div className="flex h-screen items-center justify-center"><Loader2 className="animate-spin text-orange-500" /></div>;
  }

  const handleReject = async (requestId: string) => {
    setActionLoading(requestId);
    try {
      const token = await getFreshToken();
      const baseUrl = process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL !== "undefined" ? process.env.NEXT_PUBLIC_API_URL : "https://sanatanagpt-api-gqx2jph6nq-uc.a.run.app";
      await fetch(`${baseUrl}/api/requests/${requestId}/reject`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setPendingRequests(prev => prev.filter(r => r.id !== requestId));
    } catch (e) {
      console.error("Failed to reject", e);
    } finally {
      setActionLoading(null);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">🛡️ Admin Panel</h1>
          <button onClick={() => router.push('/')} className="text-sm text-gray-500 hover:text-gray-700">
            ← Back to Chat
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Tab Navigation */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl mb-8 max-w-md">
          <button
            onClick={() => setActiveTab('requests')}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all relative ${
              activeTab === 'requests'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📋 Pending Requests
            {pendingRequests.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-orange-600 text-white text-xs rounded-full flex items-center justify-center">
                {pendingRequests.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('cli')}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'cli'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🖥️ CLI Guide
          </button>
        </div>

        {/* CLI Guide Tab */}
        {activeTab === 'cli' && (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
                <Terminal size={20} className="text-green-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Scripture Ingestion</h2>
                <p className="text-gray-500 text-sm">Managed via local CLI tool</p>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-amber-800">
                <strong>Note:</strong> Scripture uploads are handled via the local admin CLI tool.
                This keeps the backend lightweight and avoids API rate limits during large file ingestion.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">📥 Ingest a new scripture</h3>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <code>python admin/ingest.py --file &quot;path/to/file.pdf&quot; --title &quot;Bhagavad Gita&quot; --language &quot;Sanskrit&quot;</code>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">✅ Approve a user request</h3>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <code>python admin/ingest.py --approve &lt;request_id&gt;</code>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">🗑️ Wipe all chunks &amp; re-ingest</h3>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <code>python admin/ingest.py --wipe</code>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pending Requests Tab */}
        {activeTab === 'requests' && (
          <div className="space-y-4">
            {loadingRequests && (
              <div className="space-y-3">
                {[1,2,3].map(i => <div key={i} className="skeleton h-24 rounded-xl" />)}
              </div>
            )}

            {!loadingRequests && pendingRequests.length === 0 && (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <CheckCircle2 size={40} className="mx-auto text-green-400 mb-3" />
                <h3 className="font-medium text-gray-700">All caught up!</h3>
                <p className="text-sm text-gray-400 mt-1">No pending scripture requests.</p>
              </div>
            )}

            {pendingRequests.map(req => (
              <div key={req.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{req.title}</h3>
                      <span className="badge-pending">Pending</span>
                    </div>
                    {req.language && <p className="text-sm text-orange-600 font-medium">{req.language}</p>}
                    {req.description && <p className="text-sm text-gray-500 mt-1">{req.description}</p>}
                    {req.referenceUrl && (
                      <a href={req.referenceUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline mt-1">
                        <ExternalLink size={12} /> Reference Link
                      </a>
                    )}
                    <p className="text-xs text-gray-400 mt-2">Requested by: {req.requestedByEmail || 'Unknown'}</p>
                    
                    {/* Request ID with copy button */}
                    <div className="flex items-center gap-2 mt-2 bg-gray-50 rounded-lg px-3 py-2 max-w-md">
                      <span className="text-xs text-gray-500 font-mono truncate">{req.id}</span>
                      <button
                        onClick={() => copyToClipboard(req.id)}
                        className="shrink-0 p-1 hover:bg-gray-200 rounded transition-colors"
                        title="Copy Request ID"
                      >
                        {copiedId === req.id ? (
                          <Check size={14} className="text-green-600" />
                        ) : (
                          <Copy size={14} className="text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleReject(req.id)}
                      disabled={actionLoading === req.id}
                      className="flex items-center gap-1 px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 disabled:opacity-50 transition-colors"
                    >
                      {actionLoading === req.id ? <Loader2 size={14} className="animate-spin" /> : <XCircle size={14} />}
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
