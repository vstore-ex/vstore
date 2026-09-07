from sqladmin import Admin, ModelView
from app.models import Base, User, Role, Achievement, UserAchievement
from app.core.db import engine

def setup_admin(app):
    admin = Admin(app, engine=engine)

    admin.add_view(UserView)
    admin.add_view(RoleView)
    admin.add_view(AchievementView)
    admin.add_view(UserAchievementView)

    return admin

class UserView(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.phone, User.full_name, User.is_banned]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username]
    form_columns = [User.username, User.full_name, User.is_banned, "role_id"]

class RoleView(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.can_buy, Role.can_message, Role.can_ban]
    column_searchable_list = [Role.name]
    column_sortable_list = [Role.id, Role.name]
    form_columns = [Role.name, Role.can_buy, Role.can_message, Role.can_ban]

class AchievementView(ModelView, model=Achievement):
    column_list = [Achievement.id, Achievement.product_id, Achievement.title, Achievement.completion_percent]
    column_searchable_list = [Achievement.id, Achievement.title]
    column_sortable_list = [Achievement.id, Achievement.product_id, Achievement.completion_percent]
    form_columns = [Achievement.id, Achievement.product_id, Achievement.title, Achievement.description, Achievement.icon, Achievement.completion_percent]

class UserAchievementView(ModelView, model=UserAchievement):
    column_list = [UserAchievement.id, UserAchievement.user_id, UserAchievement.achievement_id, UserAchievement.unlocked_at]
    column_searchable_list = [UserAchievement.achievement_id]
    column_sortable_list = [UserAchievement.id, UserAchievement.user_id, UserAchievement.unlocked_at]
    form_columns = [UserAchievement.user_id, UserAchievement.achievement_id]