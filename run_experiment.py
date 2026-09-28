import os
import csv
import time
import requests

BASE_URL = "http://localhost:8804"
OUTPUT_DIR = "reports/hw04/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ENDPOINTS = ["naive", "fixed"]
PAGE_SIZES = [10, 50, 200]
ITERATIONS = 30

def run_benchmarks():
    csv_file_path = os.path.join(OUTPUT_DIR, "benchmark_results.csv")
    print(f"Starting benchmarks. Saving results to {csv_file_path}...")

    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["endpoint", "page_size", "iteration", "response_time_ms", "status_code"])

        for endpoint in ENDPOINTS:
            for page_size in PAGE_SIZES:
                print(f"Benchmarking endpoint: {endpoint} | page_size: {page_size}...")
                for i in range(1, ITERATIONS + 1):
                    url = f"{BASE_URL}/api/vulnerabilities/{endpoint}?limit={page_size}"
                    
                    start_time = time.perf_counter()
                    try:
                        response = requests.get(url)
                        status_code = response.status_code
                    except Exception as e:
                        status_code = 500
                    end_time = time.perf_counter()

                    latency_ms = (end_time - start_time) * 1000.0
                    writer.writerow([endpoint, page_size, i, round(latency_ms, 3), status_code])
                    
                    # Small sleep to prevent socket starvation
                    time.sleep(0.01)

    print("Benchmarking completed successfully!")

if __name__ == "__main__":
    run_benchmarks()
