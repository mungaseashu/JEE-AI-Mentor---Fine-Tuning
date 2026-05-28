// ==============================================================================
// JEE MENTOR AI - MASTERY & PERFORMANCE AREA CHARTS
// ==============================================================================
import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { BarChart3, TrendingUp, BookOpen, CheckCircle, AlertTriangle } from 'lucide-react';

export default function AnalyticsPage() {
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
        console.error("Analytics fetch error: ", err);
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

  // Seeding high-quality time-series analytics (simulating mock progression over 6 days of training)
  const timeSeriesData = [
    { day: 'Day 1', accuracy: 40, average_time: 180 },
    { day: 'Day 2', accuracy: 52, average_time: 155 },
    { day: 'Day 3', accuracy: 58, average_time: 140 },
    { day: 'Day 4', accuracy: 68, average_time: 125 },
    { day: 'Day 5', accuracy: 72, average_time: 110 },
    { day: 'Day 6', accuracy: data?.overall_accuracy ? Math.round(data.overall_accuracy * 100) : 75, average_time: 98 }
  ];

  const subjectData = [
    { subject: 'Physics', score: data?.subjects_proficiency?.Physics * 100 || 50 },
    { subject: 'Chemistry', score: data?.subjects_proficiency?.Chemistry * 100 || 50 },
    { subject: 'Mathematics', score: data?.subjects_proficiency?.Mathematics * 100 || 50 }
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center space-x-2 shrink-0">
        <BarChart3 className="h-6 w-6 text-brand-primary" />
        <h2 className="text-xl font-bold text-white font-sans">Mastery Analytics & Performance Logs</h2>
      </div>

      {/* Section 1: Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Area Chart: Accuracy Time-Series */}
        <div className="rounded-xl border border-dark-border bg-dark-card/40 p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Accuracy Progression Curve</h3>
            <span className="flex items-center space-x-1 text-xs text-brand-primary font-semibold">
              <TrendingUp className="h-4 w-4" />
              <span>Moving Average</span>
            </span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSeriesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="day" stroke="#9CA3AF" fontSize={11} />
                <YAxis stroke="#9CA3AF" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#11131E', borderColor: '#1E2235', color: '#F3F4F6' }} />
                <Area type="monotone" dataKey="accuracy" name="Accuracy %" stroke="#8B5CF6" fillOpacity={1} fill="url(#colorAcc)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart: Subject Comparison */}
        <div className="rounded-xl border border-dark-border bg-dark-card/40 p-6 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Subject-wise Mastery Ratios</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={subjectData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="subject" stroke="#9CA3AF" fontSize={11} />
                <YAxis stroke="#9CA3AF" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#11131E', borderColor: '#1E2235', color: '#F3F4F6' }} />
                <Bar dataKey="score" name="Mastery %" fill="#06B6D4" radius={[6, 6, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Section 2: Flagged Weak Topics Checklist */}
      <div className="rounded-xl border border-dark-border bg-dark-card/40 p-6 space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Granular Chapter Proficiency Table</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-dark-border text-gray-400 font-semibold uppercase tracking-wider bg-dark-bg/25">
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4">Topic / Chapter</th>
                <th className="py-3 px-4">Questions Solved</th>
                <th className="py-3 px-4">Running Mastery</th>
                <th className="py-3 px-4 text-right">Target Strategy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border/40 text-gray-300">
              {(!data?.weak_topics || data.weak_topics.length === 0) ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-dark-muted">
                    No active topic history records found. Perform CBT quizzes to populate proficiency charts.
                  </td>
                </tr>
              ) : (
                data.weak_topics.map((t, idx) => (
                  <tr key={idx} className="hover:bg-dark-card/25 transition-all">
                    <td className="py-3 px-4 font-bold text-white">{t.subject}</td>
                    <td className="py-3 px-4">{t.topic}</td>
                    <td className="py-3 px-4 font-mono">{t.questions_attempted} attempts</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-1.5 bg-dark-border rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${t.accuracy >= 0.7 ? 'bg-brand-success' : t.accuracy >= 0.5 ? 'bg-brand-warning' : 'bg-brand-accent'}`}
                            style={{ width: `${t.accuracy * 100}%` }}
                          />
                        </div>
                        <span className="font-semibold text-white font-mono">{(t.accuracy * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[9px] font-bold ${t.accuracy < 0.5 ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-brand-warning/10 text-brand-warning border border-brand-warning/20'}`}>
                        {t.accuracy < 0.5 ? 'REINFORCE CORE' : 'PRACTICE HARD'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
