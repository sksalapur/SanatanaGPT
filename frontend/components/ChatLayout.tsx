"use client";

import React, { useState, useEffect } from 'react';
import ProtectedRoute from "./ProtectedRoute";
import Sidebar from "./Sidebar";
import { Menu } from 'lucide-react';

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) setSidebarOpen(true);
    };
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-50 overflow-hidden">
        <Sidebar isOpen={sidebarOpen || !isMobile} onToggle={() => setSidebarOpen(!sidebarOpen)} isMobile={isMobile} />
        
        <div className="flex-1 flex flex-col min-w-0">
          {/* Mobile top bar */}
          {isMobile && (
            <div className="flex items-center h-14 px-4 bg-white border-b border-gray-200 shrink-0">
              <button 
                onClick={() => setSidebarOpen(true)} 
                className="p-2 -ml-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu size={20} className="text-gray-700" />
              </button>
              <span className="ml-3 font-bold text-orange-600">SanatanaGPT</span>
            </div>
          )}
          
          <main className="flex-1 flex flex-col items-center overflow-hidden">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
