from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.api.media import router as media_router
from app.api.search import router as search_router
from app.api.games import router as games_router
from app.api.reviews import router as reviews_router
from app.api.taxonomy import router as taxonomy_router
from app.api.artworks import router as artworks_router
from app.api.community import router as community_router
from app.api.users import router as users_router
from app.api.achievements import router as achievements_router
from app.api.wishlists import router as wishlists_router
from app.api.cart import router as cart_router
from app.api.orders import router as orders_router
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
app.include_router(games_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(taxonomy_router, prefix="/api/v1")
app.include_router(artworks_router, prefix="/api/v1")
app.include_router(community_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(achievements_router, prefix="/api/v1")
app.include_router(wishlists_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")

app.include_router(search_router, prefix="/api/v1")


# admin setup
setup_admin(app)

@app.get("/")
async def read_root():
    return {"message": "vstore is running. go to /admin"}