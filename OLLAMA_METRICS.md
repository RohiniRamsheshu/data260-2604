# Ollama Agent Metrics

| Scenario | Steps | Tool calls | Stop reason |
|---|---:|---:|---|
| Find vulnerabilities related to CVE | 1 | 1 | normal_completion |
| Show vulnerability with ID 5005 | 1 | 1 | normal_completion |
| Show vulnerability with ID 5006 | 1 | 1 | tool_error_or_safety_block |
| Give me a summary of vulnerabilities with severity at least 5 | 1 | 1 | normal_completion |
