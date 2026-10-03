import random
import string
from sqlalchemy.orm import Session
from src.db import db_session_basede26, engine, Base
from src.models import Vulnerability, Advisory

SEED_VAL = 2604
random.seed(SEED_VAL)

def seed_database():
    db: Session = db_session_basede26()
    try:
        print("Clearing existing advisories and vulnerabilities...")
        db.query(Advisory).delete()
        db.query(Vulnerability).delete()
        db.commit()

        print("Seeding 5,000 Vulnerabilities...")
        vulnerabilities = []
        for i in range(1, 5001):
            vuln = Vulnerability(
                package_name=f"package_{random.randint(1, 100)}",
                cve_id=f"CVE-2026-{1000 + i}"
            )
            vulnerabilities.append(vuln)
        
        db.add_all(vulnerabilities)
        db.commit()

        print("Seeding 200 Advisories linked to vulnerabilities...")
        vuln_ids = [v.id for v in db.query(Vulnerability.id).all()]
        advisories = []
        for i in range(1, 201):
            adv = Advisory(
                vulnerability_id=random.choice(vuln_ids),
                note=f"Security advisory #{i}: Patch available for affected package."
            )
            advisories.append(adv)

        db.add_all(advisories)
        db.commit()
        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()