import yaml


cases = []

for number in range(1, 11):
    cases.append(
        {
            "case_id": f"exact_{number:02d}",
            "category": "exact_duplicate",
            "cached_query": (
                "What is the severity of CVE-2026-1001?"
            ),
            "query": (
                "What is the severity of CVE-2026-1001?"
            ),
            "should_hit": True,
        }
    )

paraphrases = [
    "How severe is CVE-2026-1001?",
    "Tell me the severity for CVE-2026-1001.",
    "What severity does CVE-2026-1001 have?",
    "Can you give the severity of CVE-2026-1001?",
    "Report the severity level of CVE-2026-1001.",
    "Which severity is assigned to CVE-2026-1001?",
    "How serious is CVE-2026-1001?",
    "What is the CVE-2026-1001 severity rating?",
    "Give me the risk severity for CVE-2026-1001.",
    "What severity value belongs to CVE-2026-1001?",
]

for number, query in enumerate(paraphrases, start=1):
    cases.append(
        {
            "case_id": f"paraphrase_{number:02d}",
            "category": "paraphrase",
            "cached_query": (
                "What is the severity of CVE-2026-1001?"
            ),
            "query": query,
            "should_hit": True,
        }
    )

for number in range(1, 11):
    cases.append(
        {
            "case_id": f"similar_miss_{number:02d}",
            "category": "similar_different_answer",
            "cached_query": (
                "What is the severity of CVE-2026-1001?"
            ),
            "query": (
                "What is the severity of CVE-2026-1002?"
            ),
            "should_hit": False,
        }
    )

unrelated = [
    "How does Kafka use consumer groups?",
    "What is a Redis key?",
    "What is a UUID?",
    "Explain database normalization.",
    "What is a Python decorator?",
    "How does Docker isolate processes?",
    "What is cosine similarity?",
    "Explain an HTTP status code.",
    "What is a database index?",
    "How does a message queue work?",
]

for number, query in enumerate(unrelated, start=1):
    cases.append(
        {
            "case_id": f"unrelated_{number:02d}",
            "category": "unrelated",
            "cached_query": (
                "What is the severity of CVE-2026-1001?"
            ),
            "query": query,
            "should_hit": False,
        }
    )

with open("cache_cases.yaml", "w", encoding="utf-8") as file:
    yaml.safe_dump(cases, file, sort_keys=False)

print(f"Wrote {len(cases)} labeled cases")