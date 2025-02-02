import logging
from contextlib import asynccontextmanager

import uvicorn
from api.v1 import api
from beanie import init_beanie
from core.config import settings
from core.logger import LOGGING
from core.tracer import configure_tracer
from db.models import Film, Review, User
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from services.health import router as health_router

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache: Redis = Redis(host=settings.redis.host, port=settings.redis.port)
    motor: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo.url)
    await init_beanie(
        database=motor[settings.mongo.database], document_models=[User, Film, Review]
    )
    yield
    await cache.close()
    motor.close()


app = FastAPI(
    title=settings.project,
    docs_url=f"/{settings.project}/api/openapi",
    openapi_url=f"/{settings.project}/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


app.include_router(health_router)
app.include_router(api.router, prefix=f"/{settings.project}/api/v1")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_config=LOGGING, log_level=logging.ERROR)
