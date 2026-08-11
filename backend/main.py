"""
backend/main.py
───────────────
FastAPI application entry point.

Routes are defined in backend/api/routes/

Run:
    uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from pipeline.graph.graph import get_graph
from api.routes import health, ask, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compile graph once on startup so first request isn't slow
    get_graph()
    print("[startup] LangGraph compiled and ready.")
    yield


app = FastAPI(
    title="Legixo Document Q&A API",
    description="Answer questions strictly from a legal document corpus.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Register routes
app.include_router(health.router)
app.include_router(ask.router)
app.include_router(ingest.router)
