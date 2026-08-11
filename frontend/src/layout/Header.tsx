import React, { useState } from 'react';
import { ThemeToggle } from '../components/ThemeToggle/ThemeToggle';
import { ArchitectureModal } from '../components/ArchitectureModal/ArchitectureModal';
import { Info } from 'lucide-react';

export const Header: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-bg transition-colors duration-200">
      <div className="w-[70%] mx-auto p-6 flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-mono text-xs font-medium tracking-widest text-citation mb-1">IN RE:</span>
          <h1 className="text-xl font-semibold tracking-wide m-0 flex items-center gap-3">
            DOCUMENT Q&A
            <button 
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1.5 text-xs font-mono font-normal text-inkSecondary hover:text-ink bg-surfaceMuted px-2 py-1 rounded border border-border transition-colors"
              title="View Architecture"
            >
              <Info size={14} />
              How it works
            </button>
          </h1>
        </div>
        <ThemeToggle />
      </div>

      <ArchitectureModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </header>
  );
};
