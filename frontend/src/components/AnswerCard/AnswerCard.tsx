import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { AskResponse } from '../../types/ask.types';
import { CitationChip } from '../CitationChip/CitationChip';

interface AnswerCardProps {
  isLoading: boolean;
  result?: AskResponse | null;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ isLoading, result }) => {
  if (isLoading) {
    return (
      <div className="bg-surface border border-border rounded-lg p-6 mt-6 transition-colors duration-200">
        <div className="mb-4">
          <div className="h-6 w-2/5 bg-surfaceMuted rounded animate-pulse"></div>
        </div>
        <div className="mb-8 flex flex-col gap-2">
          <div className="h-4 w-full bg-surfaceMuted rounded animate-pulse"></div>
          <div className="h-4 w-[95%] bg-surfaceMuted rounded animate-pulse"></div>
          <div className="h-4 w-4/5 bg-surfaceMuted rounded animate-pulse"></div>
        </div>
        <div className="flex gap-2 pt-5 border-t border-border">
          <div className="h-6 w-[120px] bg-surfaceMuted rounded animate-pulse"></div>
          <div className="h-6 w-[100px] bg-surfaceMuted rounded animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (!result || !result.grounded) {
    return null;
  }

  return (
    <div className="bg-surface border border-border rounded-lg p-6 mt-6 transition-colors duration-200">
      <h2 className="text-xl text-accent mb-4 font-serif font-medium">Answer</h2>
      <div className="font-serif text-lg leading-relaxed max-w-[65ch] mb-8 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mt-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:mt-2 [&_li]:mb-1 [&_strong]:font-semibold">
        <ReactMarkdown>{result.answer}</ReactMarkdown>
      </div>
      
      {result.citations.length > 0 && (
        <div className="border-t border-border pt-5">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-inkSecondary mb-3 font-sans">Exhibits Cited:</h3>
          <div className="flex flex-wrap gap-2">
            {result.citations.map((cit, idx) => (
              <CitationChip key={`${cit.chunk_id}-${idx}`} citation={cit} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
