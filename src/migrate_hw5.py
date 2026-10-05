from sqlalchemy import inspect, text

from src.db import engine


def get_columns(table_name: str) -> set[str]:
    inspector = inspect(engine)
    return {
        column["name"]
        for column in inspector.get_columns(table_name)
    }


with engine.begin() as connection:
    # Find an existing researcher to own old vulnerability records.
    researcher = connection.execute(
        text(
            """
            SELECT id
            FROM researchers
            ORDER BY id
            LIMIT 1
            """
        )
    ).first()

    if researcher is None:
        connection.execute(
            text(
                """
                INSERT INTO researchers
                    (first_name, last_name, email, created_at, updated_at)
                VALUES
                    (:first_name, :last_name, :email,
                     UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "first_name": "System",
                "last_name": "Researcher",
                "email": "system.researcher@example.com",
            },
        )

        researcher = connection.execute(
            text(
                """
                SELECT id
                FROM researchers
                ORDER BY id
                LIMIT 1
                """
            )
        ).first()

    researcher_id = researcher[0]
    columns = get_columns("vulnerabilities")

    if "severity" not in columns:
        connection.execute(
            text(
                """
                ALTER TABLE vulnerabilities
                ADD COLUMN severity INT NOT NULL DEFAULT 0
                """
            )
        )

    if "researcher_id" not in columns:
        connection.execute(
            text(
                """
                ALTER TABLE vulnerabilities
                ADD COLUMN researcher_id INT NULL
                """
            )
        )

    if "created_at" not in columns:
        connection.execute(
            text(
                """
                ALTER TABLE vulnerabilities
                ADD COLUMN created_at DATETIME NULL
                """
            )
        )

    if "updated_at" not in columns:
        connection.execute(
            text(
                """
                ALTER TABLE vulnerabilities
                ADD COLUMN updated_at DATETIME NULL
                """
            )
        )

    # Assign existing HW4 records to an existing researcher.
    connection.execute(
        text(
            """
            UPDATE vulnerabilities
            SET researcher_id = :researcher_id
            WHERE researcher_id IS NULL
            """
        ),
        {"researcher_id": researcher_id},
    )

    connection.execute(
        text(
            """
            UPDATE vulnerabilities
            SET created_at = UTC_TIMESTAMP()
            WHERE created_at IS NULL
            """
        )
    )

    connection.execute(
        text(
            """
            UPDATE vulnerabilities
            SET updated_at = UTC_TIMESTAMP()
            WHERE updated_at IS NULL
            """
        )
    )

    connection.execute(
        text(
            """
            ALTER TABLE vulnerabilities
            MODIFY COLUMN researcher_id INT NOT NULL
            """
        )
    )

    connection.execute(
        text(
            """
            ALTER TABLE vulnerabilities
            MODIFY COLUMN created_at DATETIME NOT NULL
            """
        )
    )

    connection.execute(
        text(
            """
            ALTER TABLE vulnerabilities
            MODIFY COLUMN updated_at DATETIME NOT NULL
            """
        )
    )

    foreign_keys = inspect(engine).get_foreign_keys("vulnerabilities")

    has_researcher_foreign_key = any(
        key.get("referred_table") == "researchers"
        for key in foreign_keys
    )

    if not has_researcher_foreign_key:
        connection.execute(
            text(
                """
                ALTER TABLE vulnerabilities
                ADD CONSTRAINT fk_vulnerabilities_researcher
                FOREIGN KEY (researcher_id)
                REFERENCES researchers(id)
                ON DELETE RESTRICT
                """
            )
        )

print("HW5 database migration completed successfully.")