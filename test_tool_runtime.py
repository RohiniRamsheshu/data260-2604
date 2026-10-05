import json

from tool_runtime import execute_tool


def run_test(name, function):
    try:
        function()
        print(f"PASS: {name}")
        return True
    except AssertionError as exc:
        print(f"FAIL: {name} - {exc}")
        return False


def get_result(name, inputs):
    return json.loads(execute_tool(name, inputs))


def test_search_valid():
    output = get_result(
        "search_vulnerabilities",
        {"query": "CVE", "limit": 2},
    )
    assert output["ok"] is True
    assert len(output["data"]) == 2


def test_search_invalid():
    output = get_result(
        "search_vulnerabilities",
        {"query": "CVE", "limit": 0},
    )
    assert output["ok"] is False


def test_detail_valid():
    output = get_result(
        "vulnerability_detail",
        {"vulnerability_id": 5005},
    )
    assert output["ok"] is True
    assert output["data"]["id"] == 5005


def test_detail_invalid():
    output = get_result(
        "vulnerability_detail",
        {"vulnerability_id": 0},
    )
    assert output["ok"] is False


def test_summary_valid():
    output = get_result(
        "vulnerability_summary",
        {"min_severity": 0},
    )
    assert output["ok"] is True
    assert output["data"]["total_vulnerabilities"] == 3


def test_summary_invalid():
    output = get_result(
        "vulnerability_summary",
        {"min_severity": 11},
    )
    assert output["ok"] is False


def test_unknown_tool():
    output = get_result("not_a_real_tool", {})
    assert output["ok"] is False
def test_safety_rule_blocks_high_severity():
    output = get_result(
        "vulnerability_detail",
        {"vulnerability_id": 5006},
    )
    assert output["ok"] is False
    assert "safety rule" in output["error"]


def test_safety_rule_allows_normal_record():
    output = get_result(
        "vulnerability_detail",
        {"vulnerability_id": 5005},
    )
    assert output["ok"] is True

tests = [
    ("search valid", test_search_valid),
    ("search invalid", test_search_invalid),
    ("detail valid", test_detail_valid),
    ("detail invalid", test_detail_invalid),
    ("summary valid", test_summary_valid),
    ("summary invalid", test_summary_invalid),
    ("unknown tool", test_unknown_tool),
        (
        "safety rule blocks high severity",
        test_safety_rule_blocks_high_severity,
    ),
    (
        "safety rule allows normal record",
        test_safety_rule_allows_normal_record,
    ),
]


passed = 0

for test_name, test_function in tests:
    if run_test(test_name, test_function):
        passed += 1

print()
print(f"SUMMARY: {passed}/{len(tests)} tests passed")

if passed != len(tests):
    raise SystemExit(1)