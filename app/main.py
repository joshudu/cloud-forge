from fastapi import FastAPI
from app.routers import health, tenants

app = FastAPI(title="CloudForge", version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(tenants.router)

@app.get("/")
def root():
    return {"message": "CloudForge API"}