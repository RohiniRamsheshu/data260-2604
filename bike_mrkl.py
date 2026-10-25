import ast
import csv
import hashlib
import json
import operator
import sqlite3
from datetime import date
from pathlib import Path


RAW_DIR = Path("reports/hw07/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = RAW_DIR / "bike_trips.csv"
PRICING_PATH = RAW_DIR / "pricing_snapshot.txt"


def create_csv():
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["trip_id", "city", "member_type", "duration_min"],
        )
        writer.writeheader()

        for trip_id in range(1, 601):
            writer.writerow(
                {
                    "trip_id": trip_id,
                    "city": "San Francisco",
                    "member_type": "casual",
                    "duration_min": 20 + trip_id % 25,
                }
            )


def create_pricing_snapshot():
    text = """Bay Wheels pricing snapshot
Membership: $15 per month
Pay-per-use: $3.50 per ride
Source: https://www.baywheels.com/pricing
Snapshot date: 2026-10-24
"""
    PRICING_PATH.write_text(text, encoding="utf-8")

    return {
        "url": "https://www.baywheels.com/pricing",
        "date": "2026-10-24",
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "text": text,
    }


def csv_sql(query):
    """Read-only SQL tool."""
    normalized = query.strip().lower()

    if not normalized.startswith("select"):
        raise ValueError("Only SELECT statements are allowed")

    blocked = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "pragma",
    ]

    if any(word in normalized for word in blocked):
        raise ValueError("Read-only SQL policy blocked this query")

    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE trips "
        "(trip_id INTEGER, city TEXT, member_type TEXT, duration_min INTEGER)"
    )

    with CSV_PATH.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    connection.executemany(
        "INSERT INTO trips VALUES (?, ?, ?, ?)",
        [
            (
                row["trip_id"],
                row["city"],
                row["member_type"],
                row["duration_min"],
            )
            for row in rows
        ],
    )

    cursor = connection.execute(query)
    return cursor.fetchall()


def policy_retriever():
    snapshot = create_pricing_snapshot()

    return {
        "membership_monthly": 15.0,
        "pay_per_ride": 3.50,
        "citation": snapshot,
    }


def calculator(expression):
    """Safe arithmetic calculator; no names, calls, or attributes allowed."""
    allowed = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)
        ):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in allowed:
            return allowed[type(node.op)](
                evaluate(node.left),
                evaluate(node.right),
            )

        raise ValueError("Unsafe calculator expression")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)


def run_scenario(name, rides):
    policy = policy_retriever()

    timeline = [
        "csv_sql: inspect uploaded trip data",
        "policy_retriever: retrieve pricing snapshot",
        "calculator: compare membership and pay-per-use",
    ]

    csv_sql(
        "SELECT trip_id, duration_min FROM trips "
        "WHERE city = 'San Francisco' LIMIT 500"
    )

    membership_cost = calculator(
        f"{policy['membership_monthly']} + 0"
    )
    pay_cost = calculator(
        f"{rides} * {policy['pay_per_ride']}"
    )

    recommendation = (
        "membership wins"
        if membership_cost < pay_cost
        else "pay-per-use wins"
    )

    return {
        "scenario": name,
        "rides": rides,
        "membership_cost": membership_cost,
        "pay_per_use_cost": pay_cost,
        "recommendation": recommendation,
        "timeline": timeline,
        "citations": [policy["citation"]],
        "assumptions": [
            "All rides occur in one month",
            "Each ride is priced at the snapshot pay-per-use rate",
            "Membership cost is treated as a fixed monthly cost",
        ],
    }


def main():
    create_csv()

    results = [
        run_scenario("frequent rider", rides=10),
        run_scenario("occasional rider", rides=2),
    ]

    output = {
        "csv_rows": 600,
        "results": results,
    }

    output_path = RAW_DIR / "bike-mrkl-results.json"
    output_path.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(output, indent=2))
    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()