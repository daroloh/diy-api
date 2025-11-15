from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import simulate

app = FastAPI(
    title="API Failure Simulator & Troubleshooting Playground",
    description="Simulate common API failure conditions for debugging and learning. Perfect for API support engineers and developers learning about API error handling.",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API Failure Simulator is running"}


if __name__ == "__main__":
    import os
    import uvicorn

    # Allow overriding the host/port via environment variables for flexibility
    host = os.getenv("HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT", "8000"))
    except ValueError:
        port = 8000

    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)