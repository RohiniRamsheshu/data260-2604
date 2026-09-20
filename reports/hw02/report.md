# DATA-260 Homework 2 Report
**Name**: Rohini Ramasheshu

## Configuration Values
- SID4: 2604
- PORT_BASE: 8804
- PREFIX: s2604
- SEED: 2604
- VERIFY_SEED: 262604
- DOMAIN_ID: 4 (Open-source package vulnerabilities)

## Hardware & Model
- Hardware: MacBook Air M2, 8GB RAM
- Local model used: qwen2.5:3b (substituted for qwen3:8b, documented in HW1 due to 8GB RAM constraint)
- Tagged commit hash: 20cafe2392e080d4dcd58e4dac7ba9b40ce17300

## Part 1 — HTML & CSS
Restyled the HW1 form to remain usable at 375px width using a flex-column layout with a max-width container. Added visible loading, empty, and error state containers, toggled via JavaScript based on fetch outcomes.

## Part 2 — FastAPI Backend
Built a FastAPI backend on PORT_BASE 8804 (`src/main.py`) with an in-memory records list. Implemented:
- **Add**: `POST /api/records` — form data saved, redirects to home view showing updated list.
- **Update ID 1**: `POST /api/records/1/update` — updates package name and version for record ID 1, redirects home.
- **Delete highest ID**: `POST /api/records/delete-highest` — removes the record with the max ID, redirects home.
- **Search**: `GET /api/records?q=...` — filters by package name or version, wired to a live-search input on the frontend.

All four operations were verified end-to-end via curl and the browser UI (see RUN_LOG.txt).

## Part 3 — Stateful Agent Graph
Refactored the HW1 sequential Planner/Reviewer pipeline into a LangGraph `StateGraph` (`src/agent_graph.py`) implementing the Supervisor pattern:
- **AgentState** (TypedDict): shared state holding title, content, planner_proposal, reviewer_feedback, turn_count, validation_error, schema_valid.
- **Nodes**: `planner_node`, `reviewer_node`, `supervisor_node` — each a pure function taking state and returning a partial update dict.
- **Router (`router_logic`)**: reads state and routes to "planner", "reviewer", or END based on turn ceiling, schema validity, and reviewer feedback.
- All LLM calls route through `src/model_client.py` (the HW1 adapter), not directly through Ollama/LangChain, per the assignment requirement.

**Self-correction loop tested**: initially the Reviewer's prompt used subjective quality judgment, causing every run to loop to the turn ceiling without ever approving. Rewriting the Reviewer's prompt to check only 3 objective rules (exact tag count, tag length range, summary word count) produced a realistic mix of early-approval and looped runs, confirming the loop and ceiling both function correctly.

## Part 4 — Output Schema and Loop Safety

### Pydantic validation
Added a `PlannerOutput` Pydantic model validating: exactly 3 tags, each 3-30 characters, and a summary of at most 25 words. On validation failure, the error message is fed back into the Planner's next prompt, and the router sends control back to Planner (not Reviewer) until schema_valid is True or the turn ceiling is reached.

### Experiment 1: 30 runs, fixed input, turn ceiling = 6
Fixed input saved at `reports/hw02/cases/schema_input.json`. Raw results: `reports/hw02/raw/schema_validation_runs.csv`.

| Outcome | Count | Mean latency (ms) |
|---|---|---|
| Valid first attempt | 10 | 2,014 |
| Valid after 1 retry | 0 | - |
| Valid after 2+ retries | 0 | - |
| Hit turn ceiling | 20 | 7,296 (1 outlier excluded, 448,863ms - likely local resource contention) |

**Finding**: outcomes were strictly bimodal. Either the Planner passed schema validation and the Reviewer approved on the first attempt (10/30), or the loop never recovered before hitting the ceiling (20/30). No run succeeded after exactly 1 or 2+ retries. With TURN_CEILING=6, there is only room for roughly two full Planner-Reviewer cycles - if the first is rejected, there is little room left to recover, which directly motivated the ceiling comparison below.

### Experiment 2: Turn ceiling comparison (2 vs 10, 20 runs each)
Raw results: `reports/hw02/raw/ceiling_comparison_runs.csv`.

| Ceiling | Completion rate | Mean latency (ms) |
|---|---|---|
| 2 | 0% (0/20) | 1,760 |
| 10 | 65% (13/20) | 5,760 |

**Decision**: ceiling=2 completed 0% of runs (0/20) - essentially no chance to self-correct once the first attempt is rejected. Ceiling=10 completed 65% (13/20), at roughly 3.3x the mean latency (5,760ms vs 1,760ms). Since a completion rate of 0% makes ceiling=2 unusable in practice, ceiling=10 (or similar) is recommended for deployment despite the latency cost, as partial completion is far more valuable than near-total failure.

### Experiment 3: Adversarial input
Adversarial input (deliberately minimal/low-information): `{"title": "x", "content": "n/a"}`, saved at `reports/hw02/cases/adversarial_input.json`. Run 5 times; results in `reports/hw02/raw/adversarial_runs.csv`.

**Why it causes trouble**: with almost no real content, the Planner has nothing substantive to generate tags or a summary from, making it likely to produce vague, generic, or repetitive output that struggles to satisfy the Reviewer's criteria consistently, pushing runs toward the turn ceiling more often than a well-formed input.

**Proposed fix**: add an input-quality pre-check before the Planner runs - if title/content fall below a minimum length or information threshold, short-circuit with a clear "insufficient input" response rather than letting the graph loop uselessly toward the ceiling.

## AI Use
See `AI_USE.md` for full disclosure.

## Reproducible run instructions
See `README.md` in the repository root for full setup and run instructions for every component (FastAPI backend, LangGraph agent, experiments).
