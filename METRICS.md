# Part 5 Agent Metrics

| Scenario | Steps | Tool calls | Stop reason |
|---|---:|---:|---|
| Find CVE vulnerabilities | 1 | 1 | normal_completion |
| Show a normal vulnerability | 1 | 1 | normal_completion |
| Show a high severity vulnerability | 1 | 1 | tool_error_or_safety_block |
| Keep asking for more information | 3 | 3 | max_steps |
