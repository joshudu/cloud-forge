from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.routers import health, tenants, auth, projects, resources
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.security import limiter

setup_logging()

app = FastAPI(title="CloudForge", version="0.1.0")

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — explicitly list allowed origins, never use "*" in production
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

@app.get("/")
def root():
    return {"message": "CloudForge API"}