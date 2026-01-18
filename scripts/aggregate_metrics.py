# scripts/aggregate_metrics.py
import json, csv
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("logs/app.log")
OUT_DIR = Path("metrics")
OUT_DIR.mkdir(exist_ok=True)

def aggregate():
    stats = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "total_requests": 0,
        "avg_latency_ms": 0,
        "errors": 0,
        "tests_total": 0,
        "tests_passed": 0,
    }
    latencies = []

    with LOG_FILE.open() as f:
        for line in f:
            entry = json.loads(line)
            if entry["event"] == "request":
                stats["total_requests"] += 1
            if entry["event"] == "response":
                latencies.append(entry["latency_ms"])
            if entry["level"] == "ERROR":
                stats["errors"] += 1
            if entry["event"] == "run-tests":
                stats["tests_total"] += 1
                if entry.get("status") == "passed":
                    stats["tests_passed"] += 1

    if latencies:
        stats["avg_latency_ms"] = sum(latencies) / len(latencies)

    csv_path = OUT_DIR / f"{stats['date']}.csv"
    with csv_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=stats.keys())
        writer.writeheader()
        writer.writerow(stats)

if __name__ == "__main__":
    aggregate()