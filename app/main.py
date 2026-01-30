"""
FastAPI main application entry point for AI SaaS backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import prompts, workflows, debug, content, auth, payments
from app.config import settings

app = FastAPI(
    title="Social Media Planner API",
    description="AI-powered social media content planning for small businesses",
    version="2.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Social Media Planner API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
