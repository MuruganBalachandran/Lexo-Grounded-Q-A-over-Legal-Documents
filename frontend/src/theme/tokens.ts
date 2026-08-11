export const tokens = {
  light: {
    bg: '#EEF0EA',
    surface: '#FFFFFF',
    surfaceMuted: '#F4F5F0',
    ink: '#1B2A35',
    inkSecondary: '#5B6B75',
    border: '#D8DBD1',
    accent: '#2E5339',
    accentMuted: '#E1EAE4',
    citation: '#9C6B30',
    citationMuted: '#F1E6D6',
    refuse: '#7A2E2E',
    refuseMuted: '#F3E3E3',
  },
  dark: {
    bg: '#10161C',
    surface: '#1A222B',
    surfaceMuted: '#212B35',
    ink: '#E6E7E2',
    inkSecondary: '#8C9199',
    border: '#2A333C',
    accent: '#5FA678',
    accentMuted: '#1D2E24',
    citation: '#C9974F',
    citationMuted: '#33291A',
    refuse: '#C1615B',
    refuseMuted: '#331E1D',
  },
  font: {
    display: "'Fraunces', serif",
    body: "'Inter', sans-serif",
    mono: "'IBM Plex Mono', monospace",
  },
} as const;

export type Theme = 'light' | 'dark';
export const THEME_KEY = 'legixo_theme_preference';
