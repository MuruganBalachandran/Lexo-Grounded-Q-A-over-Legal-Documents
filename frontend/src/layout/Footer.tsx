import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-border bg-bg p-6 transition-colors duration-200">
      <div className="w-[70%] mx-auto text-center">
        <p className="font-mono text-xs text-inkSecondary">
          Fictional corpus for evaluation purposes &middot; Not legal advice.
        </p>
      </div>
    </footer>
  );
};
