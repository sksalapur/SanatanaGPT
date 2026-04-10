"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, MessageSquare, Plus, Menu, X, Loader2, BookOpen, Shield, Pencil, Trash, Check } from 'lucide-react';
import { useRouter, useParams, usePathname } from 'next/navigation';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';
import { db } from '../firebase';
import Link from 'next/link';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  isMobile: boolean;
}

export default function Sidebar({ isOpen, onToggle, isMobile }: SidebarProps) {
  const { user, idToken, signOut, getFreshToken } = useAuth();
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  
  const router = useRouter();
  const params = useParams();
  const pathname = usePathname();

  useEffect(() => {
    if (!user) return;
    
    setLoading(true);
    const q = query(
      collection(db, "users", user.uid, "conversations"),
      orderBy("updatedAt", "desc")
    );
    
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const convs = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setConversations(convs);
      setLoading(false);
    });
    
    return () => unsubscribe();
  }, [user]);

  const handleNewChat = async () => {
    const token = await getFreshToken();
    if (!token) return;
    setCreating(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/conversations`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.convId) {
        router.push(`/chat/${data.convId}`);
        if (isMobile) onToggle();
      }
    } catch (error) {
      console.error("Error creating conversation", error);
    } finally {
      setCreating(false);
    }
  };

  const handleNavClick = (path: string) => {
    router.push(path);
    if (isMobile) onToggle();
  };

  const handleRename = async (convId: string) => {
    if (!editTitle.trim()) return;
    try {
      const token = await getFreshToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/conversations/${convId}/rename`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: editTitle.trim() })
      });
      if (res.ok) {
        setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: editTitle.trim() } : c));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setEditingId(null);
    }
  };

  const handleDelete = async (convId: string) => {
    // Optimistically remove immediately
    const previousConvs = conversations;
    setConversations(prev => prev.filter(c => c.id !== convId));
    setDeletingId(null);
    
    if (params?.id === convId) {
      router.push('/');
    }

    try {
      const token = await getFreshToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/conversations/${convId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        // Restore on failure
        setConversations(previousConvs);
      }
    } catch (e) {
      console.error(e);
      // Restore on error
      setConversations(previousConvs);
    }
  };

  const isAdmin = user?.uid === process.env.NEXT_PUBLIC_ADMIN_UID;

  return (
    <>
      {/* Mobile backdrop */}
      {isMobile && isOpen && (
        <div className="fixed inset-0 backdrop-dim z-40" onClick={onToggle} />
      )}

      <div className={`
        flex flex-col h-screen bg-[#1a1a2e] text-white transition-transform duration-300 ease-in-out
        ${isMobile ? 'fixed left-0 top-0 z-50 w-72' : 'w-64 shrink-0'}
        ${isMobile && !isOpen ? '-translate-x-full' : 'translate-x-0'}
        border-r border-white/10
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 h-16">
          <span className="font-bold text-lg text-orange-400 truncate">🕉️ SanatanaGPT</span>
          <button onClick={onToggle} className="p-1.5 hover:bg-white/10 rounded-lg text-gray-400 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* New Chat */}
        <div className="p-3">
          <button 
            onClick={handleNewChat}
            disabled={creating}
            className="flex items-center justify-center gap-2 w-full bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white p-2.5 rounded-lg transition-colors font-medium text-sm" 
          >
            {creating ? <Loader2 size={18} className="animate-spin" /> : <Plus size={18} />}
            <span>New Chat</span>
          </button>
        </div>

        {/* Navigation Links */}
        <div className="px-3 space-y-1">
          <button
            onClick={() => handleNavClick('/scriptures')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-lg text-sm transition-colors ${
              pathname === '/scriptures' ? 'bg-white/15 text-white' : 'text-gray-400 hover:bg-white/10 hover:text-gray-200'
            }`}
          >
            <BookOpen size={16} />
            <span>Scripture Library</span>
          </button>
          {isAdmin && (
            <button
              onClick={() => handleNavClick('/admin')}
              className={`flex items-center gap-3 w-full p-2.5 rounded-lg text-sm transition-colors ${
                pathname === '/admin' ? 'bg-white/15 text-white' : 'text-gray-400 hover:bg-white/10 hover:text-gray-200'
              }`}
            >
              <Shield size={16} />
              <span>Admin Panel</span>
            </button>
          )}
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto w-full p-2 custom-scroll mt-2">
          <div className="text-xs font-semibold text-gray-500 mb-2 px-2 uppercase tracking-wider">Conversations</div>
          
          {/* Loading Skeletons */}
          {loading && (
            <div className="space-y-2 px-2">
              {[1,2,3,4,5].map(i => (
                <div key={i} className="skeleton-dark h-9 rounded-lg" style={{ width: `${85 - i * 8}%` }} />
              ))}
            </div>
          )}

          {!loading && conversations.length === 0 && (
            <p className="text-xs text-gray-600 px-2 py-4">No conversations yet. Start a new chat!</p>
          )}

          <ul className="space-y-0.5 pb-4">
            {conversations.map(conv => {
              const isEditing = editingId === conv.id;
              const isDeleting = deletingId === conv.id;
              
              if (isDeleting) {
                return (
                  <li key={conv.id} className="flex flex-col gap-2 p-2.5 rounded-lg bg-red-900/20 border border-red-500/30 text-sm">
                    <span className="text-red-200 text-xs">Delete this chat? This cannot be undone.</span>
                    <div className="flex gap-2 text-xs font-medium">
                      <button onClick={(e) => { e.stopPropagation(); handleDelete(conv.id); }} className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
                      <button onClick={(e) => { e.stopPropagation(); setDeletingId(null); }} className="px-2 py-1 bg-transparent text-gray-300 hover:text-white rounded">Cancel</button>
                    </div>
                  </li>
                );
              }
              
              if (isEditing) {
                return (
                  <li key={conv.id} className="flex items-center gap-2 p-1.5 rounded-lg bg-white/10 text-sm">
                    <input 
                      autoFocus
                      type="text"
                      className="bg-transparent text-white w-full outline-none px-1 text-sm"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRename(conv.id);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      onBlur={() => handleRename(conv.id)}
                    />
                    <button 
                      onMouseDown={(e) => e.preventDefault()} 
                      disabled={!editTitle.trim()}
                      className="text-orange-400 hover:text-orange-300 disabled:opacity-50 p-1 shrink-0"
                    >
                      <Check size={14} />
                    </button>
                  </li>
                );
              }

              return (
                <li 
                  key={conv.id}
                  onClick={() => handleNavClick(`/chat/${conv.id}`)}
                  className={`group flex items-center justify-between p-2.5 rounded-lg hover:bg-white/10 cursor-pointer text-sm transition-colors ${
                    params?.id === conv.id ? 'bg-white/15 text-white' : 'text-gray-400'
                  }`} 
                  title={conv.title}
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <MessageSquare size={14} className="shrink-0 opacity-60" />
                    <span className="truncate">{conv.title}</span>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={(e) => { e.stopPropagation(); setEditingId(conv.id); setEditTitle(conv.title); }}
                      className="p-1 hover:text-white hover:bg-white/10 rounded"
                    >
                      <Pencil size={14} />
                    </button>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setDeletingId(conv.id); }}
                      className="p-1 hover:text-red-400 hover:bg-red-500/10 rounded"
                    >
                      <Trash size={14} />
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        {/* User Footer */}
        <div className="p-4 border-t border-white/10 flex items-center justify-between text-sm shrink-0 h-16">
          <div className="flex items-center gap-3 truncate">
            {user?.photoURL ? (
              <img src={user.photoURL} alt="" className="w-8 h-8 rounded-full shrink-0" />
            ) : (
              <div className="w-8 h-8 rounded-full bg-orange-600 flex items-center justify-center shrink-0 text-xs font-bold">
                {user?.displayName?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </div>
            )}
            <span className="truncate text-gray-300 text-sm">{user?.displayName || user?.email?.split('@')[0]}</span>
          </div>
          <button 
            onClick={signOut} 
            className="text-gray-500 hover:text-white p-2 hover:bg-white/10 rounded-lg transition-colors shrink-0" 
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </>
  );
}
