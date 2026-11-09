from sqlalchemy import inspect, text

from src.db import engine


TABLE_NAME = "vulnerabilities"
COLUMN_NAME = "view_count"


def main():
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(TABLE_NAME)}

    if COLUMN_NAME not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE vulnerabilities "
                    "ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0"
                )
            )
        print("Added vulnerabilities.view_count")
    else:
        print("vulnerabilities.view_count already exists")


if __name__ == "__main__":
    main()
