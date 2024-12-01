from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import report, scan, update_model

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(scan.router, prefix="/api", tags=["scan"])
