import React from 'react';
import { useTheme } from '../../hooks/useTheme';
import { Moon, Sun } from 'lucide-react';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className="flex items-center justify-center w-10 h-10 rounded-full text-ink transition-all duration-200 hover:bg-surfaceMuted active:scale-95 focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
      onClick={toggleTheme}
      aria-label="Toggle theme"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
    </button>
  );
};
