from datetime import datetime, timezone
from typing import Any
import math

from src.mongo_db import (
    messages_collection,
    summaries_collection,
    episodes_collection,
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def save_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
) -> dict[str, Any]:
    message = {
        "user_id": user_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": now_utc(),
    }

    result = messages_collection.insert_one(message)
    message["_id"] = result.inserted_id
    return message


def get_recent_messages(
    user_id: str,
    session_id: str,
    limit: int = 4,
) -> list[dict[str, Any]]:
    cursor = (
        messages_collection
        .find(
            {
                "user_id": user_id,
                "session_id": session_id,
            }
        )
        .sort("created_at", -1)
        .limit(limit)
    )

    messages = list(cursor)
    messages.reverse()
    return messages


def save_summary(
    user_id: str,
    session_id: str | None,
    scope: str,
    text: str,
) -> dict[str, Any]:
    summary = {
        "user_id": user_id,
        "session_id": session_id,
        "scope": scope,
        "text": text,
        "created_at": now_utc(),
    }

    result = summaries_collection.insert_one(summary)
    summary["_id"] = result.inserted_id
    return summary


def get_latest_summary(
    user_id: str,
    session_id: str,
) -> dict[str, Any] | None:
    return summaries_collection.find_one(
        {
            "user_id": user_id,
            "$or": [
                {"scope": "session", "session_id": session_id},
                {"scope": "user", "session_id": None},
            ],
        },
        sort=[("created_at", -1)],
    )


def save_episode(
    user_id: str,
    session_id: str,
    fact: str,
    importance: float,
    embedding: list[float],
) -> dict[str, Any]:
    episode = {
        "user_id": user_id,
        "session_id": session_id,
        "fact": fact,
        "importance": importance,
        "embedding": embedding,
        "created_at": now_utc(),
    }

    result = episodes_collection.insert_one(episode)
    episode["_id"] = result.inserted_id
    return episode


def get_recent_episodes(
    user_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    return list(
        episodes_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
def count_user_messages(
    user_id: str,
    session_id: str,
) -> int:
    return messages_collection.count_documents(
        {
            "user_id": user_id,
            "session_id": session_id,
            "role": "user",
        }
    )
def cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:
    numerator = sum(a * b for a, b in zip(first, second))

    first_length = math.sqrt(sum(value * value for value in first))
    second_length = math.sqrt(sum(value * value for value in second))

    if first_length == 0 or second_length == 0:
        return 0.0

    return numerator / (first_length * second_length)


def get_top_episodes(
    user_id: str,
    query_embedding: list[float],
    limit: int = 3,
) -> list[dict]:
    episodes = list(
        episodes_collection.find({"user_id": user_id})
    )

    scored_episodes = []

    for episode in episodes:
        score = cosine_similarity(
            query_embedding,
            episode.get("embedding", []),
        )

        episode_copy = dict(episode)
        episode_copy["similarity"] = score
        scored_episodes.append(episode_copy)

    scored_episodes.sort(
        key=lambda episode: episode["similarity"],
        reverse=True,
    )

    return scored_episodes[:limit]