from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Callable  # Added List

import uvicorn
from dotenv import load_dotenv  # Add this import
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse  # Add JSONResponse
from fastapi.staticfiles import StaticFiles

# Adjust imports for new location (src/bin -> src)
from ...aurite import (  # Corrected relative import (up two levels from src/bin/api)
    Aurite,
)
from ...utils.errors import (
    AgentExecutionError,
    ConfigurationError,
    MCPServerTimeoutError,
    WorkflowExecutionError,
)

# Import shared dependencies (relative to parent directory - src/bin)
from ..dependencies import (
    get_server_config,  # Re-import ServerConfig if needed locally, or remove if only used in dependencies.py
)

# Ensure host models are imported correctly (up two levels from src/bin/api)
# Import the new routers (relative to current file's directory)
from .routes import main_router
from ..studio.static_server import setup_studio_routes_with_static

# Removed CustomWorkflowManager import
# Hello
# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file at the very beginning
load_dotenv()  # Add this call


# --- Configuration Dependency, Security Dependency, Aurite Dependency (Moved to dependencies.py) ---


# --- FastAPI Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle FastAPI lifecycle events: initialize Aurite on startup, shutdown on exit."""
    from pathlib import Path

    logger.info("Initializing Aurite for FastAPI application...")
    # Explicitly set start_dir to ensure context is found regardless of CWD
    aurite_instance = Aurite(start_dir=Path.cwd())
    # The __aenter__ will trigger the lazy initialization.
    await aurite_instance.__aenter__()
    app.state.aurite_instance = aurite_instance
    logger.info("Aurite initialized and ready.")

    yield  # Server runs here

    logger.info("Shutting down Aurite...")
    # The __aexit__ will handle the graceful shutdown.
    await aurite_instance.__aexit__(None, None, None)
    logger.info("Aurite shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="Aurite Agents API",
    description="API for the Aurite Agents framework - a Python framework for building AI agents using the Model Context Protocol (MCP)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api-docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema endpoint
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Collapse models by default
)

# Setup CORS middleware immediately during app creation
# This ensures CORS is configured regardless of how the server is started
try:
    server_config = get_server_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=server_config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS middleware configured with origins: {server_config.ALLOWED_ORIGINS}")
except Exception as e:
    # Fallback CORS configuration for development
    logger.warning(f"Could not load server config for CORS, using development fallback: {e}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware configured with development fallback origins")


# --- Health Check Endpoint ---
# Define simple routes directly on app first
@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


