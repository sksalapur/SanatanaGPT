"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { BookOpen, Search, Filter, Plus, X, Loader2, CheckCircle2, Send, LogIn, Trash, Download, Edit2, Save } from 'lucide-react';
import Link from 'next/link';

interface Scripture {
  id: string;
  title: string;
  language: string;
  author?: string;
  description: string;
  vectorized: boolean;
  addedAt: string;
  storagePath?: string;
}

export default function ScripturesPage() {
  const { user, idToken, getFreshToken, signInWithGoogle } = useAuth();
  
  const [scriptures, setScriptures] = useState<Scripture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [deletingId, setDeletingId] = useState<string | null>(null);
  
  // Editing state
  const [editingScripture, setEditingScripture] = useState<Scripture | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editLanguage, setEditLanguage] = useState("");
  const [editAuthor, setEditAuthor] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);

  const isAdmin = user?.uid === process.env.NEXT_PUBLIC_ADMIN_UID;
  
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [languageFilter, setLanguageFilter] = useState("All");
  
  // Request modal
  const [showModal, setShowModal] = useState(false);
  const [showSignInPrompt, setShowSignInPrompt] = useState(false);
  const [reqTitle, setReqTitle] = useState("");
  const [reqLanguage, setReqLanguage] = useState("");
  const [reqDescription, setReqDescription] = useState("");
  const [reqUrl, setReqUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitMsg, setSubmitMsg] = useState("");

  useEffect(() => {
    fetchScriptures();
  }, []);

  const fetchScriptures = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/scriptures/`);
      const data = await res.json();
      setScriptures(data.scriptures || []);
    } catch (e) {
      setError("Failed to load scriptures. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteScripture = async (scriptureId: string) => {
    try {
      const token = await getFreshToken();
      if (!token) throw new Error("Not authenticated");
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/scriptures/${scriptureId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Delete failed (${res.status})`);
      }
      
      // Optimistic removal
      setScriptures(prev => prev.filter(s => s.id !== scriptureId));
    } catch (e: any) {
      console.error("Delete Error:", e);
      alert(e.message || "Could not delete scripture.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleEditClick = (scripture: Scripture) => {
    setEditingScripture(scripture);
    setEditTitle(scripture.title);
    setEditLanguage(scripture.language);
    setEditAuthor(scripture.author || "");
    setEditDescription(scripture.description || "");
  };

  const handleSaveScripture = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingScripture || !editTitle.trim() || !editLanguage.trim()) return;

    setSavingEdit(true);
    try {
      const token = await getFreshToken();
      if (!token) throw new Error("Not authenticated");

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/scriptures/${editingScripture.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: editTitle,
          language: editLanguage,
          author: editAuthor,
          description: editDescription
        })
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Update failed");
      }

      setScriptures(prev => prev.map(s => 
        s.id === editingScripture.id ? { ...s, title: editTitle, language: editLanguage, author: editAuthor, description: editDescription } : s
      ));
      setEditingScripture(null);
    } catch (e: any) {
      alert(e.message || "Could not update scripture.");
    } finally {
      setSavingEdit(false);
    }
  };

  // Derive unique languages for filter dropdown
  const languages = useMemo(() => {
    const langs = new Set(scriptures.map(s => s.language).filter(Boolean));
    return ["All", ...Array.from(langs)];
  }, [scriptures]);

  // Filtered scriptures
  const filtered = useMemo(() => {
    return scriptures.filter(s => {
      const matchesSearch = s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            s.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesLang = languageFilter === "All" || s.language === languageFilter;
      return matchesSearch && matchesLang;
    });
  }, [scriptures, searchQuery, languageFilter]);

  const handleRequestClick = () => {
    if (!user) {
      setShowSignInPrompt(true);
      return;
    }
    setShowModal(true);
  };

  const handleSubmitRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reqTitle.trim()) return;
    
    setSubmitting(true);
    setSubmitMsg("");
    
    try {
      const token = await getFreshToken();
      if (!token) throw new Error("Not authenticated");

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/requests/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: reqTitle,
          language: reqLanguage,
          description: reqDescription,
          referenceUrl: reqUrl
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to submit request");
      }

      setSubmitMsg("Request submitted successfully!");
      // Only reset form on success
      setReqTitle("");
      setReqLanguage("");
      setReqDescription("");
      setReqUrl("");
      setTimeout(() => {
        setShowModal(false);
        setSubmitMsg("");
      }, 1500);
    } catch (err: any) {
      setSubmitMsg(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-xl font-bold text-orange-600">🕉️ SanatanaGPT</span>
            </Link>
            <span className="text-gray-300 hidden sm:inline">|</span>
            <h1 className="text-lg font-semibold text-gray-800 hidden sm:inline">Scripture Library</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleRequestClick}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium"
            >
              <Plus size={16} />
              <span className="hidden sm:inline">Request a Scripture</span>
              <span className="sm:hidden">Request</span>
            </button>
            <Link
              href="/"
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Back to Chat
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search & Filter Bar */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search scriptures by title or description..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-sm"
            />
          </div>
          <div className="relative">
            <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <select
              value={languageFilter}
              onChange={e => setLanguageFilter(e.target.value)}
              className="pl-9 pr-8 py-2.5 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 appearance-none cursor-pointer"
            >
              {languages.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="skeleton h-44 rounded-xl" />
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-center">
            {error}
          </div>
        )}

        {/* Empty */}
        {!loading && !error && filtered.length === 0 && (
          <div className="text-center py-16 space-y-4">
            <BookOpen size={48} className="mx-auto text-gray-300" />
            <h3 className="text-lg font-medium text-gray-600">
              {scriptures.length === 0 ? "No scriptures uploaded yet" : "No scriptures match your search"}
            </h3>
            <p className="text-gray-400 text-sm">
              {scriptures.length === 0 
                ? "The admin can upload scriptures from the admin panel." 
                : "Try a different search term or language filter."}
            </p>
          </div>
        )}

        {/* Scripture Grid */}
        {!loading && filtered.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map(scripture => {
              const filename = scripture.storagePath?.split('/').pop();
              const isDeleting = deletingId === scripture.id;
              
              if (isDeleting) {
                return (
                  <div key={scripture.id} className="bg-red-50 rounded-xl border border-red-200 p-6 flex flex-col items-center justify-center text-center space-y-4">
                    <Trash className="text-red-400" size={32} />
                    <div>
                      <h3 className="font-medium text-red-800">Delete this scripture?</h3>
                      <p className="text-xs text-red-600 mt-1 px-4">This will permanently delete the text, all vectorized chunks, and the PDF file from storage.</p>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => handleDeleteScripture(scripture.id)} className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700">Delete</button>
                      <button onClick={() => setDeletingId(null)} className="px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancel</button>
                    </div>
                  </div>
                );
              }
              
              return (
                <div
                  key={scripture.id}
                  className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-orange-200 transition-all duration-200 group flex flex-col h-full"
                >
                  <div className="flex items-start justify-between mb-3 flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 shrink-0 rounded-lg bg-orange-100 flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                        <BookOpen size={20} className="text-orange-600" />
                      </div>
                      {filename && (
                        <span className="text-xs text-gray-500 font-mono mt-1 hidden group-hover:block transition-all truncate max-w-[100px] sm:max-w-[120px]">
                          {filename}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center justify-end gap-1 flex-1 min-w-[140px]">
                      {scripture.vectorized && (
                        <span className="badge-success hidden sm:inline-flex">
                          <CheckCircle2 size={12} />
                          Vectorized
                        </span>
                      )}
                      <a 
                        href={`/api/scriptures/${scripture.id}/download?filename=${encodeURIComponent((scripture.title || "Scripture").replace(/[^a-zA-Z0-9 ]/g, "").trim())}.pdf`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded-md transition-colors"
                        title="Download PDF"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Download size={16} />
                      </a>
                      {isAdmin && (
                        <>
                          <button 
                            onClick={(e) => { e.stopPropagation(); handleEditClick(scripture); }}
                            className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                            title="Edit Scripture"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button 
                            onClick={(e) => { e.stopPropagation(); setDeletingId(scripture.id); }}
                            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                            title="Delete Scripture"
                          >
                            <Trash size={16} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg mb-1 group-hover:text-orange-700 transition-colors leading-tight">
                    {scripture.title}
                  </h3>
                  {scripture.author && (
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      By {scripture.author}
                    </p>
                  )}
                  {filename && (
                    <p className="text-[10px] text-gray-400 font-mono mb-2 group-hover:hidden truncate" title={filename}>
                      {filename}
                    </p>
                  )}
                  <p className="text-xs text-orange-600 font-medium mb-2">{scripture.language}</p>
                  {scripture.description && (
                    <p className="text-sm text-gray-500 line-clamp-3 mb-4 flex-1">{scripture.description}</p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Sign-in Prompt Modal */}
      {showSignInPrompt && (
        <div className="fixed inset-0 backdrop-dim z-50 flex items-center justify-center p-4" onClick={() => setShowSignInPrompt(false)}>
          <div className="bg-white rounded-2xl p-8 max-w-sm w-full shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="text-center space-y-4">
              <LogIn size={40} className="mx-auto text-orange-600" />
              <h3 className="text-xl font-bold text-gray-900">Sign in required</h3>
              <p className="text-gray-500 text-sm">You need to be signed in to request a scripture.</p>
              <button
                onClick={() => { signInWithGoogle(); setShowSignInPrompt(false); }}
                className="w-full py-3 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors"
              >
                Sign in with Google
              </button>
              <button
                onClick={() => setShowSignInPrompt(false)}
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Request Modal — form values persist on dismiss, reset only on success */}
      {showModal && (
        <div className="fixed inset-0 backdrop-dim z-50 flex items-center justify-center p-4" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Request a Scripture</h3>
              <button onClick={() => setShowModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X size={20} className="text-gray-400" />
              </button>
            </div>

            <form onSubmit={handleSubmitRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={reqTitle}
                  onChange={e => setReqTitle(e.target.value)}
                  placeholder="e.g. Yoga Sutras of Patanjali"
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                <select
                  value={reqLanguage}
                  onChange={e => setReqLanguage(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Any / Not sure</option>
                  <option>English</option>
                  <option>Sanskrit</option>
                  <option>Hindi</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={reqDescription}
                  onChange={e => setReqDescription(e.target.value)}
                  placeholder="Why would you like this scripture added?"
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL or Reference (optional)</label>
                <input
                  type="text"
                  value={reqUrl}
                  onChange={e => setReqUrl(e.target.value)}
                  placeholder="https://example.com/scripture.pdf"
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              {submitMsg && (
                <div className={`p-3 rounded-lg text-sm ${submitMsg.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                  {submitMsg}
                </div>
              )}

              <button
                type="submit"
                disabled={submitting || !reqTitle.trim()}
                className="w-full py-3 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:bg-gray-300 transition-colors flex items-center justify-center gap-2"
              >
                {submitting ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                {submitting ? 'Submitting...' : 'Submit Request'}
              </button>
            </form>
          </div>
        </div>
      )}
      {/* Edit Modal (Admin Only) */}
      {editingScripture && isAdmin && (
        <div className="fixed inset-0 backdrop-dim z-50 flex items-center justify-center p-4" onClick={() => !savingEdit && setEditingScripture(null)}>
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Edit2 className="text-blue-600" size={24} /> Edit Scripture
              </h3>
              <button 
                onClick={() => setEditingScripture(null)} 
                disabled={savingEdit}
                className="p-1 hover:bg-gray-100 rounded-lg disabled:opacity-50"
              >
                <X size={20} className="text-gray-400" />
              </button>
            </div>

            <form onSubmit={handleSaveScripture} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                  disabled={savingEdit}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Language *</label>
                <input
                  type="text"
                  required
                  value={editLanguage}
                  onChange={e => setEditLanguage(e.target.value)}
                  disabled={savingEdit}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Author</label>
                <input
                  type="text"
                  value={editAuthor}
                  onChange={e => setEditAuthor(e.target.value)}
                  disabled={savingEdit}
                  placeholder="e.g. Sage Vyasa"
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={editDescription}
                  onChange={e => setEditDescription(e.target.value)}
                  disabled={savingEdit}
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={savingEdit || !editTitle.trim() || !editLanguage.trim()}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-400 transition-colors flex items-center justify-center gap-2"
                >
                  {savingEdit ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                  {savingEdit ? 'Updating metadata & vector chunks...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
