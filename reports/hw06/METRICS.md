# HW6 Metrics

## Memory Window Experiment

| Memory size | Prompt tokens | Latency |
|---:|---:|---:|
| 4 | 56 | 8058.89 ms |
| 12 | 120 | 2751.45 ms |
| 30 | 264 | 4172.09 ms |

Prompt size increased as more conversation history was included.

Latency varied because Ollama was running locally. Multiple trials would provide a more stable average.

## Memory Policy Cost

| Policy | Estimated cost |
|---|---:|
| Full 30-message memory | $206.70 |
| 12 messages plus summary | $148.50 |

Estimated savings:

```text
$58.20, approximately 28.2%