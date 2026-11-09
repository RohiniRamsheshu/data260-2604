import redis

from src.db import db_session_basede26
from src.models import Vulnerability


REDIS_HOST = "localhost"
REDIS_PORT = 6379
PREFIX = "s2604"


class VulnerabilityViewCounter:
    def __init__(self, db_session=None):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
        )
        self.db = db_session or db_session_basede26()

    def increment_vulnerability_views(self, vulnerability_id):
        key = f"{PREFIX}:views:vulnerability:{vulnerability_id}"

        count = self.redis_client.incr(key)

        if count % 10 == 0:
            vulnerability = self.db.get(
                Vulnerability,
                vulnerability_id,
            )

            if vulnerability is None:
                raise ValueError("Vulnerability not found")

            vulnerability.view_count = count
            self.db.commit()

            print(
                f"Synced views to database: "
                f"vulnerability={vulnerability_id}, "
                f"count={count}"
            )

        return count

    def close(self):
        self.db.close()
