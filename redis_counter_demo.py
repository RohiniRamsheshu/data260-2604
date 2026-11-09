from src.db import db_session_basede26
from src.models import Vulnerability
from src.redis_counter import VulnerabilityViewCounter


def main():
    lookup_db = db_session_basede26()
    vulnerability = lookup_db.query(Vulnerability).first()

    if vulnerability is None:
        raise RuntimeError(
            "No vulnerability record exists in MySQL"
        )

    vulnerability_id = vulnerability.id
    lookup_db.close()

    counter = VulnerabilityViewCounter()

    redis_key = (
        f"s2604:views:vulnerability:{vulnerability_id}"
    )
    counter.redis_client.delete(redis_key)

    print("=== Testing Counter ===")
    print(f"Vulnerability ID: {vulnerability_id}")

    for access_number in range(1, 26):
        total = counter.increment_vulnerability_views(
            vulnerability_id
        )
        print(
            f"Access #{access_number}: Total = {total}"
        )

    check_db = db_session_basede26()
    updated = check_db.get(
        Vulnerability,
        vulnerability_id,
    )

    print(
        f"Database view_count after 25 accesses: "
        f"{updated.view_count}"
    )

    check_db.close()
    counter.close()


if __name__ == "__main__":
    main()