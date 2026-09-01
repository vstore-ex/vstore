from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.api.media import router as media_router
from app.api.search import router as search_router
from app.admin import setup_admin

from app.models import Base, User, Role
from app.core.config import settings
from app.core.db import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware


# init fastApi
app = FastAPI(title=settings.PROJECT_NAME)

origins = [
    "https://vstore-admin.lemonbush-87bea63a.italynorth.azurecontainerapps.io",
    "https://vstore-frontend.lemonbush-87bea63a.italynorth.azurecontainerapps.io",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db setup
Base.metadata.create_all(bind=engine)

# @app.on_event("startup")
# def run_migrations():
#     try:
#         alembic_cfg = Config("alembic.ini")
#         command.upgrade(alembic_cfg, "head")
#     except Exception as err:
#         print(f"migration fail: {err}")

# api routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")


# admin setup
setup_admin(app)

@app.get("/")
async def read_root():
    return {"message": "vstore is running. go to /admin"}
