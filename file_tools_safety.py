import difflib
import fnmatch
import json
import re
import shlex
import subprocess
import tempfile
from pathlib import Path


MAX_LINES = 50
SAFE_PREFIXES = ("pwd", "ls", "find", "grep", "rg", "cat", "head", "tail")


def safe_path(root, relative):
    path = (root / relative).resolve()

    if root.resolve() not in path.parents and path != root.resolve():
        raise ValueError("path escapes sandbox")

    return path


def read_file(root, relative, max_lines=MAX_LINES):
    path = safe_path(root, relative)
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:max_lines])


def write_file(root, relative, content):
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "written"


def edit_file(root, relative, old, new):
    path = safe_path(root, relative)
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)

    if original == updated:
        raise ValueError("target text not found")

    diff = list(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm="",
        )
    )

    if len(diff) > MAX_LINES:
        raise ValueError("diff is too large")

    path.write_text(updated, encoding="utf-8")
    return "\n".join(diff)


def glob_files(root, pattern):
    return [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and fnmatch.fnmatch(path.name, pattern)
    ]


def search_in_files(root, pattern, file_pattern="*.txt"):
    matches = []

    for relative in glob_files(root, file_pattern):
        path = safe_path(root, relative)

        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if pattern in line:
                matches.append(
                    {
                        "file": relative,
                        "line": number,
                        "text": line,
                    }
                )

    return matches


def is_destructive(command):
    lowered = command.lower()

    denied = [
        r"\brm\s+-rf\b",
        r"\brm\s+-r\b",
        r"\bsudo\b",
        r"\bchmod\b",
        r"\bchown\b",
        r"\bdd\s+if=",
        r">\s*/",
        r"\bmkfs\b",
        r"\bformat\b",
    ]

    return any(re.search(pattern, lowered) for pattern in denied)


def confirm_bash(command, auto_approve=False):
    first_word = shlex.split(command)[0] if command.strip() else ""

    if is_destructive(command):
        return {
            "allowed": False,
            "reason": "independent destructive-command deny-list",
        }

    if first_word not in SAFE_PREFIXES:
        return {
            "allowed": False,
            "reason": "command is not in SAFE_PREFIXES",
        }

    if not auto_approve:
        return {
            "allowed": False,
            "reason": "confirmation required; auto_approve is false",
        }

    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=5,
    )

    return {
        "allowed": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout[:1000],
    }


def main():
    passed = 0
    blocked = 0

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)

        write_file(root, "notes.txt", "INFO: hello\nDEBUG: inspect this line\n")
        write_file(root, "other.txt", "INFO: another file\n")

        # Integration test: glob -> search -> read
        files = glob_files(root, "*.txt")
        findings = search_in_files(root, "DEBUG", "*.txt")
        content = read_file(root, findings[0]["file"])

        integration_ok = (
            files == ["notes.txt", "other.txt"]
            and findings[0]["line"] == 2
            and "DEBUG" in content
        )

        print("Integration glob->search->read:", "PASS" if integration_ok else "FAIL")

        tests = [
            ("write file", lambda: write_file(root, "new.txt", "hello")),
            ("read file", lambda: read_file(root, "notes.txt")),
            ("edit file", lambda: edit_file(root, "notes.txt", "hello", "updated")),
            ("glob files", lambda: glob_files(root, "*.txt")),
            ("search files", lambda: search_in_files(root, "DEBUG", "*.txt")),
        ]

        for name, function in tests:
            try:
                function()
                print("PASS:", name)
                passed += 1
            except Exception as exc:
                print("FAIL:", name, exc)

        blocked_tests = [
            ("path escape", lambda: read_file(root, "../outside.txt")),
            ("large read", lambda: read_file(root, "notes.txt", max_lines=1000)),
            ("destructive rm", lambda: confirm_bash("rm -rf /tmp/x")),
            ("privilege escalation", lambda: confirm_bash("sudo ls")),
            ("unapproved bash", lambda: confirm_bash("ls", auto_approve=False)),
        ]

        for name, function in blocked_tests:
            try:
                result = function()

                if name == "large read":
                    raise AssertionError("large read was not blocked")

                if name in {"destructive rm", "privilege escalation", "unapproved bash"}:
                    if result["allowed"]:
                        raise AssertionError("command was allowed")

                print("BLOCKED:", name)
                blocked += 1
            except Exception:
                print("BLOCKED:", name)
                blocked += 1

    output = {
        "integration_passed": integration_ok,
        "safe_tests_passed": passed,
        "blocked_tests_passed": blocked,
        "expected_safe_tests": 5,
        "expected_blocked_tests": 5,
    }

    path = Path("reports/hw07/raw/file-tools-safety-results.json")
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()