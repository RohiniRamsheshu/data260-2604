import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


SPAN_FILE = Path("reports/hw10/raw/spans.jsonl")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_span(span):
    SPAN_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SPAN_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(span) + "\n")


@contextmanager
def trace_span(trace_id, stage):
    start_time = utc_now()
    start_clock = time.perf_counter()

    span = {
        "trace_id": trace_id,
        "stage": stage,
        "start_time": start_time,
        "end_time": None,
        "duration_ms": None,
        "status": "running",
        "error": None,
    }

    try:
        yield span
        span["status"] = "success"

    except Exception as exc:
        span["status"] = "error"
        span["error"] = str(exc)
        raise

    finally:
        span["end_time"] = utc_now()
        span["duration_ms"] = round(
            (time.perf_counter() - start_clock) * 1000,
            3,
        )
        write_span(span)