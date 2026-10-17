import json
import urllib.request
import urllib.error
import hashlib
import math

from src.file_memory import (
    build_file_memory_prompt,
    load_file_memory,
)

from src.file_memory import build_file_memory_prompt

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.memory_store import (
    save_message,
    get_recent_messages,
    get_latest_summary,
)

from datetime import datetime

from src.mongo_db import (
    messages_collection,
    summaries_collection,
    episodes_collection,
)
from src.memory_store import get_recent_episodes
from src.memory_store import (
    save_message,
    get_recent_messages,
    get_latest_summary,
    save_summary,
    save_episode,
    count_user_messages,
)
from src.memory_store import (
    save_message,
    get_recent_messages,
    get_latest_summary,
    save_summary,
    save_episode,
    count_user_messages,
    get_top_episodes,
)
router = APIRouter(prefix="/api", tags=["Chat Memory"])

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)


def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

            print(
                "Ollama response length:",
                len(data.get("response", "")),
            )

            return data.get("response", "").strip()

    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is unavailable: {exc}",
        )


def build_prompt(
    recent_messages: list[dict],
    summary: dict | None,
    episodes: list[dict],
) -> str:
    file_memory_context = build_file_memory_prompt()

    lines = [
        file_memory_context,
        "",
        "Use the conversation memory below to answer the user.",
        "",
    ]

    if summary:
        lines.append(f"Summary: {summary.get('text', '')}")
        lines.append("")

    if episodes:
        lines.append("Relevant durable facts:")

        for episode in episodes:
            lines.append(f"- {episode.get('fact', '')}")

        lines.append("")

    lines.append("Recent conversation:")

    for message in recent_messages:
        role = message.get("role", "user").capitalize()
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    lines.append("")
    lines.append("Assistant:")

    return "\n".join(lines)

def make_embedding(text: str, size: int = 8) -> list[float]:
    vector = [0.0] * size

    for word in text.lower().split():
        digest = hashlib.sha256(word.encode("utf-8")).hexdigest()
        index = int(digest, 16) % size
        vector[index] += 1.0

    magnitude = math.sqrt(sum(value * value for value in vector))

    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]


def create_memory_summary(
    user_id: str,
    session_id: str,
    messages: list[dict],
) -> str:
    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )

    summary_prompt = f"""
Summarize this conversation in two concise sentences.
Keep important topics and facts.

Conversation:
{conversation}
"""

    return call_ollama(summary_prompt)


@router.post("/chat")
def chat(request: ChatRequest):
    command = request.message.strip().lower()

    if command == "/memory":
        file_memory = load_file_memory()

        return {
            "command": "/memory",
            "memory_line_count": file_memory["memory_line_count"],
            "needs_compaction": file_memory["needs_compaction"],
            "agent_loaded": bool(
                file_memory["agent_instructions"]
            ),
            "memory_loaded": bool(
                file_memory["memory"]
            ),
        }

    if command == "/compact":
        file_memory = load_file_memory()

        return {
            "command": "/compact",
            "message": (
                "Memory is already consolidated."
                if not file_memory["needs_compaction"]
                else "Memory needs consolidation."
            ),
            "memory_line_count": file_memory["memory_line_count"],
            "needs_compaction": file_memory["needs_compaction"],
        }

    if command == "/dream":
        return {
            "command": "/dream",
            "message": (
                "Dream mode reviews recent conversation "
                "for possible durable facts."
            ),
            "status": "ready",
        }

    if command == "/help":
        return {
            "command": "/help",
            "commands": [
                "/memory",
                "/compact",
                "/dream",
                "/help",
            ],
        }
    save_message(
        user_id=request.user_id,
        session_id=request.session_id,
        role="user",
        content=request.message,
    )

    recent_messages = get_recent_messages(
        user_id=request.user_id,
        session_id=request.session_id,
        limit=4,
    )

    latest_summary = get_latest_summary(
        user_id=request.user_id,
        session_id=request.session_id,
    )
    query_embedding = make_embedding(request.message)

    top_episodes = get_top_episodes(
        user_id=request.user_id,
        query_embedding=query_embedding,
        limit=3,
    )

    prompt = build_prompt(recent_messages,
        latest_summary,
        top_episodes,)
    reply = call_ollama(prompt)

    save_message(
        user_id=request.user_id,
        session_id=request.session_id,
        role="assistant",
        content=reply,
    )
    user_message_count = count_user_messages(
        user_id=request.user_id,
        session_id=request.session_id,
    )

    summary_created = False
    episode_created = False

    if user_message_count % 5 == 0:
        summary_text = create_memory_summary(
            user_id=request.user_id,
            session_id=request.session_id,
            messages=get_recent_messages(
                user_id=request.user_id,
                session_id=request.session_id,
                limit=16,
            ),
        )

        save_summary(
            user_id=request.user_id,
            session_id=request.session_id,
            scope="session",
            text=summary_text,
        )

        save_episode(
            user_id=request.user_id,
            session_id=request.session_id,
            fact=request.message,
            importance=0.5,
            embedding=make_embedding(request.message),
        )

        summary_created = True
        episode_created = True

    return {
        "reply": reply,
        "used_memory": {
            "recent_message_count": len(recent_messages),
            "summary_used": latest_summary is not None,
            "summary_created": summary_created,
            "episode_created": episode_created,
            "episodic_memory_count": len(top_episodes),
            "model": OLLAMA_MODEL,
        },
    }
def serialize_memory_document(document: dict) -> dict:
    result = dict(document)

    if "_id" in result:
        result["id"] = str(result.pop("_id"))

    for field, value in result.items():
        if isinstance(value, datetime):
            result[field] = value.isoformat()

    return result


@router.get("/memory/{user_id}")
def get_memory(user_id: str):
    messages = list(
        messages_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(16)
    )
    messages.reverse()

    summaries = list(
        summaries_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(10)
    )

    episodes = get_recent_episodes(user_id=user_id, limit=20)

    return {
        "user_id": user_id,
        "messages": [
            serialize_memory_document(message)
            for message in messages
        ],
        "summaries": [
            serialize_memory_document(summary)
            for summary in summaries
        ],
        "episodes": [
            serialize_memory_document(episode)
            for episode in episodes
        ],
    }


@router.get("/aggregate/{user_id}")
def get_aggregate(user_id: str):
    messages = list(
        messages_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
    )

    daily_counts: dict[str, int] = {}

    for message in messages:
        created_at = message.get("created_at")

        if isinstance(created_at, datetime):
            day = created_at.date().isoformat()
        else:
            day = "unknown"

        daily_counts[day] = daily_counts.get(day, 0) + 1

    recent_summaries = list(
        summaries_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(5)
    )

    return {
        "user_id": user_id,
        "total_messages": len(messages),
        "daily_message_counts": daily_counts,
        "recent_summaries": [
            serialize_memory_document(summary)
            for summary in recent_summaries
        ],
    }