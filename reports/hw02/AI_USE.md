# AI Use Disclosure - HW2

1. Used Claude to explain FastAPI/LangGraph/Pydantic concepts and debug real errors (Docker port squatting old server, missing script.js edits due to browser cache, empty file saves). Wrote/ran all code myself.
2. AI-suggested Reviewer prompt was initially too subjective ("vague summary"), causing every run to hit the turn ceiling.
3. Detected via inspecting reviewer_feedback text across runs and noticing it never approved anything.
4. Rewrote Reviewer prompt to check only 3 objective rules (exact tag count, tag length, word count) instead of subjective quality - runs then showed realistic mixed outcomes.
