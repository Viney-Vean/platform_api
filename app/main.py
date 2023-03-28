from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

apm = make_apm_client({
    'SERVICE_NAME': 'apm-platform-api',
    'SECRET_TOKEN': '',
    'SERVER_URL': 'http://localhost:8200',
    'ENVIRONMENT': 'production',
    'DEBUG': True,
    'CAPTURE_HEADERS': True,
    'CAPTURE_BODY': 'all'
})

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.add_middleware(ElasticAPM, client=apm)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
