// ==============================================================================
// JEE MENTOR AI - FOCUS SOLVER WORKSPACE (Split-Screen Design)
// ==============================================================================
import React, { useState, useRef } from 'react';
import { Cpu, Upload, Image as ImageIcon, Sparkles, Clock, BookOpen, AlertTriangle } from 'lucide-react';
import MathRenderer from '../components/MathRenderer';

export default function QuestionSolver() {
  const [questionText, setQuestionText] = useState('');
  const [subject, setSubject] = useState('Physics');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef(null);

  const handleSolve = async (textParam = null) => {
    const textToSolve = textParam || questionText;
    if (!textToSolve.trim() && !fileInputRef.current?.files?.[0]) return;

    setLoading(true);
    setResult(null);

    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question_text: textToSolve || undefined,
          subject: subject
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Solver failed');
      setResult(data);
    } catch (err) {
      alert(`Solver failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setResult(null);

    try {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onloadend = async () => {
        const base64Str = reader.result;
        
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/solve', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            image_base64: base64Str,
            subject: subject
          })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Solver failed');
        setResult(data);
      };
    } catch (err) {
      alert(`OCR Solver failed: ${err.message}`);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = e.dataTransfer.files;
      // Assign to input file value and fire
      if (fileInputRef.current) {
        fileInputRef.current.files = files;
        handleFileUpload({ target: { files } });
      }
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 h-[calc(100vh-4rem)] flex flex-col space-y-6">
      
      {/* Header */}
      <div className="flex items-center space-x-2 shrink-0">
        <Cpu className="h-6 w-6 text-brand-secondary" />
        <h2 className="text-xl font-bold text-white">Focus Solver Board</h2>
        <span className="text-xs text-dark-muted hidden md:inline">| Step-by-step IIT-JEE equation solver & graph plotter</span>
      </div>

      {/* Main Split Workspace */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
        
        {/* Left: Input Console */}
        <div className="rounded-xl border border-dark-border bg-dark-card/40 p-6 flex flex-col space-y-4 min-h-0">
          <h3 className="text-sm font-bold text-white shrink-0">Problem Editor</h3>
          
          {/* Subject select tabs */}
          <div className="flex space-x-2 shrink-0">
            {['Physics', 'Chemistry', 'Mathematics'].map((s) => (
              <button
                key={s}
                onClick={() => setSubject(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  subject === s
                    ? 'bg-brand-secondary/10 border-brand-secondary text-brand-secondary'
                    : 'border-dark-border text-gray-400 hover:text-white'
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Text Input Area */}
          <textarea
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
            disabled={loading}
            placeholder="Type your question or drop an equation image here (e.g. Find the MOI of compound solid disc)..."
            className="flex-1 min-h-[120px] rounded-lg border border-dark-border bg-dark-bg/60 p-4 text-sm text-white placeholder-dark-muted focus:border-brand-secondary focus:shadow-neon-cyan focus:outline-none resize-none transition-all duration-300"
          />

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 shrink-0 ${
              dragActive 
                ? 'border-brand-secondary bg-brand-secondary/5' 
                : 'border-dark-border bg-dark-bg/30 hover:border-brand-secondary/40'
            }`}
          >
            <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*" />
            <Upload className={`h-8 w-8 text-dark-muted mb-2 ${dragActive ? 'animate-bounce text-brand-secondary' : ''}`} />
            <span className="text-xs font-semibold text-white">Drag & drop question photo</span>
            <span className="text-[10px] text-gray-500 mt-1">Supports PNG, JPG, or JPEG up to 10MB</span>
          </div>

          {/* Solve action button */}
          <button
            onClick={() => handleSolve()}
            disabled={loading || (!questionText.trim() && !fileInputRef.current?.files?.[0])}
            className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-brand-secondary to-brand-primary py-2.5 text-sm font-semibold text-white shadow-neon-cyan hover:opacity-95 transition-all duration-300 disabled:opacity-50 shrink-0"
          >
            {loading ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <>
                <Sparkles className="h-4.5 w-4.5 animate-pulse" />
                <span>Trigger AI Solver Pipeline</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Solution Output */}
        <div className="rounded-xl border border-dark-border bg-dark-card/40 p-6 flex flex-col min-h-0">
          <h3 className="text-sm font-bold text-white mb-4 shrink-0">Step-by-step Solution Board</h3>
          
          <div className="flex-1 overflow-y-auto pr-1 space-y-6">
            {!result ? (
              <div className="flex h-full flex-col items-center justify-center text-center max-w-sm mx-auto space-y-3">
                <ImageIcon className="h-10 w-10 text-dark-muted" />
                <span className="text-xs font-semibold text-white">Waiting for solver parameters</span>
                <span className="text-[10px] text-gray-500 leading-relaxed">
                  Enter your question inside the problem editor or upload a snapshot to watch the AI build a complete reasoning derivation.
                </span>
              </div>
            ) : (
              <div className="space-y-6">
                
                {/* Latency Stats */}
                <div className="flex space-x-4 shrink-0">
                  <div className="flex items-center space-x-1.5 px-3 py-1 bg-brand-primary/10 border border-brand-primary/20 text-brand-primary rounded-full text-[10px] font-bold">
                    <Clock className="h-3.5 w-3.5" />
                    <span>Solved in {result.latency_ms} ms</span>
                  </div>
                  <div className="flex items-center space-x-1.5 px-3 py-1 bg-brand-secondary/10 border border-brand-secondary/20 text-brand-secondary rounded-full text-[10px] font-bold">
                    <BookOpen className="h-3.5 w-3.5" />
                    <span>RAG Knowledge Synced</span>
                  </div>
                </div>

                {/* Extracted OCR */}
                {result.extracted_text && (
                  <div className="p-3 bg-dark-bg/60 border border-dark-border rounded-lg space-y-1">
                    <span className="text-[10px] font-bold text-brand-secondary block uppercase tracking-wider">Extracted OCR Prompt:</span>
                    <p className="text-xs text-gray-300 italic">"{result.extracted_text}"</p>
                  </div>
                )}

                {/* Plotted Graph Image */}
                {result.graph_base64 && (
                  <div className="border border-dark-border rounded-lg overflow-hidden bg-dark-bg p-2 shadow-neon-purple/5">
                    <span className="text-[10px] font-bold text-brand-primary block uppercase tracking-wider mb-2">Matplotlib Neon Function Graph:</span>
                    <img src={result.graph_base64} alt="Neon Plotted Function Chart" className="w-full h-auto rounded" />
                  </div>
                )}

                {/* Solution explanation */}
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-brand-secondary block uppercase tracking-wider">Rigorous Solution:</span>
                  <MathRenderer text={result.solution} />
                </div>

                {/* Formula bank */}
                {result.formulas_used && result.formulas_used.length > 0 && (
                  <div className="p-3 bg-dark-bg/60 border border-dark-border rounded-lg space-y-2">
                    <span className="text-[10px] font-bold text-brand-secondary block uppercase tracking-wider">Consulted Formula Index:</span>
                    {result.formulas_used.map((f, idx) => (
                      <code key={idx} className="text-[10px] text-gray-400 block font-mono bg-dark-card/60 p-1 rounded border border-dark-border/40">{f}</code>
                    ))}
                  </div>
                )}
                
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
