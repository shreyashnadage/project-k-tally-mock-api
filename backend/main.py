from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.data_routes import router as data_router
from backend.api.health_routes import router as health_router
from backend.api.simulation_routes import router as simulation_router
from backend.api.tdml_routes import router as tdml_router
from backend.config import settings
from backend.database import init_db

app = FastAPI(
    title="Tally Data Simulator",
    description="Generate realistic MSME financial data and serve it via Tally-compatible TDML/XML API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tdml_router, tags=["tdml"])
app.include_router(simulation_router, prefix="/api/simulations", tags=["simulations"])
app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(health_router, prefix="/api", tags=["health"])

# Serve React frontend if built assets are present
_STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        return FileResponse(_STATIC_DIR / "index.html")


@app.on_event("startup")
def startup():
    init_db()
