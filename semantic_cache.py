import hashlib
import json
import math
import time
import uuid

import redis


PREFIX = "s2604"
CACHE_INDEX_KEY = f"{PREFIX}:semantic-cache:index"
SIMILARITY_THRESHOLD = 0.85


class SemanticCache:
    def __init__(self):
        self.redis = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )

    def make_embedding(self, text, size=64):
        vector = [0.0] * size

        for word in text.lower().split():
            digest = hashlib.sha256(
                word.encode("utf-8")
            ).hexdigest()

            index = int(digest, 16) % size
            vector[index] += 1.0

        magnitude = math.sqrt(
            sum(value * value for value in vector)
        )

        if magnitude == 0:
            return vector

        return [
            value / magnitude
            for value in vector
        ]

    def cosine_similarity(self, first, second):
        numerator = sum(
            left * right
            for left, right in zip(first, second)
        )

        left_norm = math.sqrt(
            sum(value * value for value in first)
        )
        right_norm = math.sqrt(
            sum(value * value for value in second)
        )

        if left_norm == 0 or right_norm == 0:
            return 0.0

        return numerator / (left_norm * right_norm)

    def store(
        self,
        query,
        answer,
        data_version="v1",
    ):
        cache_id = str(uuid.uuid4())
        key = f"{PREFIX}:semantic-cache:{cache_id}"

        record = {
            "query": query,
            "embedding": self.make_embedding(query),
            "answer": answer,
            "data_version": data_version,
            "created_at": time.time(),
        }

        self.redis.set(
            key,
            json.dumps(record),
        )
        self.redis.sadd(
            CACHE_INDEX_KEY,
            key,
        )

        return cache_id

    def lookup(
        self,
        query,
        threshold=SIMILARITY_THRESHOLD,
        data_version="v1",
    ):
        query_embedding = self.make_embedding(query)
        best_match = None
        best_score = 0.0

        keys = self.redis.smembers(
            CACHE_INDEX_KEY
        )

        for key in keys:
            raw_record = self.redis.get(key)

            if raw_record is None:
                continue

            record = json.loads(raw_record)

            if record["data_version"] != data_version:
                continue

            score = self.cosine_similarity(
                query_embedding,
                record["embedding"],
            )

            if score > best_score:
                best_score = score
                best_match = record

        if best_match is not None and best_score >= threshold:
            return {
                "is_cached": True,
                "similarity": best_score,
                "answer": best_match["answer"],
                "query": best_match["query"],
                "latency_ms": 0.0,
            }

        return {
            "is_cached": False,
            "similarity": best_score,
            "answer": None,
            "query": None,
            "latency_ms": 0.0,
        }