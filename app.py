from src.main import app
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
# Import routers (adjust paths if needed)
from src.main import app
# ---------------------------
# Logging Configuration
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------
# Lifespan Events (Startup / Shutdown)
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting PyAutomate AI...")
    
    # TODO: initialize database here
    # TODO: load ML models
    # TODO: connect Redis / Celery

    yield

    logger.info("🛑 Shutting down PyAutomate AI...")


# ---------------------------
# FastAPI App Initialization
# ---------------------------
app = FastAPI(
    title="PyAutomate AI",
    description="AI + RPA Automation Platform",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------
# Root Endpoint
# ---------------------------
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "PyAutomate AI is live 🚀"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# ---------------------------
# Global Exception Handler (Basic)
# ---------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return {
        "error": "Internal Server Error",
        "detail": str(exc)
    }