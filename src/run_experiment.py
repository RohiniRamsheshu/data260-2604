from langchain_ollama import ChatOllama
import json
import time
import csv

with open("reports/hw01/cases/nondeterminism_input.json") as f:
    case = json.load(f)

title = case["title"]
content = case["content"]

def run_once(temperature):
    llm = ChatOllama(model="qwen2.5:3b", temperature=temperature)
    prompt = f"""Given a title and content, respond ONLY in valid JSON with keys "tags" (list of exactly 3 strings) and "summary" (string, max 25 words).

Title: {title}
Content: {content}
"""
    start = time.time()
    response = llm.invoke(prompt)
    latency_ms = (time.time() - start) * 1000

    try:
        parsed = json.loads(response.content)
        tags = parsed.get("tags", [])
    except json.JSONDecodeError:
        tags = []

    return tags, latency_ms

results = []

for temp in [0.7, 0.0]:
    print(f"\n=== Running 20 iterations at temperature {temp} ===")
    for i in range(20):
        tags, latency_ms = run_once(temp)
        results.append({
            "temperature": temp,
            "run": i + 1,
            "tags": json.dumps(tags),
            "latency_ms": round(latency_ms, 2)
        })
        print(f"Run {i+1}: tags={tags}, latency={latency_ms:.0f}ms")

with open("reports/hw01/raw/nondeterminism_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["temperature", "run", "tags", "latency_ms"])
    writer.writeheader()
    writer.writerows(results)

print("\nDone. Results saved to reports/hw01/raw/nondeterminism_results.csv")