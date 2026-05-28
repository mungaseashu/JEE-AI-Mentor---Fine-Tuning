// ==============================================================================
// JEE MENTOR AI - HIGH-PRECISION DYNAMIC MATH & LATEX TYPESETTER
// ==============================================================================
import React from 'react';
import katex from 'katex';

export default function MathRenderer({ text = '' }) {
  if (!text) return null;

  // Process text line-by-line or split by block/inline LaTeX tags
  // We tokenize using a robust double-pass parsing strategy:
  // 1. Separate block equations ($$ ... $$)
  // 2. Separate inline equations ($ ... $)
  
  const renderMath = (formula, isBlock) => {
    try {
      const html = katex.renderToString(formula, {
        displayMode: isBlock,
        throwOnError: false,
        trust: true
      });
      return <span dangerouslySetInnerHTML={{ __html: html }} />;
    } catch (e) {
      console.warn("KaTeX rendering error: ", e);
      return <code className="px-1 py-0.5 bg-dark-border rounded text-red-400 font-mono">{formula}</code>;
    }
  };

  const parseText = (rawStr) => {
    if (!rawStr) return [];
    
    // First, split by block math $$
    const blockParts = rawStr.split('$$');
    
    return blockParts.flatMap((blockPart, bIdx) => {
      // Even indexes are text (possibly containing inline math), odd indexes are block math
      if (bIdx % 2 !== 0) {
        return (
          <div key={`block-${bIdx}`} className="my-4 p-4 bg-dark-card border border-dark-border rounded-xl text-center overflow-x-auto text-brand-primary">
            {renderMath(blockPart, true)}
          </div>
        );
      }
      
      // Split inline math $ inside text segment
      const inlineParts = blockPart.split('$');
      return inlineParts.map((inlinePart, iIdx) => {
        if (iIdx % 2 !== 0) {
          return (
            <span key={`inline-${bIdx}-${iIdx}`} className="mx-1 px-1.5 py-0.5 bg-dark-card border border-dark-border rounded text-brand-secondary inline-block font-mono">
              {renderMath(inlinePart, false)}
            </span>
          );
        }
        
        // Render simple text segments (with markdown bold formatting simple support)
        const formatBoldText = (txt) => {
          const boldParts = txt.split('**');
          return boldParts.map((boldPart, idx) => {
            if (idx % 2 !== 0) {
              return <strong key={idx} className="font-bold text-white">{boldPart}</strong>;
            }
            // Simple new line formatting
            const lines = boldPart.split('\n');
            return lines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {line}
                {lIdx < lines.length - 1 && <br />}
              </React.Fragment>
            ));
          });
        };
        
        return <React.Fragment key={`text-${bIdx}-${iIdx}`}>{formatBoldText(inlinePart)}</React.Fragment>;
      });
    });
  };

  return <div className="prose-math leading-relaxed text-sm md:text-base text-gray-300">{parseText(text)}</div>;
}
