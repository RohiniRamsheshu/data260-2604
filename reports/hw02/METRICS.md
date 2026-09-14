# HW2 Metrics

## Experiment 1: Schema Validation over 30 runs (turn ceiling = 6)

| Outcome | Count | Mean latency (ms) |
|---|---|---|
| Valid first attempt | 10 | 2,014 |
| Valid after 1 retry | 0 | — |
| Valid after 2+ retries | 0 | — |
| Hit turn ceiling | 20 (one outlier at 448,863ms excluded from mean) | 7,296 |

**Observation**: outcomes were strictly bimodal — either the Planner passed schema validation and the Reviewer approved on the very first attempt (10/30 runs), or the loop never recovered before hitting the ceiling (20/30 runs). No run succeeded after exactly 1 or 2+ retries. With `TURN_CEILING = 6`, there is only room for roughly two full Planner->Reviewer cycles; if the first cycle is rejected, the second attempt is apparently also failing validation or review often enough that the ceiling is reached before a clean approval. This suggests the turn ceiling may be too low to give the self-correction loop a realistic chance to succeed - directly motivating the ceiling comparison experiment below.

One run (#28) took approximately 7.5 minutes (448,863ms), wildly inconsistent with every other run (1.8s-15s range). This is treated as a system-level anomaly (likely local resource contention on an 8GB machine) rather than representative model latency, and is excluded from the mean latency calculation for that outcome category.
