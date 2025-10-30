"""
Application FastAPI principale pour le backend de pricing.

Ce module configure l'application FastAPI avec tous les routers
et les middlewares nécessaires (CORS pour React, etc.).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import pricing_router

# Création de l'application FastAPI
app = FastAPI(
    title="Interest Rate Modeling API",
    description="API de pricing pour produits dérivés (options, swaps, etc.)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les requêtes depuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Permet tous les headers
)

# Inclusion des routers
app.include_router(pricing_router.router)

# Route racine pour vérifier que l'API fonctionne
@app.get("/")
async def root():
    """
    Route racine de l'API.
    
    Returns:
        Message de bienvenue avec les liens vers la documentation
    """
    return {
        "message": "Interest Rate Modeling API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "pricing": "/api/pricing",
            "health": "/api/pricing/health"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check général de l'API.
    
    Returns:
        Status de l'API
    """
    return {
        "status": "healthy",
        "service": "interest-rate-modeling-api",
        "version": "1.0.0"
    }


# Point d'entrée pour lancer l'application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload pendant le développement
        log_level="info"
    )
