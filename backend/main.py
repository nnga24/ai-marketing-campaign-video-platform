from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.config import settings

app = FastAPI(
    title="AI Video Marketing MVP",
    description="SaaS Backend for Automated Video Generation",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def read_root():
    return {"message": "Welcome to AI Video Marketing API"}

from api.routes import generate, project, projects_v2

app.include_router(project.router, prefix="/api/projects", tags=["Projects"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])

app.include_router(
    projects_v2.router,
    prefix="/api/v2/projects",
    tags=["Projects v2"],
)

import os
os.makedirs("frontend/css", exist_ok=True)
os.makedirs("frontend/js", exist_ok=True)

# Mount statics
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Trả về index.html nếu không match router API
    if not full_path.startswith("api"):
        if full_path == "gallery" or full_path == "gallery/":
            return FileResponse("frontend/gallery.html")
        return FileResponse("frontend/index.html")
    return {"error": "Not found"}
