from sqladmin import Admin, ModelView
from app.models import Base, User, Role
from app.core.db import engine

def setup_admin(app):
    admin = Admin(app, engine=engine)

    admin.add_view(UserView)
    admin.add_view(RoleView)

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
