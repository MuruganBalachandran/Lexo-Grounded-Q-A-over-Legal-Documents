import traceback
from fastapi import APIRouter, HTTPException
from backend.api.schemas.qa import IngestResponse
from backend.pipeline.ingest import run_ingest

router = APIRouter(tags=["Ingest"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest() -> IngestResponse:
    """
    Load the corpus from disk, embed chunks, and upsert to Pinecone.

    Safe to call multiple times — uses deterministic chunk IDs so re-running
    overwrites existing vectors rather than duplicating them.

    CLI alternative:
        python -m backend.pipeline.ingest [--dir path/to/corpus]
    """
    try:
        result = run_ingest()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(exc)}")

    return IngestResponse(
        files_processed=result["files_processed"],
        chunks_upserted=result["chunks_upserted"],
    )
