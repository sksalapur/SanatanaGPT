"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { db } from '../../../firebase';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';
import { Loader2, Send, AlertCircle, BookOpen, AlertTriangle, Download } from 'lucide-react';
import ChatLayout from '../../../components/ChatLayout';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Source {
  type: 'scripture';
  title: string;
  scriptureId: string;
  chunkIndex: number;
  snippet: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  has_scripture_match?: boolean;
}

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const { user, getFreshToken } = useAuth();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) return;
    
    const q = query(
      collection(db, "users", user.uid, "conversations", id, "messages"),
      orderBy("timestamp", "asc")
    );
    
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const msgs = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as Message[];
      setMessages(msgs);
      setLoading(false);
      autoScroll();
    }, (error) => {
      console.error("Error fetching messages", error);
      setLoading(false);
    });
    
    return () => unsubscribe();
  }, [user, id]);

  const autoScroll = () => {
    setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    }, 100);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;
    
    const messageContent = input.trim();
    setInput("");
    setSending(true);
    setError(null);

    // Optimistically show user message immediately
    const optimisticMsg: Message = {
      id: `optimistic-${Date.now()}`,
      role: 'user',
      content: messageContent,
    };
    setMessages(prev => [...prev, optimisticMsg]);
    autoScroll();
    
    try {
      const token = await getFreshToken();
      if (!token) throw new Error("Please sign in to send messages.");

      const baseUrl = process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL !== "undefined" ? process.env.NEXT_PUBLIC_API_URL : "https://sanatanagpt-api-gqx2jph6nq-uc.a.run.app";
      const response = await fetch(`${baseUrl}/api/chat/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: messageContent })
      });

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch(e) {}
        if (response.status === 401) {
          throw new Error("Your session has expired. Please sign out and sign in again.");
        }
        throw new Error(errorData?.detail || errorData?.error || `Server error (${response.status})`);
      }

      await response.json();
      
    } catch (error: any) {
      console.error("Chat Error:", error);
      setError(error.message || "Failed to reach the AI server. Please ensure the backend is running.");
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    const prefill = new URLSearchParams(window.location.search).get('q');
    if (prefill) setInput(prefill);
  }, []);

  if (loading) {
    return (
      <ChatLayout>
        <div className="flex-1 flex flex-col w-full max-w-4xl mx-auto p-4 md:p-8 space-y-4">
          {[1,2,3].map(i => (
            <div key={i} className={`flex ${i % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
              <div className="skeleton h-16 rounded-2xl" style={{ width: `${50 + i * 10}%` }} />
            </div>
          ))}
        </div>
      </ChatLayout>
    );
  }

  return (
    <ChatLayout>
      <div className="flex flex-col flex-1 h-full max-w-4xl mx-auto w-full">
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 custom-scroll-light"
        >
          {messages.length === 0 && !sending ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 text-gray-500">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">🕉️</span>
              </div>
              <h2 className="text-xl font-medium text-gray-800">Your conversation is empty</h2>
              <p className="max-w-md text-gray-500">Ask about Dharma, the Vedas, the Bhagavad Gita, or any aspect of Hindu philosophy.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div 
                key={msg.id} 
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} gap-2`}
              >
                {/* Message bubble */}
                <div 
                  className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user' 
                      ? 'bg-orange-600 text-white rounded-tr-sm' 
                      : 'bg-white border border-gray-200 text-gray-800 shadow-sm rounded-tl-sm'
                  }`}
                >
                  <div className={`text-[15px] ${msg.role === 'user' ? 'whitespace-pre-wrap' : 'prose prose-sm max-w-none prose-orange'}`}>
                    {msg.role === 'user' ? (
                      msg.content
                    ) : (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    )}
                  </div>
                </div>

                {/* Sources + warning panel — assistant only, hide when AI errored */}
                {msg.role === 'assistant' && !msg.content.startsWith('[AI Error]') && (
                  <div className="max-w-[85%] md:max-w-[75%] w-full space-y-2">

                    {/* Yellow warning: answer not from scripture */}
                    {msg.has_scripture_match === false && (
                      <div className="flex items-start gap-2 bg-yellow-50 border border-yellow-200 rounded-xl px-3 py-2.5">
                        <AlertTriangle size={14} className="text-yellow-600 mt-0.5 shrink-0" />
                        <p className="text-xs text-yellow-800 leading-relaxed">
                          <span className="font-semibold">Not found in scripture library.</span>{' '}
                          This answer is based on general AI knowledge, not from the scriptures added to SanatanaGPT. Always verify with authentic sources.
                        </p>
                      </div>
                    )}

                    {/* Scripture sources list — only show when there IS a scripture match */}
                    {msg.has_scripture_match === true && msg.sources && msg.sources.length > 0 && (
                      <div className="bg-orange-50/70 border border-orange-100 rounded-xl px-3 py-2.5">
                        <p className="text-[11px] font-semibold text-orange-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                          <BookOpen size={11} /> Referenced from scriptures
                        </p>
                        <div className="divide-y divide-orange-100">
                          {msg.sources.map((src, i) => (
                            <div key={i} className="flex items-start justify-between gap-3 py-1.5 group first:pt-0 last:pb-0">
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-semibold text-orange-900">
                                  📖 {src.title}
                                </p>
                                <p className="text-[11px] text-gray-500 line-clamp-2 mt-0.5 leading-relaxed">
                                  {src.snippet}
                                </p>
                              </div>
                              {src.scriptureId ? (
                                <a
                                  href={`/api/scriptures/${src.scriptureId}/download?filename=${encodeURIComponent((src.title || "Scripture").replace(/[^a-zA-Z0-9 ]/g, "").trim())}.pdf`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="shrink-0 flex items-center gap-1 text-[11px] font-medium text-orange-600 hover:text-orange-800 hover:underline opacity-0 group-hover:opacity-100 transition-opacity mt-0.5"
                                  title="Download PDF"
                                >
                                  <Download size={11} /> Download PDF
                                </a>
                              ) : (
                                <span className="shrink-0 flex items-center gap-1 text-[11px] font-medium text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity mt-0.5" title="Not available for legacy messages">
                                  <Download size={11} /> Unavailable
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
          
          {/* Sending indicator */}
          {sending && (
            <div className="flex justify-start">
               <div className="bg-white border border-gray-200 text-gray-800 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3 max-w-[75%] flex items-center gap-2">
                  <Loader2 size={18} className="animate-spin text-orange-400" />
                  <span className="text-sm text-gray-500">Consulting the scriptures...</span>
               </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="flex justify-center">
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 max-w-md flex items-start gap-3 text-sm">
                <AlertCircle size={18} className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium">Something went wrong</p>
                  <p className="text-red-600 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-3 md:p-4 bg-white/80 backdrop-blur-sm border-t border-gray-200">
          <form onSubmit={handleSend} className="relative flex items-center max-w-3xl mx-auto">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Hindu scriptures..."
              className="w-full pl-5 pr-14 py-3.5 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent shadow-sm bg-white text-[15px]"
              disabled={sending}
            />
            <button 
              type="submit"
              disabled={!input.trim() || sending}
              className="absolute right-2 p-2.5 bg-orange-600 text-white rounded-full hover:bg-orange-700 disabled:bg-gray-300 transition-colors"
            >
              {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-2">
            SanatanaGPT can make mistakes. Always verify scriptural references.
          </p>
        </div>
      </div>
    </ChatLayout>
  );
}
