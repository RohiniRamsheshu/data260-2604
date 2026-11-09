import json
from pathlib import Path

from self_improving_agents import (
    answer_agent,
    evaluator_agent,
    load_lessons,
    save_lesson,
)


def evaluate_answer(case, answer):
    return evaluator_agent(
        question=case["question"],
        context=case["context"],
        answer=answer,
    )


def baseline(case):
    answer = answer_agent(
        question=case["question"],
        context=case["context"],
    )

    evaluation = evaluate_answer(case, answer)

    return {
        "answer": answer,
        "decision": evaluation.get("decision"),
        "attempts": 1,
    }


def evaluator_repair(case):
    answer = answer_agent(
        question=case["question"],
        context=case["context"],
    )

    evaluation = evaluate_answer(case, answer)
    attempts = 1

    if evaluation.get("decision") == "REVISE":
        answer = answer_agent(
            question=case["question"],
            context=case["context"],
            feedback=evaluation.get("feedback", ""),
        )
        evaluation = evaluate_answer(case, answer)
        attempts = 2

    return {
        "answer": answer,
        "decision": evaluation.get("decision"),
        "attempts": attempts,
    }


def lesson_memory(case):
    lessons = load_lessons()

    answer = answer_agent(
        question=case["question"],
        context=case["context"],
        lessons=lessons,
    )

    evaluation = evaluate_answer(case, answer)

    return {
        "answer": answer,
        "decision": evaluation.get("decision"),
        "attempts": 1,
        "lessons_used": len(lessons),
    }


def validated_improvement(case):
    result = evaluator_repair(case)

    if (
        result["attempts"] == 2
        and result["decision"] == "PASS"
    ):
        save_lesson(
            failure_pattern="Initial answer required correction",
            correction=(
                "Use the provided context and apply evaluator feedback "
                "before finalizing the answer."
            ),
        )

    return result


def summarize(results):
    passed = sum(
        1 for result in results
        if result["decision"] == "PASS"
    )

    total_attempts = sum(
        result["attempts"]
        for result in results
    )

    return {
        "cases": len(results),
        "passed": passed,
        "pass_rate": round(passed / len(results), 4),
        "average_attempts": round(
            total_attempts / len(results),
            2,
        ),
    }


def main():
    with open("test_data.json", "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    variants = {
        "baseline": baseline,
        "evaluator_repair": evaluator_repair,
        "lesson_memory": lesson_memory,
        "validated_improvement": validated_improvement,
    }

    report = {}

    for name, function in variants.items():
        print(f"\n=== {name} ===")

        results = []

        for case in test_cases:
            result = function(case)
            results.append(result)

            print(
                f"decision={result['decision']} | "
                f"attempts={result['attempts']}"
            )

        report[name] = summarize(results)
        print(json.dumps(report[name], indent=2))

    output_path = Path(
        "reports/hw09/raw/part4-variant-comparison.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()