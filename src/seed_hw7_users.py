from src.auth_api import hash_password
from src.db import db_session_basede26
from src.models import User


TEST_USERS = [
    {
        "name": "HW7 Reader",
        "username": "reader2604",
        "email": "reader2604@example.com",
        "password": "Reader2604!",
        "role": "reader",
    },
    {
        "name": "HW7 Writer",
        "username": "writer2604",
        "email": "writer2604@example.com",
        "password": "Writer2604!",
        "role": "writer",
    },
    {
        "name": "HW7 Moderator",
        "username": "moderator2604",
        "email": "moderator2604@example.com",
        "password": "Moderator2604!",
        "role": "moderator",
    },
]


def seed_users():
    db = db_session_basede26()

    try:
        for account in TEST_USERS:
            user = db.query(User).filter(User.username == account["username"]).first()

            if user is None:
                user = User(
                    name=account["name"],
                    username=account["username"],
                    email=account["email"],
                    password_hash=hash_password(account["password"]),
                    role=account["role"],
                )
                db.add(user)
            else:
                user.password_hash = hash_password(account["password"])
                user.role = account["role"]

        db.commit()
        print("HW7 test users created or updated.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
