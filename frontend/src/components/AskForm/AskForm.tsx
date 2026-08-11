import React, { useState } from 'react';
import { useAsk } from '../../hooks/useAsk';
import { toast } from 'react-hot-toast';
import { Send, Loader2 } from 'lucide-react';

export const AskForm: React.FC = () => {
  const [input, setInput] = useState('');
  const { askQuestion, status } = useAsk();
  const isLoading = status === 'loading';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      toast.error('Please enter a question.');
      return;
    }
    askQuestion(trimmed);
  };

  return (
    <form 
      className="flex flex-col bg-surface border border-border rounded-lg overflow-hidden transition-all duration-200 focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20" 
      onSubmit={handleSubmit}
    >
      <textarea
        className="w-full border-none bg-transparent p-4 resize-none text-ink text-base outline-none disabled:opacity-60 disabled:cursor-not-allowed"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question about the documents..."
        disabled={isLoading}
        rows={3}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <div className="flex justify-end px-4 py-3 border-t border-border bg-bg">
        <button
          type="submit"
          className="flex items-center gap-2 bg-ink text-bg px-4 py-2 rounded font-medium transition-all duration-200 enabled:hover:opacity-90 enabled:active:translate-y-[1px] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <Send size={18} />
          )}
          <span>Submit</span>
        </button>
      </div>
    </form>
  );
};
