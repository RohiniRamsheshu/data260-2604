import pandas as pd
import numpy as np

df = pd.read_csv("reports/hw04/raw/benchmark_results.csv")

summary = df.groupby(["endpoint", "page_size"])["response_time_ms"].agg(
    mean="mean",
    median="median",
    p95=lambda x: np.percentile(x, 95),
    p99=lambda x: np.percentile(x, 99)
).reset_index()

print("=== BENCHMARK SUMMARY (ms) ===")
print(summary.to_string(index=False))

# Save summary metrics
summary.to_csv("reports/hw04/raw/benchmark_summary.csv", index=False)