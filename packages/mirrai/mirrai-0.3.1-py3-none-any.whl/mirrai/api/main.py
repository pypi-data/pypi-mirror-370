import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mirrai.api.endpoints import agent, windows
from mirrai.api.execution_adapter import APIExecutionManager
from mirrai.core.constants import DEFAULT_API_HOST, DEFAULT_API_PORT
from mirrai.core.logger import logger

load_dotenv()

execution_manager: Optional[APIExecutionManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    _ = app
    global execution_manager

    # startup
    logger.info("Starting Mirrai API server")
    execution_manager = APIExecutionManager()
    logger.info("Execution manager initialized")

    yield

    # shutdown
    logger.info("Shutting down Mirrai API server")

    if execution_manager and execution_manager.core_manager._current_execution_id:
        try:
            await execution_manager.cancel_execution(
                execution_manager.core_manager._current_execution_id
            )
        except Exception:
            pass


app = FastAPI(
    title="Mirrai API",
    description="API for desktop automation using AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_execution_manager_override() -> APIExecutionManager:
    """Get the global execution manager instance."""
    if not execution_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    return execution_manager


app.include_router(agent.router)
app.include_router(windows.router)

from mirrai.api.endpoints.agent import get_execution_manager

app.dependency_overrides[get_execution_manager] = get_execution_manager_override


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Mirrai API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "agent": "/agent",
            "windows": "/windows",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "execution_manager": execution_manager is not None,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    _ = request
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", DEFAULT_API_HOST)
    port = int(os.getenv("API_PORT", str(DEFAULT_API_PORT)))

    uvicorn.run(
        "mirrai.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
