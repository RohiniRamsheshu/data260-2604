from sqlalchemy import inspect, text

from src.db import engine


def migrate_users_table():
    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    with engine.begin() as connection:
        if "username" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD COLUMN username VARCHAR(100) NULL UNIQUE
                    """
                )
            )

        if "role" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD COLUMN role VARCHAR(20)
                    NULL DEFAULT 'reader'
                    """
                )
            )

        connection.execute(
            text(
                """
                UPDATE users
                SET username = SUBSTRING_INDEX(email, '@', 1)
                WHERE username IS NULL
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE users
                SET role = 'reader'
                WHERE role IS NULL
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE users
                MODIFY username VARCHAR(100) NOT NULL
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE users
                MODIFY role VARCHAR(20)
                NOT NULL DEFAULT 'reader'
                """
            )
        )


if __name__ == "__main__":
    migrate_users_table()
    print("HW7 users table migration completed.")