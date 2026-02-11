import structlog
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.logging_conf import configure_structlog
from app.api.v1 import recipes, subscribers

# 1. Initialize Sentry
if hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# 2. Configure Structlog (Using central config)
configure_structlog()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", msg="Application starting up")
    yield
    logger.info("shutdown", msg="Application shutting down")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 3. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc))
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred."},
    )

# 5. Monitoring
Instrumentator().instrument(app).expose(app)

# 6. Routers
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(subscribers.router, prefix="/subscribers", tags=["subscribers"])