# main routes
app.include_router(main_router)


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema, optionally loading from external file."""
    if app.openapi_schema:
        return app.openapi_schema

    # Fallback to auto-generated schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Let FastAPI auto-detect security from Security() dependencies
    # Testing if newer FastAPI versions can detect nested Security dependencies
    logger.info("Using auto-generated OpenAPI schema with FastAPI's built-in security detection")

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the OpenAPI schema function
app.openapi = custom_openapi  # type: ignore[no-redef]


# --- Custom Exception Handlers ---
# Define handlers before endpoints that might raise these exceptions


# Handler for ConfigurationErrors
@app.exception_handler(ConfigurationError)
async def configuration_error_exception_handler(request: Request, exc: ConfigurationError):
    logger.warning(f"Configuration error: {exc} for request {request.url.path}")
    return JSONResponse(
        status_code=404,  # Not Found, as the requested resource config is missing
        content={"detail": str(exc)},
    )


# Handler for AgentExecutionErrors
@app.exception_handler(AgentExecutionError)
async def agent_execution_error_exception_handler(request: Request, exc: AgentExecutionError):
    logger.error(f"Agent execution error: {exc} for request {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,  # Internal Server Error
        content={"detail": f"Agent execution failed: {str(exc)}"},
    )


# Handler for WorkflowExecutionErrors
@app.exception_handler(WorkflowExecutionError)
async def workflow_execution_error_exception_handler(request: Request, exc: WorkflowExecutionError):
    logger.error(f"Workflow execution error: {exc} for request {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,  # Internal Server Error
        content={"detail": f"Workflow execution failed: {str(exc)}"},
    )


# Handler for MCPServerTimeoutError
@app.exception_handler(MCPServerTimeoutError)
async def mcp_server_timeout_error_handler(request: Request, exc: MCPServerTimeoutError):
    logger.error(
        f"MCP server timeout error: {exc} for request {request.url.path} - "
        f"Server: {exc.server_name}, Timeout: {exc.timeout_seconds}s, Operation: {exc.operation}"
    )
    return JSONResponse(
        status_code=504,  # Gateway Timeout
        content={
            "error": "mcp_server_timeout",
            "detail": str(exc),
            "server_name": exc.server_name,
            "timeout_seconds": exc.timeout_seconds,
            "operation": exc.operation,
        },
    )


# Handler for FileNotFoundError (e.g., custom workflow module, client server path)
@app.exception_handler(FileNotFoundError)
async def file_not_found_error_handler(request: Request, exc: FileNotFoundError):
    logger.error(f"Required file not found: {exc} for request {request.url.path}")
    return JSONResponse(
        status_code=404,  # Treat as Not Found, could argue 500 if it's internal config
        content={"detail": f"Required file not found: {str(exc)}"},
    )


# Handler for setup/import errors related to custom workflows
@app.exception_handler(AttributeError)
@app.exception_handler(ImportError)
@app.exception_handler(PermissionError)
@app.exception_handler(TypeError)
async def custom_workflow_setup_error_handler(request: Request, exc: Exception):
    # Check if the request path involves custom_workflows to be more specific
    # This is a basic check; more robust checking might involve inspecting the exception origin
    is_custom_workflow_path = "/custom_workflows/" in request.url.path
    error_type = type(exc).__name__

    if is_custom_workflow_path:
        logger.error(
            f"Error setting up custom workflow ({error_type}): {exc} for request {request.url.path}",
            exc_info=True,
        )
        detail = f"Error setting up custom workflow: {error_type}: {str(exc)}"
        status_code = 500  # Internal server error during setup
    else:
        # If it's not a custom workflow path, treat as a generic internal error
        logger.error(
            f"Internal server error ({error_type}): {exc} for request {request.url.path}",
            exc_info=True,
        )
        detail = f"Internal server error: {error_type}: {str(exc)}"
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


# Handler for RuntimeErrors (e.g., during custom workflow execution, config loading)
@app.exception_handler(RuntimeError)
async def runtime_error_exception_handler(request: Request, exc: RuntimeError):
    logger.error(
        f"Runtime error encountered: {exc} for request {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,  # Internal Server Error
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Generic fallback handler for any other exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc} for request {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected internal server error occurred: {type(exc).__name__}"},
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log all HTTP requests."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "Unknown")

    logger.info(
        f"[{request.method}] {request.url.path} - Status: {response.status_code} - "
        f"Duration: {duration:.3f}s - Client: {client_ip} - "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
    )

    return response


# --- Static Files for Swagger UI ---
# FastAPI 0.115+ changed how Swagger UI assets are served
# We need to configure it to use CDN assets instead of local files
try:
    # Override the default swagger_ui_parameters to use CDN assets
    app.swagger_ui_parameters = {
        **app.swagger_ui_parameters,
        "swagger_js_url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        "swagger_css_url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    }
    logger.info("✓ Swagger UI configured to use CDN assets")
except Exception as e:
    logger.warning(f"⚠ Error configuring Swagger UI CDN assets: {e}")

logger.info("✓ Swagger UI configured at /api-docs")
logger.info("✓ ReDoc configured at /redoc") 
logger.info("✓ OpenAPI schema available at /openapi.json")

# Mount custom static files if they exist (for studio assets)
try:
    from pathlib import Path
    static_dir = Path(__file__).parent.parent / "studio" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.debug(f"✓ Mounted custom static files from {static_dir}")
except Exception as e:
    logger.debug(f"No custom static files to mount: {e}")


# --- Health Check Endpoint (Moved earlier) ---


# Setup static file serving for Aurite Studio if available
# IMPORTANT: This must come AFTER all other API routes but BEFORE catch-all routes
try:
    studio_static_setup = setup_studio_routes_with_static(app)
    if studio_static_setup:
        logger.info("✓ Aurite Studio static assets configured and available at /studio")
    else:
        logger.info("⚠ Aurite Studio static assets not available - studio will use development mode")
        
        # Fallback catch-all route for paths not handled by API
        # IMPORTANT: Exclude FastAPI's internal paths for Swagger UI
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_fallback(full_path: str):
            """Fallback for unmatched routes when static assets are not available."""
            # Don't intercept FastAPI's internal Swagger UI assets
            if full_path.startswith("swagger/") or full_path.startswith("redoc/"):
                raise HTTPException(status_code=404, detail="Not Found")
            raise HTTPException(status_code=404, detail="Not Found")
except Exception as e:
    logger.error(f"Error setting up static file serving: {e}")
    # Fallback catch-all route for paths not handled by API
    # IMPORTANT: Exclude FastAPI's internal paths for Swagger UI
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_fallback_error(full_path: str):
        """Fallback for unmatched routes when static setup failed."""
        # Don't intercept FastAPI's internal Swagger UI assets
        if full_path.startswith("swagger/") or full_path.startswith("redoc/"):
            raise HTTPException(status_code=404, detail="Not Found")
        raise HTTPException(status_code=404, detail="Not Found")


# --- End Serve React Frontend Build ---


def start():
    """
    Start the FastAPI application with uvicorn.
    In development, this function will re-exec uvicorn with --reload.
    In production, it runs the server directly.
    """
    # Load config to get server settings
    config = get_server_config()
    if not config:
        logger.critical("Server configuration could not be loaded. Aborting startup.")
        raise RuntimeError("Server configuration could not be loaded. Aborting startup.")

    # Determine reload mode based on environment. Default to development mode.
    reload_mode = os.getenv("ENV", "development").lower() != "production"

    # In development (reload mode), it's more stable to hand off execution directly
    # to the uvicorn CLI. This avoids issues with the reloader in a programmatic context.
    if reload_mode:
        logger.info(
            f"Development mode detected. Starting Uvicorn with reload enabled on {config.HOST}:{config.PORT}..."
        )
        # Use os.execvp to replace the current process with uvicorn.
        # This is the recommended way to run with --reload from a script.
        args = [
            "uvicorn",
            "aurite.bin.api.api:app",
            "--host",
            config.HOST,
            "--port",
            str(config.PORT),
            "--log-level",
            config.LOG_LEVEL.lower(),
            "--reload",
        ]
        os.execvp("uvicorn", args)
    else:
        # In production, run uvicorn programmatically without the reloader.
        # This is suitable for running with multiple workers.
        logger.info(
            f"Production mode detected. Starting Uvicorn on {config.HOST}:{config.PORT} with {config.WORKERS} worker(s)..."
        )
        uvicorn.run(
            "aurite.bin.api.api:app",
            host=config.HOST,
            port=config.PORT,
            workers=config.WORKERS,
            log_level=config.LOG_LEVEL.lower(),
            reload=False,
        )


if __name__ == "__main__":
    start()
