from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(
    title="Video Downloader API",
    description="API for downloading videos from YouTube and Facebook",
    version="1.0.0",
)

# Allow CORS so other websites can use our API if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix="/api")

# Mount static files (the frontend UI) at the root
# Ensure that the 'public' directory exists
app.mount("/", StaticFiles(directory="public", html=True), name="public")
