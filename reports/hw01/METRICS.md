# HW1 Metrics

## Non-Determinism Results

| Metric | Temp 0.7 | Temp 0.0 |
|---|---|---|
| Distinct tag sets | 10 | 1 |
| Tags in all 20 runs | ["lodash"] | ["lodash", "vulnerability", "security"] |
| Tags in exactly 1 run | ["prototype pollution", "security vulnerability", "prototype"] | (none) |
| Latency p50 (ms) | 1390 | 1197 |
| Latency p95 (ms) | 9078 | 1302 |
| Latency p99 (ms) | 9078 | 1302 |

## Explanation

At temperature 0.7, two users submitting identical input could see meaningfully different tag sets and summaries — our data shows 10 distinct tag sets out of 20 runs, with only "lodash" appearing consistently across every run. At temperature 0.0, users would see virtually identical output every time — all 20 runs produced the same 3 tags, showing the model behaves near-deterministically at this setting.

**Where variation is acceptable**: a creative writing assistant or brainstorming tool, where users want varied, fresh suggestions each time — temperature 0.7-style variation is a feature, not a bug.

**Where variation is not acceptable**: a compliance/classification system (e.g., tagging vulnerabilities by category for a security dashboard) — if the same report gets tagged differently each run, it breaks consistency and trust for a team relying on those tags. Temperature 0.0 is the right choice there.
