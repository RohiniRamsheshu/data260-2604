import csv
import json
import time
import urllib.request
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

messages = [
    {
        "role": "user" if index % 2 == 0 else "assistant",
        "content": f"Conversation message number {index + 1} about MongoDB memory.",
    }
    for index in range(30)
]


def estimate_tokens(text: str) -> int:
    return len(text.split())


def build_prompt(memory_size: int) -> str:
    selected_messages = messages[-memory_size:]

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in selected_messages
    )

    return f"""
You are a helpful assistant studying conversation memory.

Recent conversation:
{conversation}

Answer this question briefly:
Why is memory size important in an AI chat system?
"""


def call_ollama(prompt: str) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    elapsed_ms = (time.perf_counter() - start) * 1000
    return result.get("response", ""), elapsed_ms


def main():
    results = []

    for memory_size in [4, 12, 30]:
        prompt = build_prompt(memory_size)
        reply, latency_ms = call_ollama(prompt)

        results.append(
            {
                "memory_size": memory_size,
                "prompt_tokens": estimate_tokens(prompt),
                "completion_tokens": estimate_tokens(reply),
                "latency_ms": round(latency_ms, 2),
                "reply_preview": reply[:120],
            }
        )

        print(
            f"N={memory_size} | "
            f"prompt_tokens={results[-1]['prompt_tokens']} | "
            f"latency_ms={results[-1]['latency_ms']}"
        )

    output_dir = Path("reports/hw06/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "memory-cost-results.json"
    csv_path = output_dir / "memory-cost-results.csv"

    json_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "memory_size",
                "prompt_tokens",
                "completion_tokens",
                "latency_ms",
                "reply_preview",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nWrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()