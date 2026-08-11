import React from 'react';
import { ThemeToggle } from '../components/ThemeToggle/ThemeToggle';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-bg transition-colors duration-200">
      <div className="w-[70%] mx-auto p-6 flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-mono text-xs font-medium tracking-widest text-citation mb-1">IN RE:</span>
          <h1 className="text-xl font-semibold tracking-wide m-0">DOCUMENT Q&A</h1>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
};
