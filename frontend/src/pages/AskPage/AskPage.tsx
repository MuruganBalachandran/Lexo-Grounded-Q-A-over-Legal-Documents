import React from 'react';
import { useAsk } from '../../hooks/useAsk';
import { AskForm } from '../../components/AskForm/AskForm';
import { AnswerCard } from '../../components/AnswerCard/AnswerCard';
import { NotFoundState } from '../../components/NotFoundState/NotFoundState';

export const AskPage: React.FC = () => {
  const { status, result, error } = useAsk();
  const isLoading = status === 'loading';
  const hasResult = status === 'succeeded' && result;
  
  // Is it a refusal/not found?
  const isNotFound = hasResult && !result.grounded;

  return (
    <div className="flex flex-col w-full">
      <div className="mb-8 text-lg text-inkSecondary max-w-[65ch] leading-relaxed">
        <p>
          Query the fictional legal corpus. Ask about employment agreements, 
          settlements, or matter memos.
        </p>
      </div>

      <AskForm />

      {error && (
        <div className="mt-6 p-4 bg-refuseMuted border-l-4 border-refuse rounded text-refuse font-medium">
          <p>{error}</p>
        </div>
      )}

      {(isLoading || (hasResult && !isNotFound)) && (
        <AnswerCard isLoading={isLoading} result={result} />
      )}

      {isNotFound && (
        <NotFoundState message={result?.answer} />
      )}
    </div>
  );
};
