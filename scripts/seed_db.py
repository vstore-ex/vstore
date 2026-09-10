import sys
import os
from typing import Any, Type, Dict

# Ensure the app package is importable
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.core.db import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.user import Role, User
from app.models.taxonomy import Tag
from app.models.game import Game, GameBanner, GameMedia, BannerType, MediaType
from app.models.achievement import Achievement
from app.models.review import GameReview
from app.models.comment import CommentThread
from app.models.discover import DiscoverLayout
from app.models.support import SupportArticle

def get_or_create(session: Session, model: Type, defaults: Dict[str, Any], lookup_key: str):
    lookup_value = defaults.get(lookup_key)
    instance = session.query(model).filter(getattr(model, lookup_key) == lookup_value).first()
    if instance:
        return instance
    else:
        instance = model(**defaults)
        session.add(instance)
        session.commit()
        return instance

def seed_database():
    session = SessionLocal()
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        print("Starting database seeding...")

        # 1. Roles
        print("Seeding Roles...")
        admin_role = get_or_create(session, Role, {
            "name": "admin",
            "can_buy": True,
            "can_message": True,
            "can_ban": True
        }, "name")

        user_role = get_or_create(session, Role, {
            "name": "user",
            "can_buy": True,
            "can_message": True,
            "can_ban": False
        }, "name")

        # 2. Users
        print("Seeding Users...")
        admin_user = get_or_create(session, User, {
            "username": "admin",
            "email": "admin@vstore.com",
            "password": get_password_hash("adminpassword"),
            "full_name": "System Administrator",
            "role_id": admin_role.id
        }, "email")

        demo_user = get_or_create(session, User, {
            "username": "demo_user",
            "email": "user@vstore.com",
            "password": get_password_hash("userpassword"),
            "full_name": "Demo User",
            "role_id": user_role.id
        }, "email")

        # 3. Taxonomy (Tags)
        print("Seeding Tags...")
        tags_data = [
            {"name": "Action", "slug": "action"},
            {"name": "RPG", "slug": "rpg"},
            {"name": "Indie", "slug": "indie"},
            {"name": "Strategy", "slug": "strategy"},
            {"name": "Adventure", "slug": "adventure"},
        ]
        tags = {}
        for t in tags_data:
            tag = get_or_create(session, Tag, t, "slug")
            tags[t["name"]] = tag

        # 4. Games (Products)
        print("Seeding Games...")
        games_data = [
            {
                "title": "Cyber Odyssey 2077",
                "description_md": "An immersive journey through a neon-lit metropolis where technology and humanity collide.",
                "original_price": 59.99,
                "price": 44.99,
                "is_free": False,
                "developer": "Neo Studio",
                "publisher": "CyberCorp",
                "rating": "PEGI 18",
                "tags": ["Action", "RPG"]
            },
            {
                "title": "Mystic Realms",
                "description_md": "Explore a vast open world filled with magic, mystery, and ancient ruins.",
                "original_price": 39.99,
                "price": 29.99,
                "is_free": False,
                "developer": "Arcane Games",
                "publisher": "Magic House",
                "rating": "PEGI 12",
                "tags": ["RPG", "Adventure"]
            },
            {
                "title": "Void Runner",
                "description_md": "High-speed racing in the depths of outer space. Defy gravity and outrun the void.",
                "original_price": 0.00,
                "price": 0.00,
                "is_free": True,
                "developer": "Stellar Soft",
                "publisher": "Void Pub",
                "rating": "PEGI 3",
                "tags": ["Action", "Indie"]
            }
        ]

        seeded_games = []
        for g in games_data:
            # We use title as lookup key for Games
            game = get_or_create(session, Game, {
                "title": g["title"],
                "description_md": g["description_md"],
                "original_price": g["original_price"],
                "price": g["price"],
                "is_free": g["is_free"],
                "developer": g["developer"],
                "publisher": g["publisher"],
                "rating": g["rating"],
            }, "title")

            # Associate Tags
            game.tags = [tags[tag_name] for tag_name in g["tags"]]

            seeded_games.append(game)

        session.commit()

        # 5. Game Assets (Banners & Media)
        print("Seeding Game Assets...")
        for game in seeded_games:
            # Banners
            banner_types = [
                BannerType.MAIN_HERO,
                BannerType.SPECIAL_OFFER,
                BannerType.SMALL_CAPSULE,
                BannerType.GAME_PAGE_HEADER,
                BannerType.LIBRARY_ICON,
                BannerType.LIBRARY_POSTER,
                BannerType.LIBRARY_HERO,
                BannerType.COLLECTION_HEADER,
            ]
            for bt in banner_types:
                # Using a combination of game_id and banner_type for uniqueness check
                exists = session.query(GameBanner).filter_by(game_id=game.id, banner_type=bt).first()
                if not exists:
                    banner = GameBanner(
                        game_id=game.id,
                        banner_type=bt,
                        image_url=f"https://placehold.co/600x400?text={game.title}+{bt.value}"
                    )
                    session.add(banner)

            # Media (Gallery)
            for i in range(3):
                media = GameMedia(
                    game_id=game.id,
                    media_type=MediaType.IMAGE,
                    url=f"https://placehold.co/1280x720?text={game.title}_screenshot_{i+1}",
                    thumbnail_url=f"https://placehold.co/200x150?text={game.title}_{i+1}",
                    sort_order=i
                )
                session.add(media)

        session.commit()

        # 6. Achievements
        print("Seeding Achievements...")
        for game in seeded_games:
            ach_data = [
                {"id": f"ach_{game.id}_1", "title": "First Steps", "description": "Complete the tutorial.", "icon": "icon1.png", "completion_percent": 10},
                {"id": f"ach_{game.id}_2", "title": "Master", "description": "Achieve the highest rank.", "icon": "icon2.png", "completion_percent": 100},
            ]
            for ad in ach_data:
                exists = session.query(Achievement).filter_by(id=ad["id"]).first()
                if not exists:
                    ach = Achievement(
                        id=ad["id"],
                        product_id=game.id,
                        title=ad["title"],
                        description=ad["description"],
                        icon=ad["icon"],
                        completion_percent=ad["completion_percent"]
                    )
                    session.add(ach)

        session.commit()

        # 7. Reviews
        print("Seeding Reviews...")
        for game in seeded_games:
            # One review per game from demo user
            thread = CommentThread() # Assuming CommentThread can be created without arguments or with minimal
            session.add(thread)
            session.flush() # Get thread ID

            review = GameReview(
                game_id=game.id,
                user_id=demo_user.id,
                thread_id=thread.id,
                is_positive=True,
                content_md=f"Amazing game! I love the gameplay and graphics of {game.title}.",
                is_hidden=False
            )
            session.add(review)

        session.commit()

        # 8. Discover Layout
        print("Seeding Discover Layout...")
        layout = session.query(DiscoverLayout).first()
        if not layout:
            layout = DiscoverLayout()
            session.add(layout)
            session.flush()

        layout.featured_game_id = seeded_games[0].id
        layout.sections = [
            {"title": "Trending Now", "type": "grid", "game_ids": [g.id for g in seeded_games]},
            {"title": "New Releases", "type": "carousel", "game_ids": [seeded_games[1].id]},
        ]
        layout.promos = [
            {"title": "Summer Sale", "image_url": "https://placehold.co/1200x400?text=Summer+Sale", "link": "/store/sale"},
        ]
        layout.deals_game_ids = [seeded_games[0].id, seeded_games[1].id]
        layout.free_games_game_ids = [seeded_games[2].id]
        layout.ranked_columns = [
            {"title": "Top Rated", "game_ids": [g.id for g in seeded_games]},
        ]
        layout.mobile_banner = {"image_url": "https://placehold.co/400x200?text=Mobile+Promo", "link": "/store"}

        session.commit()

        # 9 support articles
        print("Seeding Support Articles...")
        articles_data = [
            {"title": "How to reset password", "content_md": "Go to settings and click reset...", "category": "Account"},
            {"title": "Payment methods", "content_md": "We accept Visa, Mastercard, and PayPal...", "category": "Payment"},
            {"title": "Technical issues", "content_md": "Ensure your drivers are updated...", "category": "Technical"},
            {"title": "Refund policy", "content_md": "Refunds are available within 14 days...", "category": "Payment"},
            {"title": "Contacting support", "content_md": "You can open a ticket in your profile...", "category": "Account"},
        ]
        for ad in articles_data:
            exists = session.query(SupportArticle).filter_by(title=ad["title"]).first()
            if not exists:
                article = SupportArticle(**ad)
                session.add(article)

        session.commit()

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()