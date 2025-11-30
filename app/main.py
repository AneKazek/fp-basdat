import structlog
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.logging import add_timing_middleware, setup_logging
from app.rate_limit import limiter
from app.routers.monitor import router as monitor_router


setup_logging(settings.LOG_LEVEL)
app = FastAPI(title="Sepolia Wallet Monitor", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
add_timing_middleware(app)

app.include_router(monitor_router)

logger = structlog.get_logger()
logger.info("service_started", rate_limit=settings.rate_limit_str(), log_level=settings.LOG_LEVEL)

