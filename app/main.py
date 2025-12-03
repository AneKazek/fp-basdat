import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.logging import add_timing_middleware, setup_logging
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

app.include_router(monitor_router)
app.include_router(wallet_tracker_router)

logger = structlog.get_logger()
logger.info("service_started", rate_limit=settings.rate_limit_str(), log_level=settings.LOG_LEVEL)

