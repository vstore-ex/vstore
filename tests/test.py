import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.db import get_db
from app.models.base import Base
from app.core.security import get_password_hash
from app.models import User, Role, Game, Tag, GameReview, Order, CommentThread
from app.schemas import GameCreate, GameAdminUpdate, TagCreate, AchievementCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    admin_role = Role(name="admin", can_buy=True, can_message=True, can_ban=True)
    user_role = Role(name="user", can_buy=True, can_message=True, can_ban=False)
    db.add_all([admin_role, user_role])
    db.commit()

    admin_user = User(
        username="admin_test",
        email="admin@test.com",
        password=get_password_hash("password123"),
        role=admin_role
    )
    db.add(admin_user)
    db.commit()

    reg_user = User(
        username="user_test",
        email="user@test.com",
        password=get_password_hash("userpass"),
        role=user_role
    )
    db.add(reg_user)
    db.commit()

    tag = Tag(name="Action", slug="action")
    db.add(tag)
    db.commit()

    game = Game(
        title="Test Game",
        description_md="Testing description",
        price=10.0,
        original_price=15.0,
        is_free=False,
        tags=[tag]
    )
    db.add(game)
    db.commit()

    thread = CommentThread()
    db.add(thread)
    db.commit()
    review = GameReview(
        game_id=game.id,
        user_id=reg_user.id,
        thread_id=thread.id,
        is_positive=True,
        content_md="Amazing game!"
    )
    db.add(review)
    db.commit()

    yield
    Base.metadata.drop_all(bind=engine)
    db.close()

def get_token(username="admin_test", password="password123"):
    response = client.post(
        "/api/v1/login",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

class TestAuthAndSecurity:
    def test_login_success(self):
        res = client.post("/api/v1/login", data={"username": "admin_test", "password": "password123"})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_fail(self):
        res = client.post("/api/v1/login", data={"username": "admin_test", "password": "wrong"})
        assert res.status_code == 401

    def test_admin_endpoint_forbidden_for_user(self):
        token = get_token("user_test", "userpass")
        res = client.post("/api/v1/admin/tags", headers={"Authorization": f"Bearer {token}"}, json={"name": "Forbidden"})
        assert res.status_code == 403

class TestPublicAPI:
    def test_get_games(self):
        res = client.get("/api/v1/games")
        assert res.status_code == 200
        assert len(res.json()) > 0

    def test_get_discover(self):
        res = client.get("/api/v1/discover/discover")
        assert res.status_code == 200
        assert "featured" in res.json()

    def test_reviews_visibility(self):
        res = client.get("/api/v1/games/1/reviews")
        assert res.status_code == 200
        assert len(res.json()) == 1

class TestAdminCMS:
    def test_tag_crud(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/v1/admin/tags", headers=headers, json={"name": "Horror"})
        assert res.status_code == 201
        tag_id = res.json()["id"]
        res = client.patch(f"/api/v1/admin/tags/{tag_id}", headers=headers, json={"name": "Psychological Horror"})
        assert res.status_code == 200
        res = client.delete(f"/api/v1/admin/tags/{tag_id}", headers=headers)
        assert res.status_code == 204

    def test_tag_duplicate(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/api/v1/admin/tags", headers=headers, json={"name": "UniqueTag"})
        res = client.post("/api/v1/admin/tags", headers=headers, json={"name": "UniqueTag"})
        assert res.status_code == 400

    def test_game_crud(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/v1/admin/games", headers=headers, json={
            "title": "Admin Game", "description_md": "Desc", "price": 5.0, "tag_ids": []
        })
        assert res.status_code == 201
        game_id = res.json()["id"]
        res = client.delete(f"/api/v1/admin/games/{game_id}", headers=headers)
        assert res.status_code == 204

    def test_media_upload(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        with patch("app.services.media.MediaService.upload_bytes", return_value="http://fake.url/img.webp"), \
             patch("app.services.media.MediaService.convert_to_webp", return_value=b"fake"):
            with open("dummy.jpg", "wb") as f: f.write(b"fake")
            res = client.post(
                "/api/v1/admin/games/1/banners",
                headers=headers,
                data={"banner_type": "main_hero"},
                files={"file": open("dummy.jpg", "rb")}
            )
            assert res.status_code == 200
            assert "image_url" in res.json()
            os.remove("dummy.jpg")

    def test_achievement_create(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post(
            "/api/v1/admin/games/1/achievements",
            headers=headers,
            json={"id": "ACH_1", "title": "First Blood", "description": "Kill someone", "icon": "icon.png", "completion_percent": 10.0}
        )
        assert res.status_code == 201
        assert res.json()["id"] == "ACH_1"

    def test_discover_update(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.patch(
            "/api/v1/admin/discover",
            headers=headers,
            json={"featured_game_id": 1}
        )
        assert res.status_code == 200
        assert "updated successfully" in res.json()["message"]

class TestModeration:
    def test_review_moderation(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.patch("/api/v1/admin/reviews/1/hide", headers=headers)
        assert res.status_code == 200
        res_pub = client.get("/api/v1/games/1/reviews")
        assert len(res_pub.json()) == 0

    def test_user_role_update(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.patch("/api/v1/admin/users/2", headers=headers, json={"role_id": 1})
        assert res.status_code == 200
        assert res.json()["role_name"] == "admin"

    def test_order_status_update(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}

        db = TestingSessionLocal()
        order = Order(
            user_id=1,
            payment_method="card",
            subtotal=100.0,
            tax=20.0,
            total=120.0,
            status="pending"
        )
        db.add(order)
        db.commit()
        order_id = order.id
        db.close()

        res = client.patch(f"/api/v1/admin/orders/{order_id}", headers=headers, data={"status": "shipped"})
        assert res.status_code == 200
        assert "shipped" in res.json()["message"]

class TestStats:
    def test_public_stats(self):
        res = client.get("/api/v1/stats/reviews-activity")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_admin_stats(self):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/v1/stats/admin/revenue", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)