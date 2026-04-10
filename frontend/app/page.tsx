"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import ChatLayout from "../components/ChatLayout";
import { Sparkles } from 'lucide-react';

const TOPIC_CHIPS = [
  { label: "🕉️ Bhagavad Gita", query: "Tell me about the key teachings of the Bhagavad Gita" },
  { label: "📜 Vedas", query: "What are the four Vedas and their significance?" },
  { label: "🧘 Upanishads", query: "Explain the core philosophy of the Upanishads" },
  { label: "⚖️ Dharma", query: "What is Dharma according to Hindu philosophy?" },
  { label: "🔄 Karma", query: "Explain the concept of Karma in Hinduism" },
  { label: "🪷 Moksha", query: "What is Moksha and how does one attain it?" },
];

export default function Home() {
  const router = useRouter();
  const { idToken, getFreshToken } = useAuth();

  const handleChipClick = async (queryText: string) => {
    // Create a new conversation, then navigate with query pre-filled
    const token = await getFreshToken();
    if (!token) return;
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/conversations`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.convId) {
        router.push(`/chat/${data.convId}?q=${encodeURIComponent(queryText)}`);
      }
    } catch (error) {
      console.error("Error creating conversation", error);
    }
  };

  return (
    <ChatLayout>
      <div className="flex-1 flex flex-col items-center justify-center w-full px-4">
        <div className="max-w-2xl text-center space-y-8">
          {/* Hero icon */}
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
              <Sparkles size={36} className="text-white" />
            </div>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
              Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-amber-500">SanatanaGPT</span>
            </h1>
            <p className="text-lg text-gray-500 max-w-lg mx-auto">
              Ask anything about the Vedas, Upanishads, Gita, Dharma, Karma, and the rich traditions of Hindu philosophy.
            </p>
          </div>

          {/* Topic chips */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-gray-400 uppercase tracking-wide">Explore a topic</p>
            <div className="flex flex-wrap justify-center gap-2">
              {TOPIC_CHIPS.map(chip => (
                <button
                  key={chip.label}
                  onClick={() => handleChipClick(chip.query)}
                  className="px-4 py-2.5 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700 hover:border-orange-400 hover:text-orange-700 hover:shadow-md hover:shadow-orange-500/10 transition-all duration-200 cursor-pointer"
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </ChatLayout>
  );
}
