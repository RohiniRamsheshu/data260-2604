# Part 3 - Tool Contracts Under Stress

## Rejected calls from Part 2B

| Tool | Valid input | Rejected input | Expected error |
|---|---|---|---|
| search_vulnerabilities | `{"query":"CVE","limit":5}` | `{"query":"CVE","limit":0}` | limit must be between 1 and 50 |
| vulnerability_detail | `{"vulnerability_id":5006}` | `{"vulnerability_id":0}` | vulnerability_id must be positive |
| vulnerability_summary | `{"min_severity":0}` | `{"min_severity":11}` | min_severity must be between 0 and 10 |

All rejected calls returned the shared envelope:

```json
{
  "ok": false,
  "data": null,
  "error": "..."
}