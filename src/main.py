from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from src.api.routes import router
from src.api.auth_routes import router as auth_router
from src.jobs.scheduler import setup_scheduler
from src.models.database import create_tables

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

# Initialize database tables on startup
create_tables()

# Include routers
app.include_router(router)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Cloud Cost Optimizer Dashboard API"}

# Performance monitoring middleware
@app.middleware("http")
async def add_performance_monitoring(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log performance metrics
    from src.services.monitoring_service import monitoring
    monitoring.log_api_performance(
        endpoint=str(request.url.path),
        method=request.method,
        response_time=process_time,
        status_code=response.status_code
    )

    return response

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
