import json


FIXTURE_RECORDS = [
    {
        "id": 5005,
        "package_name": "package_1",
        "cve_id": "CVE-2026-1001",
        "severity": 5,
        "researcher_id": 1,
    },
    {
        "id": 5006,
        "package_name": "package_33",
        "cve_id": "CVE-2026-1002",
        "severity": 8,
        "researcher_id": 1,
    },
    {
        "id": 5007,
        "package_name": "package_safe",
        "cve_id": "CVE-2026-1003",
        "severity": 2,
        "researcher_id": 2,
    },
]


def success(data):
    return {
        "ok": True,
        "data": data,
        "error": None,
    }


def failure(message):
    return {
        "ok": False,
        "data": None,
        "error": message,
    }


def search_vulnerabilities(inputs, records):
    query = inputs.get("query")
    limit = inputs.get("limit", 10)

    if not isinstance(query, str) or not query.strip():
        return failure("query must not be empty")

    if not isinstance(limit, int) or limit < 1 or limit > 50:
        return failure("limit must be between 1 and 50")

    query = query.lower().strip()

    matches = [
        row
        for row in records
        if query in row["package_name"].lower()
        or query in row["cve_id"].lower()
    ]

    return success(matches[:limit])


def vulnerability_detail(inputs, records):
    vulnerability_id = inputs.get("vulnerability_id")

    if not isinstance(vulnerability_id, int) or vulnerability_id <= 0:
        return failure("vulnerability_id must be positive")

    for row in records:
        if row["id"] == vulnerability_id:
            return success(row)

    return failure("vulnerability was not found")


def vulnerability_summary(inputs, records):
    min_severity = inputs.get("min_severity", 0)

    if (
        not isinstance(min_severity, int)
        or min_severity < 0
        or min_severity > 10
    ):
        return failure("min_severity must be between 0 and 10")

    filtered = [
        row for row in records
        if row["severity"] >= min_severity
    ]

    by_severity = {}

    for row in filtered:
        severity = str(row["severity"])
        by_severity[severity] = by_severity.get(severity, 0) + 1

    return success(
        {
            "total_vulnerabilities": len(filtered),
            "by_severity": by_severity,
        }
    )


def execute_tool(name, inputs, records=None):
    """Safely execute one of the three domain tools."""

    if records is None:
        records = FIXTURE_RECORDS

    if not isinstance(inputs, dict):
        return json.dumps(failure("inputs must be a JSON object"))

    # Safety rule:
    # High-severity vulnerability details require explicit approval.
    if name == "vulnerability_detail":
        requested_id = inputs.get("vulnerability_id")

        for row in records:
            if row["id"] == requested_id and row["severity"] >= 8:
                if inputs.get("approved") is not True:
                    return json.dumps(
                        failure(
                            "safety rule blocked high-severity "
                            "vulnerability details"
                        )
                    )

    if name == "search_vulnerabilities":
        output = search_vulnerabilities(inputs, records)
    elif name == "vulnerability_detail":
        output = vulnerability_detail(inputs, records)
    elif name == "vulnerability_summary":
        output = vulnerability_summary(inputs, records)
    else:
        output = failure(f"unknown tool: {name}")

    return json.dumps(output)


if __name__ == "__main__":
    print(
        execute_tool(
            "search_vulnerabilities",
            {"query": "CVE"},
        )
    )