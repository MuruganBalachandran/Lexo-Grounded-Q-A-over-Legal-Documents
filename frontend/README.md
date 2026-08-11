# Legixo Docket Frontend

This is the user interface for the Legixo Docket Q&A system. It provides a clean, "Ledger"-themed UI for querying legal documents with distinct citation features.

## Tech Stack & Libraries

- **React 18 & TypeScript**: For building a robust, type-safe, and component-driven user interface.
- **Vite**: Chosen for its incredibly fast hot-module-reloading and optimized production builds.
- **Tailwind CSS v3**: Used for rapid, utility-first styling. It completely replaces cumbersome CSS modules while allowing us to easily inject our custom design tokens (Sage Paper, Ink Navy).
- **Redux Toolkit (RTK)**: Centralized state management. Decouples the API fetching and loading/error states (`askSlice`) from the React component tree, avoiding context-soup.
- **Axios**: Configured with a central client to handle API communication with the FastAPI backend.
- **react-hot-toast**: For elegant, non-intrusive toast notifications (errors, validations, successes).
- **lucide-react**: A lightweight, clean SVG icon library.

## Quick Start

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Production Build
```bash
npm run build
```
