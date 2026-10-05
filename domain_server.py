import sys
from collections import Counter

from mcp.server.fastmcp import FastMCP

from src.db import db_session_basede26
from src.models import Vulnerability


mcp = FastMCP("Vulnerability Domain Server")


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


def vulnerability_to_dict(item):
    return {
        "id": item.id,
        "package_name": item.package_name,
        "cve_id": item.cve_id,
        "severity": item.severity,
        "researcher_id": item.researcher_id,
    }


@mcp.tool()
def search_vulnerabilities(query: str, limit: int = 10):
    """Search vulnerabilities by package name or CVE ID."""

    if not query or not query.strip():
        return failure("query must not be empty")

    if limit < 1 or limit > 50:
        return failure("limit must be between 1 and 50")

    db = db_session_basede26()

    try:
        pattern = f"%{query.strip()}%"

        rows = (
            db.query(Vulnerability)
            .filter(
                (Vulnerability.package_name.ilike(pattern))
                | (Vulnerability.cve_id.ilike(pattern))
            )
            .limit(limit)
            .all()
        )

        return success([vulnerability_to_dict(row) for row in rows])

    except Exception as exc:
        print(f"search error: {exc}", file=sys.stderr)
        return failure("database search failed")

    finally:
        db.close()


@mcp.tool()
def vulnerability_detail(vulnerability_id: int):
    """Return one vulnerability by numeric ID."""

    if vulnerability_id <= 0:
        return failure("vulnerability_id must be positive")

    db = db_session_basede26()

    try:
        row = (
            db.query(Vulnerability)
            .filter(Vulnerability.id == vulnerability_id)
            .first()
        )

        if row is None:
            return failure("vulnerability was not found")

        return success(vulnerability_to_dict(row))

    except Exception as exc:
        print(f"detail error: {exc}", file=sys.stderr)
        return failure("database lookup failed")

    finally:
        db.close()


@mcp.tool()
def vulnerability_summary(min_severity: int = 0):
    """Return aggregate statistics for vulnerabilities at or above a severity."""

    if min_severity < 0 or min_severity > 10:
        return failure("min_severity must be between 0 and 10")

    db = db_session_basede26()

    try:
        rows = (
    db.query(Vulnerability)
    .filter(Vulnerability.severity >= min_severity)
    .all()
)

        severity_counts = Counter(
            str(row.severity)
            for row in rows
            if row.severity is not None
        )

        return success(
            {
                "total_vulnerabilities": len(rows),
                "by_severity": dict(severity_counts),
            }
        )

    except Exception as exc:
        print(f"summary error: {exc}", file=sys.stderr)
        return failure("database aggregation failed")

    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()