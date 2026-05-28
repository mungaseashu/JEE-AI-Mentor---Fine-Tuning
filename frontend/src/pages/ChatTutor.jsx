// ==============================================================================
// JEE MENTOR AI - INTERACTIVE TUTOR CHAT & STREAMING WORKSPACE
// ==============================================================================
import React, { useState, useEffect, useRef } from 'react';
import { Send, Upload, Cpu, FileText, AlertCircle, Bot, User, CheckCircle2 } from 'lucide-react';
import MathRenderer from '../components/MathRenderer';

export default function ChatTutor() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [ocrLoading, setOcrLoading] = useState(false);
  
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Scroll to bottom whenever messages list expands
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // 1. Add user message locally
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      });

      if (!response.ok) {
        throw new Error('API failed to respond.');
      }

      // 2. Set up SSE Reader stream loop
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let botResponse = '';
      let isFirstChunk = true;

      // Seed an empty assistant message to stream tokens into
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        
        // Extract session ID header if present on first chunk
        if (isFirstChunk && chunk.startsWith("SESSION_ID:")) {
          const lines = chunk.split('\n\n');
          const header = lines[0];
          const actualSessionId = header.split(':')[1];
          setSessionId(actualSessionId.trim());
          
          const actualText = lines.slice(1).join('\n\n');
          botResponse += actualText;
          isFirstChunk = false;
        } else {
          botResponse += chunk;
        }

        // Incrementally update assistant message in state
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: botResponse,
            // Include mock RAG source tracking for visuals
            sources: [
              { subject: 'Physics', topic: 'Gauss Law', type: 'NCERT Notes', relevance: 92 },
              { subject: 'Chemistry', topic: 'Kinetics', type: 'Formula Sheet', relevance: 88 }
            ]
          };
          return updated;
        });
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `[ERROR] Connection failed: ${err.message}. Please check that the FastAPI server is online at port 8000.` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setOcrLoading(true);
    setMessages((prev) => [...prev, { role: 'user', content: '[Uploaded Question Image]' }]);

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
          body: JSON.stringify({ image_base64: base64Str })
        });

        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Solver failed');
        }

        // Append solver outputs and base64 plots if generated
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `**Extracted OCR Question:**\n_${data.extracted_text}_\n\n**Step-by-step Solution:**\n${data.solution}`,
            formulas: data.formulas_used,
            graph_base64: data.graph_base64,
            latency: data.latency_ms
          }
        ]);
      };
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `OCR solver failed: ${err.message}.` }
      ]);
    } finally {
      setOcrLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col bg-dark-bg">
      {/* Chat log container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-primary to-brand-secondary shadow-neon-purple">
              <Bot className="h-9 w-9 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white">Ask your JEE doubts!</h3>
            <p className="text-sm text-gray-400">
              Type a problem, paste equation queries, or upload written notes. The AI will consult textbook notes to solve them step-by-step.
            </p>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex items-start space-x-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                {msg.role !== 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-primary/10 border border-brand-primary/20 text-brand-primary shadow-neon-purple/5">
                    <Bot className="h-4.5 w-4.5" />
                  </div>
                )}

                <div className={`max-w-[85%] rounded-2xl border px-4 py-3 shadow-sm ${
                  msg.role === 'user'
                    ? 'border-brand-primary/20 bg-brand-primary/5 text-white'
                    : 'border-dark-border bg-dark-card/40 text-gray-300'
                }`}>
                  <MathRenderer text={msg.content} />
                  
                  {/* Plot output image */}
                  {msg.graph_base64 && (
                    <div className="mt-4 border border-dark-border rounded-lg overflow-hidden bg-dark-bg">
                      <img src={msg.graph_base64} alt="Plotted Graph Chart" className="w-full h-auto" />
                    </div>
                  )}

                  {/* Injected formulas lists */}
                  {msg.formulas && msg.formulas.length > 0 && (
                    <div className="mt-3 p-2 bg-dark-bg/60 rounded border border-dark-border space-y-1">
                      <span className="text-[10px] font-bold text-brand-secondary block">Formulas Synced:</span>
                      {msg.formulas.map((f, fIdx) => (
                        <code key={fIdx} className="text-[10px] text-gray-400 block font-mono">{f}</code>
                      ))}
                    </div>
                  )}

                  {/* Collapsible Accordions for RAG context */}
                  {msg.role !== 'user' && msg.sources && msg.sources.length > 0 && (
                    <details className="group mt-3 border-t border-dark-border/40 pt-2 cursor-pointer">
                      <summary className="flex items-center justify-between text-[10px] font-semibold text-brand-secondary list-none select-none hover:text-white transition-all">
                        <span>📖 View revision sheets consulted</span>
                        <span className="text-[9px] text-dark-muted font-normal">Relevance: {msg.sources[0].relevance}%</span>
                      </summary>
                      <div className="mt-2 space-y-1.5 pl-1.5 border-l border-brand-secondary/30">
                        {msg.sources.map((src, sIdx) => (
                          <div key={sIdx} className="text-[10px] text-gray-400 leading-relaxed">
                            <strong className="text-white">[{src.type}]</strong> {src.subject} {src.topic} notes applied.
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-dark-border text-gray-300">
                    <User className="h-4.5 w-4.5" />
                  </div>
                )}
                
              </div>
            ))}
          </div>
        )}
        
        {loading && (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-primary/10 border border-brand-primary/20 text-brand-primary animate-pulse">
              <Bot className="h-4.5 w-4.5" />
            </div>
            <div className="rounded-2xl border border-dark-border bg-dark-card/40 px-4 py-3">
              <span className="flex items-center space-x-1.5 text-xs text-gray-400">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-primary" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-primary [animation-delay:0.2s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-primary [animation-delay:0.4s]" />
                <span>AI Tutor is drafting steps...</span>
              </span>
            </div>
          </div>
        )}

        {ocrLoading && (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-secondary/10 border border-brand-secondary/20 text-brand-secondary animate-pulse">
              <Cpu className="h-4.5 w-4.5" />
            </div>
            <div className="rounded-2xl border border-dark-border bg-dark-card/40 px-4 py-3">
              <span className="flex items-center space-x-1.5 text-xs text-brand-secondary">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-secondary border-t-transparent" />
                <span>Reading physical question image via OCR...</span>
              </span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Chat input container */}
      <div className="border-t border-dark-border bg-dark-card/40 p-4">
        <form onSubmit={handleSend} className="mx-auto flex max-w-4xl space-x-3">
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            onChange={handleImageUpload}
            className="hidden"
          />
          
          {/* Upload attachment button */}
          <button
            type="button"
            disabled={loading || ocrLoading}
            onClick={() => fileInputRef.current?.click()}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-dark-border text-gray-400 hover:text-white hover:bg-dark-border/40 hover:border-brand-primary/20 transition-all duration-200"
            title="Upload question photo"
          >
            <Upload className="h-5 w-5" />
          </button>

          {/* Text Input */}
          <input
            type="text"
            required
            disabled={loading || ocrLoading}
            placeholder="Ask a question (e.g. Find the MOI of a compound disc or integrate x*cos(x))..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 rounded-lg border border-dark-border bg-dark-bg/60 px-4 py-2.5 text-sm text-white placeholder-dark-muted focus:border-brand-primary focus:shadow-neon-purple focus:outline-none transition-all duration-300"
          />

          {/* Submit button */}
          <button
            type="submit"
            disabled={loading || ocrLoading || !input.trim()}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-brand-primary text-white shadow-neon-purple hover:opacity-95 transition-all disabled:opacity-50"
          >
            <Send className="h-4.5 w-4.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
