"""
This is the main FastAPI entry file.
It creates the app, enables CORS, and includes the route files.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.alert_routes import router as alert_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.health_routes import router as health_router


app = FastAPI(
    title="Elder Health Monitoring System",
    description="Simple FastAPI backend for elder health tracking.",
    version="1.0.0",
)


# CORS lets the frontend call the backend from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    """
    Simple test route to confirm the backend is running.
    """
    return {"message": "Elder Health Monitoring System backend is running."}


# Add route modules to the app.
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(alert_router)
