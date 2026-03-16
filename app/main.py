from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from contextlib import asynccontextmanager
from app.routers import health, tenants, auth, projects, resources, admin
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.core.security import limiter

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("CloudForge starting up")
    logger.info("database connection pool initialised")
    yield
    # Shutdown — this runs when ECS sends SIGTERM
    logger.info("CloudForge shutting down gracefully")
    logger.info("waiting for in-flight requests to complete")
    # Give in-flight requests time to complete
    import asyncio
    await asyncio.sleep(2)
    logger.info("shutdown complete")

app = FastAPI(
    title="CloudForge",
    version="0.1.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(resources.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "CloudForge API"}