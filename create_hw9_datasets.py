import json


training_data = [
    {
        "question": "What is the severity of CVE-2026-1001?",
        "context": "CVE-2026-1001 affects package_1 and has severity 5.",
    },
    {
        "question": "Which package is affected by CVE-2026-1002?",
        "context": "CVE-2026-1002 affects package_33 and has severity 8.",
    },
    {
        "question": "What does Redis INCR do?",
        "context": "Redis INCR atomically increases an integer value.",
    },
]


validation_data = [
    {
        "question": "How serious is CVE-2026-1001?",
        "context": "CVE-2026-1001 affects package_1 and has severity 5.",
    },
    {
        "question": "What severity belongs to CVE-2026-1002?",
        "context": "CVE-2026-1002 affects package_33 and has severity 8.",
    },
]


test_data = [
    {
        "question": "Tell me the risk level for CVE-2026-1001.",
        "context": "CVE-2026-1001 affects package_1 and has severity 5.",
    },
    {
        "question": "Which package has CVE-2026-1002?",
        "context": "CVE-2026-1002 affects package_33 and has severity 8.",
    },
]


for filename, data in [
    ("training_data.json", training_data),
    ("validation_data.json", validation_data),
    ("test_data.json", test_data),
]:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Wrote {filename}: {len(data)} records")