import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from src.api.rpa_routes import router as rpa_router
from src.api.data_routes import router as data_router
from src.api.workflow_routes import router as workflow_router
from src.api.document_ai_routes import router as document_ai_router
from src.api.task_routes import router as task_router


from src.core.config import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
)
logger = logging.getLogger("PyAutomateAI")


os.makedirs("static", exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise AI Automation Platform"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(rpa_router, prefix="/api/v1", tags=["RPA Automation"])
app.include_router(data_router, prefix="/api/v1", tags=["Advanced Data Processing"])
app.include_router(workflow_router, prefix="/api/v1", tags=["Workflow Engine"])
app.include_router(document_ai_router, prefix="/api/v1", tags=["Document AI"])
app.include_router(task_router, prefix="/api/v1", tags=["Task Monitoring"])


@app.get("/")
async def root():
    return {
        "project": "PyAutomate AI",
        "status": "running",
        "modules": ["RPA", "Data Processing", "Workflow Engine", "Document AI"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test")
async def test_endpoint():
    return {"status": "ok"}

@app.get("/favicon.ico")
async def favicon():
    path = "static/favicon.ico"
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(status_code=204, content=None)