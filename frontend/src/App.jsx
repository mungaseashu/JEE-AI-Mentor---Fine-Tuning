// ==============================================================================
// JEE MENTOR AI - MASTER APPLICATION RUNTIME CONTROLLER
// ==============================================================================
import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ChatTutor from './pages/ChatTutor';
import QuestionSolver from './pages/QuestionSolver';
import MockTest from './pages/MockTest';
import AnalyticsPage from './pages/AnalyticsPage';

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  // Authenticate token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Mock active session profile for immediate onboarding
      // In production, backend validations occur at api boundaries
      setUser({
        username: 'JEE_Aspirant_2026',
        email: 'student@jeementor.ai'
      });
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setActiveTab('dashboard');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-dark-bg text-brand-primary">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-primary border-t-transparent" />
      </div>
    );
  }

  // Enforce auth
  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-dark-bg text-dark-text font-sans">
      {/* Global Glassmorphic Header */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user} 
        onLogout={handleLogout} 
      />

      {/* Content Main Panel */}
      <main className="flex-1 overflow-x-hidden">
        {activeTab === 'dashboard' && <Dashboard setActiveTab={setActiveTab} />}
        {activeTab === 'chat' && <ChatTutor />}
        {activeTab === 'solver' && <QuestionSolver />}
        {activeTab === 'test' && <MockTest setActiveTab={setActiveTab} />}
        {activeTab === 'analytics' && <AnalyticsPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-border bg-dark-card/25 py-4 text-center shrink-0">
        <p className="text-[10px] text-dark-muted">
          JEE Mentor AI © 2026. Deployment-ready MLOps Architect Project. Powered by QLoRA Base fine-tuned LLM & ChromaDB RAG.
        </p>
      </footer>
    </div>
  );
}
