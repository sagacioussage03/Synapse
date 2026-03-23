import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from logger import setup_logging, get_logger
from config import load_config, get_services
from routers import hardware, system

logger = get_logger("core")


# ── Lifespan events ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    load_config()
    logger.info("Synapse Core started")
    yield
    logger.info("Synapse Core shutting down")


app = FastAPI(title="Project Synapse - Control Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Routers ───────────────────────────────────────────────
app.include_router(hardware.router)
app.include_router(system.router)


@app.get("/")
def read_root():
    return {"status": "Synapse Core is Online"}


@app.get("/config/services")
def list_services():
    return {"services": get_services()}