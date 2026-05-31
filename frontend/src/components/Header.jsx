import React from 'react';
import { Compass } from 'lucide-react';

export default function Header() {
  return (
    <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/20 text-white">
            <Compass className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-400 bg-clip-text text-transparent">
              CareerPilot AI
            </h1>
            <p className="text-xs text-slate-400 hidden sm:block">
              Hệ thống phân tích khoảng cách kỹ năng cho sinh viên IT
            </p>
          </div>
        </div>
        
        <div className="text-xs px-3 py-1.5 rounded-full border border-indigo-500/20 bg-indigo-500/5 text-indigo-300 font-medium">
          Demo Bản MVP Chạy Thật
        </div>
      </div>
    </header>
  );
}
