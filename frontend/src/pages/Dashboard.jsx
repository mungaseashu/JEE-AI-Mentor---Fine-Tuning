// ==============================================================================
// JEE MENTOR AI - INTERACTIVE PERFORMANCE ANALYTICS DASHBOARD
// ==============================================================================
import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { BookOpen, AlertTriangle, CheckCircle2, Flame, Award, ArrowUpRight, TrendingUp } from 'lucide-react';

export default function Dashboard({ setActiveTab }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch('http://localhost:8000/analyze', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Dashboard fetch error: ", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center bg-dark-bg">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-primary border-t-transparent" />
      </div>
    );
  }

  // Seeding default visualization parameters in case history is empty
  const defaultProficiencies = [
    { subject: 'Physics', score: data?.subjects_proficiency?.Physics * 100 || 50 },
    { subject: 'Chemistry', score: data?.subjects_proficiency?.Chemistry * 100 || 50 },
    { subject: 'Mathematics', score: data?.subjects_proficiency?.Mathematics * 100 || 50 }
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      
      {/* Section 1: Hero Banner */}
      <div className="relative rounded-2xl border border-dark-border bg-gradient-to-r from-brand-primary/10 via-dark-card to-brand-secondary/5 p-6 md:p-8 overflow-hidden shadow-glass">
        <div className="absolute top-0 right-0 h-40 w-40 rounded-full bg-brand-primary/10 blur-3xl"></div>
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-brand-primary/10 text-brand-primary border border-brand-primary/20 text-xs font-semibold mb-3">
            <Flame className="h-3.5 w-3.5" />
            <span>Targeting IIT-JEE 2026</span>
          </span>
          <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">Ready to boost your JEE score?</h2>
          <p className="text-sm text-gray-400 mt-2">
            JEE Mentor AI combines QLoRA model reasoning with RAG NCERT context to solve complex problems and tracks your learning gaps in real-time.
          </p>
          <div className="flex space-x-4 mt-6">
            <button onClick={() => setActiveTab('chat')} className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-brand-primary text-sm font-semibold text-white shadow-neon-purple hover:opacity-95 transition-all">
              <span>Ask a Doubt</span>
              <ArrowUpRight className="h-4 w-4" />
            </button>
            <button onClick={() => setActiveTab('test')} className="px-4 py-2 rounded-lg border border-dark-border text-sm font-semibold text-gray-300 hover:bg-dark-border/40 transition-all">
              <span>Take Quiz</span>
            </button>
          </div>
        </div>
      </div>

      {/* Section 2: General Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Card 1: Solved Count */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Total Solved</span>
            <div className="rounded-lg bg-brand-secondary/10 p-2 text-brand-secondary">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-3xl font-bold text-white">{data?.total_solved || 0}</h3>
            <p className="text-xs text-brand-secondary mt-1 flex items-center space-x-0.5">
              <TrendingUp className="h-3 w-3" />
              <span>Running Questions Solved</span>
            </p>
          </div>
        </div>

        {/* Card 2: Overall Accuracy */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Overall Accuracy</span>
            <div className="rounded-lg bg-brand-primary/10 p-2 text-brand-primary">
              <Award className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-3xl font-bold text-white">{(data?.overall_accuracy * 100).toFixed(0) || 0}%</h3>
            <p className="text-xs text-brand-primary mt-1">Average topic accuracy</p>
          </div>
        </div>

        {/* Card 3: Study Streak */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Daily Streak</span>
            <div className="rounded-lg bg-amber-500/10 p-2 text-amber-500">
              <Flame className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-3xl font-bold text-white">5 Days</h3>
            <p className="text-xs text-amber-500 mt-1">Consistent daily progress</p>
          </div>
        </div>

        {/* Card 4: Weak Areas Count */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Flagged Topics</span>
            <div className="rounded-lg bg-brand-accent/10 p-2 text-brand-accent">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-3xl font-bold text-white">{data?.weak_topics?.length || 0}</h3>
            <p className="text-xs text-brand-accent mt-1">Under-performance zones</p>
          </div>
        </div>
      </div>

      {/* Section 3: Charts & Recommendations */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: Radar Chart */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-6 backdrop-blur-md lg:col-span-2 space-y-4">
          <h3 className="text-lg font-bold text-white">Subject Proficiency Index</h3>
          <div className="h-[250px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" radius="80%" data={defaultProficiencies}>
                <PolarGrid stroke="#1F2937" />
                <PolarAngleAxis dataKey="subject" stroke="#9CA3AF" fontSize={12} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#374151" />
                <Radar name="Syllabus Mastery" dataKey="score" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Flagged Weak Topics Checklist */}
        <div className="rounded-xl border border-dark-border bg-dark-card/60 p-6 backdrop-blur-md space-y-4">
          <h3 className="text-lg font-bold text-white">Weak Chapters & Revisions</h3>
          <div className="space-y-4 overflow-y-auto max-h-[250px] pr-1">
            {(!data?.weak_topics || data.weak_topics.length === 0) ? (
              <div className="flex flex-col items-center justify-center text-center p-6 bg-dark-bg/40 rounded-xl border border-dark-border">
                <CheckCircle2 className="h-8 w-8 text-brand-success mb-2" />
                <span className="text-xs font-semibold text-white">Excellent Standing!</span>
                <span className="text-[10px] text-gray-400 mt-1">No weak topics flagged currently. Complete quizzes to populate analytics.</span>
              </div>
            ) : (
              data.weak_topics.map((t, idx) => (
                <div key={idx} className="flex flex-col p-3 rounded-lg border border-brand-accent/20 bg-brand-accent/5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{t.topic}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-brand-accent/15 text-brand-accent font-semibold">
                      {(t.accuracy * 100).toFixed(0)}% Acc
                    </span>
                  </div>
                  <p className="text-[10px] text-gray-300 leading-relaxed italic">
                    {t.recommendation}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

    </div>
  );
}
