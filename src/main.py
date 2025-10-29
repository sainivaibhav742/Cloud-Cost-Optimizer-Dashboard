from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.api.routes import router
from src.api.auth_routes import router as auth_router
from src.jobs.scheduler import setup_scheduler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloud Cost Optimizer Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Cloud Cost Optimizer Dashboard API"}

# Start background scheduler on app startup
@app.on_event("startup")
async def startup_event():
    """Initialize background jobs on startup."""
    try:
        scheduler = setup_scheduler()
        scheduler.start()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Application shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
