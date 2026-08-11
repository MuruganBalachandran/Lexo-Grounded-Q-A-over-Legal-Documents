import React from 'react';
import { Header } from './Header';
import { Footer } from './Footer';

interface PageShellProps {
  children: React.ReactNode;
}

export const PageShell: React.FC<PageShellProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 flex flex-col w-[70%] mx-auto p-8 px-6">
        {children}
      </main>
      <Footer />
    </div>
  );
};
