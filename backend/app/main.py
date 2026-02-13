from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
import traceback
from app.core import logging_config # noqa
from app.core.config import settings
from app.db import base # noqa
from app.db.session import get_db
from app.api import api_router
from app.core.middleware import LoggingMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error (it might have been logged by middleware already, but 
    # capturing it here ensures it's logged even if middleware is bypassed or fails)
    logger.error(f"Global exception caught for {request.method} {request.url.path}: {str(exc)}")
    
    if settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
                "path": request.url.path,
                "method": request.method
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

# Register centralized logging middleware
app.add_middleware(LoggingMiddleware)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://.*\.up\.railway\.app$",
    allow_origins=[
        "https://react-frontend-production-e144.up.railway.app",
        "https://fastapi-production-bc086.up.railway.app",
        *[str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for media
uploads_path = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
if not os.path.exists(uploads_path):
    os.makedirs(uploads_path)
app.mount(settings.MEDIA_URL, StaticFiles(directory=uploads_path), name="media")

@app.get("/")
def root():
    return {"message": "Welcome to cschool API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
