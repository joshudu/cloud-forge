from fastapi import FastAPI
from app.routers import health, tenants, auth

app = FastAPI(title="CloudForge", version="0.1.0")

app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "CloudForge API"}