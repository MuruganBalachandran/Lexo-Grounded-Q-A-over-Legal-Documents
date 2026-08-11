import React, { useState } from 'react';
import type { Citation } from '../../types/ask.types';
import { formatCitation } from '../../utils/formatCitation';
import { cn } from '../../utils/classNames';
import ReactMarkdown from 'react-markdown';

interface CitationChipProps {
  citation: Citation;
}

export const CitationChip: React.FC<CitationChipProps> = ({ citation }) => {
  const [isOpen, setIsOpen] = useState(false);
  const label = formatCitation(citation.source_file, citation.chunk_id);

  return (
    <div className="relative inline-block">
      <button 
        className={cn(
          "relative overflow-hidden bg-transparent border border-citation text-citation py-1 px-3 rounded-sm font-mono text-xs font-medium transition-all duration-200 hover:bg-citation hover:text-bg focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2",
          "before:content-[''] before:absolute before:-top-1 before:-right-1 before:w-2 before:h-2 before:bg-bg before:rotate-45 before:border-l before:border-citation",
          isOpen && "bg-citation text-bg"
        )}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span>{label}</span>
      </button>
      
      {isOpen && (
        <div className="absolute top-[calc(100%+0.5rem)] left-0 z-20 w-max max-w-[320px] bg-surface border border-border rounded p-4 shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.5)] animate-in fade-in slide-in-from-top-1 duration-200">
          <div className="text-sm mb-3 leading-relaxed [&_h1]:font-semibold [&_h2]:font-semibold [&_h3]:font-semibold [&_strong]:font-semibold [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:list-decimal [&_ol]:pl-4">
            <ReactMarkdown>{citation.snippet}</ReactMarkdown>
          </div>
          <div className="flex flex-col gap-1 font-mono text-[0.7rem] text-inkSecondary">
            <span>Source: {citation.source_file}</span>
            <span>Relevance: {(citation.score * 100).toFixed(1)}%</span>
          </div>
        </div>
      )}
    </div>
  );
};
