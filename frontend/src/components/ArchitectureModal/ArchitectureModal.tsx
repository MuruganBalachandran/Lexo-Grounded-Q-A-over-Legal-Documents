import React, { useEffect } from 'react';
import { X, Database, GitMerge, FileCheck2, ShieldAlert } from 'lucide-react';

interface ArchitectureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ArchitectureModal: React.FC<ArchitectureModalProps> = ({ isOpen, onClose }) => {
  // Prevent scrolling on body when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-ink/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-3xl bg-surface rounded-xl shadow-2xl border border-border overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-6 border-b border-border bg-surfaceMuted">
          <div>
            <h2 className="text-xl font-display font-semibold text-ink m-0">System Architecture</h2>
            <p className="text-sm text-inkSecondary mt-1">How Legixo Docket processes your queries</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-inkSecondary hover:text-ink hover:bg-border rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-10">
          
          <section>
            <h3 className="text-sm font-mono font-semibold text-citation tracking-widest mb-4 border-b border-border pb-2">1. INGESTION PIPELINE (DATA PREP)</h3>
            <div className="bg-surfaceMuted p-5 rounded-lg border border-border space-y-4">
              <p className="text-sm text-ink leading-relaxed">
                <strong>Goal:</strong> Transform raw Markdown legal documents into a searchable vector index while preserving semantic context.
              </p>
              <ul className="list-disc pl-5 text-sm text-inkSecondary space-y-2">
                <li><strong>Chunking Strategy:</strong> Documents are split strictly on `##` Markdown headers. <em>Why?</em> Legal documents rely heavily on section context (e.g., "Termination Clause"). Splitting by characters would destroy this context.</li>
                <li><strong>Embeddings:</strong> Used `gemini-embedding-001` via the official Google REST API with `task_type="RETRIEVAL_DOCUMENT"`.</li>
                <li><strong>Storage:</strong> Upserted to a <strong>Pinecone Serverless</strong> index (cosine similarity, 3072 dimensions). Metadata (`chunk_id`, `source_file`, `section_title`) is attached to every vector to guarantee 100% accurate citations later.</li>
              </ul>
            </div>
          </section>

          <section>
            <h3 className="text-sm font-mono font-semibold text-citation tracking-widest mb-4 border-b border-border pb-2">2. LLM-AS-A-JUDGE (LANGGRAPH ARCHITECTURE)</h3>
            <div className="bg-surfaceMuted p-5 rounded-lg border border-border space-y-6">
              <p className="text-sm text-ink leading-relaxed">
                <strong>Goal:</strong> Prevent hallucinations by ensuring the LLM only answers if the retrieved data actually contains the answer. Built using <strong>LangGraph StateGraph</strong> for deterministic state management.
              </p>
              
              <div className="pl-4 border-l-2 border-border space-y-6">
                <div>
                  <h4 className="font-semibold text-ink text-sm mb-1 flex items-center gap-2">
                    <Database size={16} className="text-citation" /> 
                    Node: Retrieve
                  </h4>
                  <p className="text-xs text-inkSecondary leading-relaxed">
                    Embeds the user's query using `task_type="RETRIEVAL_QUERY"` (asymmetric retrieval) and fetches the Top-K (5) closest chunks from Pinecone.
                  </p>
                </div>
                
                <div>
                  <h4 className="font-semibold text-ink text-sm mb-1 flex items-center gap-2">
                    <FileCheck2 size={16} className="text-accent" /> 
                    Node: Grade Chunks (The LLM Judge)
                  </h4>
                  <p className="text-xs text-inkSecondary leading-relaxed">
                    Passes the retrieved chunks and the question to <strong>Gemini 2.5 Flash</strong>. It strictly grades "yes" or "no" on relevance. <em>Why?</em> Vector search might return the closest chunks, but they still might not contain the actual answer (e.g., out-of-corpus questions). This judge catches those near-misses.
                  </p>
                </div>

                <div className="bg-bg p-4 rounded border border-border">
                  <h4 className="font-semibold text-ink text-sm mb-2 flex items-center gap-2">
                    <GitMerge size={16} className="text-inkSecondary" /> 
                    Conditional Branching & Loop Guard
                  </h4>
                  <ul className="list-disc pl-5 text-xs text-inkSecondary space-y-2">
                    <li>If <strong>Sufficient</strong> ➡️ Routes to `generate` node to build the final grounded answer.</li>
                    <li>If <strong>Insufficient</strong> ➡️ Loops back to `retrieve` to try again, capped at a strict `MAX_RETRIES=2` limit to prevent infinite LLM spinning.</li>
                    <li>If <strong>Out of Retries</strong> ➡️ Routes to `not_found` for an honest refusal.</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};
