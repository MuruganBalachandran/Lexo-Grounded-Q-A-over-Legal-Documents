import traceback
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from api.schemas.qa import AskRequest, AskResponse, Citation
from pipeline.graph.graph import get_graph
from pipeline.graph.state import QAState

router = APIRouter(tags=["Q&A"])

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    Answer a question from the legal document corpus.

    - Retrieves relevant chunks from Pinecone.
    - Grades chunk relevance using Gemini (LLM-as-judge).
    - Generates a grounded answer with source citations.
    - If no relevant chunks found after retries, returns an honest refusal.
    """
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    graph = get_graph()

    # Initialise state
    initial_state: Dict[str, Any] = {
        "question": request.question.strip(),
        "retrieved_chunks": [],
        "grade": "",
        "graded_chunks": [],
        "answer": "",
        "citations": [],
        "grounded": False,
        "retry_count": 0,
        "trace": [],
    }

    try:
        final_state: QAState = graph.invoke(initial_state)
    except Exception as exc:
        traceback.print_exc()
        error_msg = str(exc)
        
        # Gracefully handle Gemini Free Tier rate limits
        if "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="The AI provider's free-tier rate limit has been reached (15 requests/minute). Please wait 60 seconds and try your question again.",
            )
            
        raise HTTPException(
            status_code=502,
            detail=f"Graph execution failed: {error_msg}",
        )

    citations = [
        Citation(
            source_file=c.get("source_file", ""),
            chunk_id=c.get("chunk_id", ""),
            snippet=c.get("snippet", ""),
            score=float(c.get("score", 0.0)),
        )
        for c in final_state.get("citations", [])
    ]

    return AskResponse(
        answer=final_state.get("answer", ""),
        citations=citations,
        grounded=final_state.get("grounded", False),
        trace=final_state.get("trace", []),
    )
