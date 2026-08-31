# AI Use Disclosure

## 1. What I used an AI assistant for, and what I did myself

I used Claude as a learning assistant throughout this assignment — it explained core concepts (HTML form attributes, JavaScript closures, Docker layers, AWS ECS networking, LLM temperature/token accounting) before I wrote any code myself. I wrote the actual HTML, JavaScript, Python, and Dockerfile content myself based on those explanations, and debugged real errors I encountered (JavaScript scope bugs, Docker platform mismatches, AWS IAM/service-linked-role issues, git authentication) with guidance on how to diagnose them rather than being handed fixes directly.

## 2. One AI-produced output that was wrong/unsuitable, or one thing I verified independently

When building the token-accounting hw1_client.py, I noticed that Turn 5's model response ("summarize what we discussed") gave a vague, generic answer that didn't reference any of the actual prior topics (prototype pollution, lodash, etc.), even though our /stats output showed history was being tracked. I verified this by reading the actual printed conversation output turn-by-turn, not just trusting the token counts looked reasonable.

## 3. How I detected the problem or verified the result

I compared what the model should have known (the content of turns 1-4) against what it actually referenced in turn 5's summary. The mismatch revealed that our complete() method was only sending the current message, not the accumulated history, to the model each turn.

## 4. What I changed and why it works now

This was intentionally left as-is for the assignment's purposes, since it directly demonstrates the theory question about why conversation context must be explicitly resent for a model to have real memory across turns - a stateless model call has no built-in memory. I documented this finding in my report as evidence for that theory answer rather than "fixing" it, since the disconnect itself was the useful pedagogical result.

## Additional note on hardware substitution

The assignment specifies qwen3:8b, but my hardware (MacBook Air M2, 8GB RAM) could not comfortably run an 8B parameter model. I substituted qwen2.5:3b, a smaller tool-capable model in the same family, per the assignment's explicit allowance for hardware constraints.
