from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, families, requests, events, schemes, eligibility, benefits, identity, departments, audit, analytics, notifications

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pravi ID — Gujarat Family Identity & Beneficiary Management Platform. DEMO/HACKATHON PROTOTYPE.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(families.router)
app.include_router(requests.router)
app.include_router(events.router)
app.include_router(schemes.router)
app.include_router(eligibility.router)
app.include_router(benefits.router)
app.include_router(identity.router)
app.include_router(departments.router)
app.include_router(audit.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
        "note": "DEMO/HACKATHON PROTOTYPE — Uses synthetic data. Not connected to live government systems."
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
