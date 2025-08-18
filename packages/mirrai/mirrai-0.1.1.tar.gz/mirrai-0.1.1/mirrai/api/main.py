"""FastAPI application for Mirrai desktop automation."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mirrai.api.endpoints import agent, windows
from mirrai.api.execution_adapter import APIExecutionManager
from mirrai.core.logger import logger

# Load environment variables
load_dotenv()

# Global execution manager instance
execution_manager: Optional[APIExecutionManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global execution_manager

    # Startup
    logger.info("Starting Mirrai API server")

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment")
        raise ValueError("ANTHROPIC_API_KEY is required")

    # Initialize execution manager
    execution_manager = APIExecutionManager(anthropic_api_key=api_key)
    logger.info("Execution manager initialized")

    yield

    # Shutdown
    logger.info("Shutting down Mirrai API server")

    # Cancel any running executions
    if execution_manager and execution_manager.core_manager._current_execution_id:
        try:
            await execution_manager.cancel_execution(
                execution_manager.core_manager._current_execution_id
            )
        except Exception:
            pass  # Ignore errors during shutdown


# Create FastAPI app
app = FastAPI(
    title="Mirrai API",
    description="API for desktop automation using AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Override the dependency in agent endpoints
def get_execution_manager_override() -> APIExecutionManager:
    """Get the global execution manager instance."""
    if not execution_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    return execution_manager


# Include routers
app.include_router(agent.router)
app.include_router(windows.router)

# Override the dependency using FastAPI's dependency overrides
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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8777"))

    # Run the server
    uvicorn.run(
        "mirrai.api.main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload in development
        log_level="info",
    )
