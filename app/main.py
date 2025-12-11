from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from sqlalchemy import text
from app.database import SessionLocal
from app.app_logging import add_timing_middleware, setup_logging
from app.rate_limit import limiter
from app.routers.monitor import router as monitor_router
from app.routers.wallet_tracker import router as wallet_tracker_router


setup_logging(settings.LOG_LEVEL)
app = FastAPI(title="Sepolia Wallet Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
add_timing_middleware(app)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... imports ...

app.include_router(monitor_router)
app.include_router(wallet_tracker_router)

# Mount static files for frontend (Monolith Mode)
# Ensure this is after API routers so API routes take precedence
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(static_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")
    
    # Catch-all route for SPA (Single Page Application)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Check if file exists in root of dist (e.g. favicon.ico)
        file_path = os.path.join(static_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise return index.html for React Router
        return FileResponse(os.path.join(static_path, "index.html"))
else:
    import structlog
    logger = structlog.get_logger()
    logger.warning("Frontend build not found. Run 'npm run build' in frontend/ directory to enable monolith mode.")

import structlog
logger = structlog.get_logger()
logger.info("service_started", rate_limit=settings.rate_limit_str(), log_level=settings.LOG_LEVEL)

@app.get("/health")
async def health():
    db_ok = True
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    finally:
        try:
            db.close()
        except Exception:
            pass
    return {
        "status": "ok",
        "db": db_ok,
        "etherscan_key": bool(settings.ETHERSCAN_API_KEY),
    }

