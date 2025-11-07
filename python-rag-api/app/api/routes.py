"""
API routes aggregator
"""
from fastapi import APIRouter
from app.api.endpoints import health, documents, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)

