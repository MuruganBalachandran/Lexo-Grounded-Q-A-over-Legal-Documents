# Legixo Docket Backend

This is the document-grounded Q&A HTTP API. It handles the ingestion of legal documents into a vector database and processes user queries using a sophisticated LLM-as-a-judge pipeline.

## Tech Stack & Libraries

- **Python 3.10+**: The core language.
- **FastAPI & Uvicorn**: Chosen for building a high-performance, asynchronous REST API with automatic OpenAPI documentation.
- **LangGraph**: Used to construct the complex, stateful LLM workflow (Retrieve -> Grade -> Generate/Refuse). It allows for strict control loops and easy debugging of the AI's thought process.
- **Pinecone**: A serverless vector database used to store and query document chunks efficiently.
- **Google GenAI (Gemini)**:
  - `gemini-embedding-001` (via REST): High quality semantic embeddings for retrieval.
  - `gemini-2.5-flash`: The core LLM used for both judging the relevance of chunks and generating the final grounded answer.
- **Pydantic**: For strict data validation (settings, API requests, API responses).

## Quick Start

### Installation
```bash
python -m venv .venv
# Activate: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
```

### Setup Environment
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

### Ingest Corpus
```bash
python -m pipeline.ingest
```

### Run Server
```bash
python -m uvicorn main:app --reload
```
