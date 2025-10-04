"""
X Sentiment Analysis API
Main FastAPI application entrypoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.sentiment import router as sentiment_router

app = FastAPI(
    title="X Sentiment Analysis API",
    description="Daily batch sentiment analysis for Bitcoin, MSTR, and Bitcoin treasuries",
    version="0.1.0"
)

# CORS middleware for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sentiment_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "x-sentiment-analysis"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
