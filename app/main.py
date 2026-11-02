from fastapi import FastAPI

from app.config import settings
from app.api.invoices import router as invoices_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered invoice processing system"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version
    }


app.include_router(invoices_router)
