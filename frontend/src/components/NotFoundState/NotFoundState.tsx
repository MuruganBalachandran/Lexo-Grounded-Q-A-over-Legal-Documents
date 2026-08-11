import React from 'react';
import { AlertCircle } from 'lucide-react';

interface NotFoundStateProps {
  message?: string;
}

export const NotFoundState: React.FC<NotFoundStateProps> = ({ 
  message = "I couldn't find an answer to that question in the provided documents." 
}) => {
  return (
    <div className="flex gap-4 bg-surface border border-refuse border-l-4 rounded-lg p-6 mt-6 transition-colors duration-200">
      <div className="flex-shrink-0 pt-1">
        <AlertCircle size={24} className="text-refuse" />
      </div>
      <div className="flex flex-col">
        <h2 className="text-lg text-refuse mb-2 font-sans font-medium">Answer Not Found</h2>
        <p className="font-serif text-[1.05rem] mb-3 leading-relaxed">{message}</p>
        <p className="text-sm text-inkSecondary">
          Try rephrasing your question or asking about a different topic from the corpus.
        </p>
      </div>
    </div>
  );
};
