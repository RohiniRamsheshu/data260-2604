import json
import urllib.request
from datetime import datetime
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
LESSONS_FILE = Path("lessons.json")


def call_ollama(prompt):
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

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("response", "").strip()


def answer_agent(question, context, feedback="", lessons=None):
    lessons = lessons or []

    lesson_text = "\n".join(
        f"- {lesson['correction']}"
        for lesson in lessons
    )

    prompt = f"""
You are the Answering Agent.

Answer the question using only the provided context.
Be concise and factual.
Do not invent information.

Question:
{question}

Context:
{context}

Evaluator feedback:
{feedback or "None"}

Reusable lessons:
{lesson_text or "None"}

Answer:
"""

    return call_ollama(prompt)


def evaluator_agent(question, context, answer):
    prompt = f"""
You are the Evaluator Agent.

Check whether the answer is correct using the context.
Return ONLY valid JSON with these keys:
- decision: PASS or REVISE
- explanation: short reason
- feedback: correction instructions

Question:
{question}

Context:
{context}

Answer:
{answer}
"""

    raw_output = call_ollama(prompt)

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "decision": "REVISE",
            "explanation": "Evaluator output was not valid JSON.",
            "feedback": "Return a concise answer based only on the context.",
        }


def load_lessons():
    if not LESSONS_FILE.exists():
        return []

    with open(LESSONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_lesson(failure_pattern, correction):
    lessons = load_lessons()

    for lesson in lessons:
        if lesson["failure_pattern"] == failure_pattern:
            lesson["use_count"] += 1
            break
    else:
        lessons.append(
            {
                "lesson_id": f"lesson_{len(lessons) + 1:03d}",
                "failure_pattern": failure_pattern,
                "correction": correction,
                "created_at": datetime.utcnow().isoformat(),
                "use_count": 1,
            }
        )

    with open(LESSONS_FILE, "w", encoding="utf-8") as file:
        json.dump(lessons, file, indent=2)


def run_case(case):
    lessons = load_lessons()

    answer = answer_agent(
        question=case["question"],
        context=case["context"],
        lessons=lessons,
    )

    attempts = 1
    evaluation = evaluator_agent(
        question=case["question"],
        context=case["context"],
        answer=answer,
    )

    if evaluation.get("decision") == "REVISE":
        attempts += 1

        answer = answer_agent(
            question=case["question"],
            context=case["context"],
            feedback=evaluation.get("feedback", ""),
            lessons=lessons,
        )

        evaluation = evaluator_agent(
            question=case["question"],
            context=case["context"],
            answer=answer,
        )

        save_lesson(
            failure_pattern=evaluation.get(
                "explanation",
                "Answer required evaluator revision",
            ),
            correction=evaluation.get(
                "feedback",
                "Use only facts supported by the context.",
            ),
        )

    return {
        "question": case["question"],
        "answer": answer,
        "decision": evaluation.get("decision"),
        "explanation": evaluation.get("explanation"),
        "attempts": attempts,
    }


def main():
    with open("test_data.json", "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    results = []

    for number, case in enumerate(test_cases, start=1):
        print(f"\n=== Test Case {number} ===")
        result = run_case(case)
        results.append(result)

        print("Question:", result["question"])
        print("Answer:", result["answer"])
        print("Decision:", result["decision"])
        print("Attempts:", result["attempts"])

    output_path = Path(
        "reports/hw09/raw/self-improving-agent-results.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"\nWrote {output_path}")
    print(f"Lessons saved to: {LESSONS_FILE}")
    save_lesson(
    failure_pattern="Answer does not use the provided context",
    correction="Use only facts directly supported by the context.",
)

print("Lessons saved to:", LESSONS_FILE)
print(json.dumps(load_lessons(), indent=2))


if __name__ == "__main__":
    main()