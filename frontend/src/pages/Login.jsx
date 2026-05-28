// ==============================================================================
// JEE MENTOR AI - PREMIER AUTHENTICATION PAGE (Login & Registration)
// ==============================================================================
import React, { useState } from 'react';
import { GraduationCap, Mail, Lock, User as UserIcon, LogIn, Sparkles } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const API_URL = 'http://localhost:8000';

    try {
      if (isRegister) {
        // Register API flow
        const response = await fetch(`${API_URL}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, username, password, full_name: fullName })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Registration failed');
        }
        
        // Auto-login after registration
        setIsRegister(false);
        setPassword('');
        setError('Registration successful! Please login with your new credentials.');
      } else {
        // Login API flow
        const response = await fetch(`${API_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Incorrect credentials');
        }
        
        // Save access token
        localStorage.setItem('token', data.access_token);
        
        // Fetch user data
        const userRes = await fetch(`${API_URL}/analyze`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        
        // Fake a profile fetch since analyze returns user summaries
        onLoginSuccess({
          username: username || email.split('@')[0],
          email: email
        });
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      {/* Neon Ambient Background Orbs */}
      <div className="absolute top-1/4 left-1/4 h-72 w-72 rounded-full bg-brand-primary/20 blur-[100px] animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-brand-secondary/20 blur-[100px] animate-pulse delay-700"></div>

      <div className="w-full max-w-md rounded-2xl border border-dark-border bg-dark-card/60 p-8 shadow-glass backdrop-blur-xl z-10">
        
        {/* Header branding */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-primary to-brand-secondary shadow-neon-purple mb-3">
            <GraduationCap className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            {isRegister ? 'Create Your Account' : 'Welcome to JEE Mentor AI'}
          </h1>
          <p className="text-xs text-dark-muted mt-1.5 text-center">
            {isRegister 
              ? 'Unlock adaptive practice and RAG-infused tutoring.' 
              : 'Interact with QLoRA fine-tuned ML models trained to solve JEE questions.'}
          </p>
        </div>

        {error && (
          <div className={`mb-6 p-3 rounded-lg border text-xs text-center font-medium ${
            error.includes('successful')
              ? 'bg-brand-success/10 border-brand-success/20 text-brand-success'
              : 'bg-red-500/10 border-red-500/20 text-red-400'
          }`}>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <>
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1.5">Full Name</label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-3 h-4.5 w-4.5 text-dark-muted" />
                  <input
                    type="text"
                    required
                    placeholder="Enter your name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full rounded-lg border border-dark-border bg-dark-bg/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-dark-muted focus:border-brand-primary focus:shadow-neon-purple focus:outline-none transition-all duration-300"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1.5">Username</label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-3 h-4.5 w-4.5 text-dark-muted" />
                  <input
                    type="text"
                    required
                    placeholder="Choose a username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full rounded-lg border border-dark-border bg-dark-bg/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-dark-muted focus:border-brand-primary focus:shadow-neon-purple focus:outline-none transition-all duration-300"
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4.5 w-4.5 text-dark-muted" />
              <input
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-dark-border bg-dark-bg/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-dark-muted focus:border-brand-primary focus:shadow-neon-purple focus:outline-none transition-all duration-300"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4.5 w-4.5 text-dark-muted" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-dark-border bg-dark-bg/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-dark-muted focus:border-brand-primary focus:shadow-neon-purple focus:outline-none transition-all duration-300"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-brand-primary to-brand-secondary py-2.5 text-sm font-semibold text-white shadow-neon-purple hover:opacity-95 focus:outline-none transition-all duration-300 disabled:opacity-50"
          >
            {loading ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <>
                {isRegister ? <Sparkles className="h-4 w-4" /> : <LogIn className="h-4 w-4" />}
                <span>{isRegister ? 'Sign Up' : 'Sign In'}</span>
              </>
            )}
          </button>
        </form>

        {/* Toggle button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-xs font-medium text-brand-secondary hover:text-brand-secondary/80 focus:outline-none"
          >
            {isRegister 
              ? 'Already registered? Sign in here' 
              : "Don't have an account? Sign up here"}
          </button>
        </div>

      </div>
    </div>
  );
}
