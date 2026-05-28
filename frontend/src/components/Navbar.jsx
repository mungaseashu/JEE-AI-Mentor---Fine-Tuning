// ==============================================================================
// JEE MENTOR AI - DARK GLASSMORPHIC HEADER & NAVIGATION BAR
// ==============================================================================
import React from 'react';
import { LogOut, GraduationCap, Flame, User as UserIcon, LayoutDashboard, MessageSquare, Cpu, ClipboardCheck, BarChart3 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onLogout }) {
  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', name: 'AI Chat Tutor', icon: MessageSquare },
    { id: 'solver', name: 'Focus Solver', icon: Cpu },
    { id: 'test', name: 'Practice Exam', icon: ClipboardCheck },
    { id: 'analytics', name: 'Mastery', icon: BarChart3 }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-dark-border bg-dark-bg/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Title Logo */}
        <div className="flex items-center space-x-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-primary to-brand-secondary shadow-neon-purple">
            <GraduationCap className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent hidden sm:block">
            JEE Mentor <span className="text-brand-primary">AI</span>
          </span>
        </div>

        {/* Nav Tabs */}
        <nav className="flex space-x-1 md:space-x-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs md:text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? 'bg-brand-primary/10 text-brand-primary border-b-2 border-brand-primary shadow-neon-purple/5'
                    : 'text-gray-400 hover:text-white hover:bg-dark-border/40'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden md:inline">{tab.name}</span>
              </button>
            );
          })}
        </nav>

        {/* Profile & Logout */}
        <div className="flex items-center space-x-4">
          {user && (
            <>
              {/* Daily Streak Flame indicator */}
              <div className="flex items-center space-x-1 px-2.5 py-1 bg-amber-500/10 text-amber-500 border border-amber-500/20 rounded-full cursor-help hover:bg-amber-500/20 transition-all duration-300" title="Daily study streak!">
                <Flame className="h-4 w-4 fill-amber-500 animate-pulse" />
                <span className="text-xs font-semibold">5 Days</span>
              </div>
              
              {/* User Name */}
              <div className="flex items-center space-x-1.5 text-gray-300">
                <UserIcon className="h-4 w-4 text-brand-secondary" />
                <span className="text-xs font-semibold hidden lg:block">{user.username}</span>
              </div>

              {/* Logout Button */}
              <button 
                onClick={onLogout}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-dark-border text-gray-400 hover:text-red-400 hover:bg-red-500/10 hover:border-red-500/20 transition-all duration-200"
                title="Log out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
        
      </div>
    </header>
  );
}
