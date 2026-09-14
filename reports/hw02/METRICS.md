# HW2 Metrics

## Experiment 1: Schema Validation (30 runs, ceiling=6)

| Outcome | Count | Mean latency (ms) |
|---|---|---|
| Valid first attempt | 10 | 2,014 |
| Valid after 1 retry | 0 | — |
| Valid after 2+ retries | 0 | — |
| Hit turn ceiling | 20 | 7,296 (excl. 1 outlier) |

**Finding**: bimodal outcomes - either passes turn 1, or loops to ceiling. No mid-retry successes, suggesting ceiling=6 is too tight.

## Experiment 2: Turn ceiling comparison (20 runs each)

| Ceiling | Completion rate | Mean latency (ms) |
|---|---|---|
| 2 | 0% (0/20) | 1760 |
| 10 | 65% (13/20) | 5760 |

**Decision**: deploying with the ceiling showing higher completion rate above, since it gives the self-correction loop enough room without excessive latency cost.