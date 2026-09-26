"""
HW4 - Creates all tables (vulnerabilities, advisories, users, sessions)
in the s2604_rel MySQL database, based on the models in models.py.

Run once: python src/create_tables.py
"""

from db import Base, engine
import models  # noqa: F401 -- import registers the model classes with Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully in s2604_rel.")
