from app.core.db import engine, SessionLocal
from app.models import Role

def init_roles():
    db = SessionLocal()
    roles = ["user", "admin"]
    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            print(f"Creating role: {role_name}")
            db.add(Role(name=role_name))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_roles()
