import React from 'react';
import { ThemeProvider } from './theme/ThemeProvider';
import { PageShell } from './layout/PageShell';
import { AskPage } from './pages/AskPage/AskPage';
import { Toaster } from 'react-hot-toast';
import { useTheme } from './hooks/useTheme';

const AppContent: React.FC = () => {
  const { theme } = useTheme();
  
  return (
    <>
      <PageShell>
        <AskPage />
      </PageShell>
      <Toaster 
        position="bottom-right"
        toastOptions={{
          style: {
            background: theme === 'dark' ? '#1A222B' : '#FFFFFF',
            color: theme === 'dark' ? '#E6E7E2' : '#1B2A35',
            border: `1px solid ${theme === 'dark' ? '#2D3945' : '#C8CCC1'}`,
            fontFamily: "'IBM Plex Sans', sans-serif"
          }
        }}
      />
    </>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;
