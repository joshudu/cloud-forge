from fastapi import FastAPI
from app.routers import health, tenants, auth, projects, resources
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware

# Set up logging before anything else
setup_logging()

app = FastAPI(title="CloudForge", version="0.1.0")

# Add middleware — order matters, first added is outermost
app.add_middleware(RequestContextMiddleware)

app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(resources.router)

@app.get("/")
def root():
    return {"message": "CloudForge API"}