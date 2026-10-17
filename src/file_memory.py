from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

AGENT_PATH = PROJECT_ROOT / "AGENT.md"
MEMORY_PATH = PROJECT_ROOT / "MEMORY_CONSOLIDATED.md"
ORIGINAL_MEMORY_PATH = PROJECT_ROOT / "MEMORY.md"


def read_memory_file(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8").strip()


def count_memory_lines(path: Path) -> int:
    text = read_memory_file(path)

    return sum(
        1
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def should_compact(path: Path) -> bool:
    if not path.exists():
        return False

    too_many_lines = count_memory_lines(path) > 40

    modified_at = datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    )

    older_than_one_day = (
        datetime.now(timezone.utc) - modified_at
        > timedelta(hours=24)
    )

    return too_many_lines or older_than_one_day


def load_file_memory() -> dict[str, str | int | bool]:
    agent_instructions = read_memory_file(AGENT_PATH)
    consolidated_memory = read_memory_file(MEMORY_PATH)

    return {
        "agent_instructions": agent_instructions,
        "memory": consolidated_memory,
        "memory_line_count": count_memory_lines(MEMORY_PATH),
        "needs_compaction": should_compact(MEMORY_PATH),
    }


def build_file_memory_prompt() -> str:
    file_memory = load_file_memory()

    return f"""
Assistant instructions:
{file_memory["agent_instructions"]}

Durable file memory:
{file_memory["memory"]}
""".strip()