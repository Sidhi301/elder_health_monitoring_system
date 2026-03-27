

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
  
    return {"message": "Elder Health Monitoring System backend is running."}



app.include_router(auth_router)
app.include_router(health_router)
app.include_router(alert_router)
