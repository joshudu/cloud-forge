from fastapi import FastAPI
from app.routers import health

app = FastAPI(title = "CloudForge", version = "1.0.0")

app.include_router(health.router, tags=["health"])

@app.get("/")
def root():
    return{"message": "CloudForgeAPI"}

