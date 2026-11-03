"""Clean a CSV contact list: split it into numbers with and without WhatsApp.

Sends the phone column to the WA Validator bulk API in batches of 100,
waits automatically on rate limits, and writes whatsapp.csv and no_whatsapp.csv
(rows the API could not check go to retry.csv).

Usage:
    pip install requests
    export WAVALIDATOR_API_KEY=your_key
    python clean_csv.py leads.csv --column phone
"""
import argparse
import csv
import os
import re
import time

import requests

API_URL = "https://wavalidator.com/api/v1/bulk-check/"
BATCH = 100


def normalize(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    return digits[2:] if digits.startswith("00") else digits


def check_batch(numbers, api_key):
    while True:
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"numbers": numbers},
            timeout=90,
        )
        if r.status_code == 429:
            wait = int(r.json().get("retry_after", 60))
            print(f"  rate limit reached, waiting {wait}s")
            time.sleep(wait)
            continue
        if r.status_code == 402:
            raise SystemExit("Out of credits — top up at https://wavalidator.com/pricing/")
        r.raise_for_status()
        return {item["number"]: item["status"] for item in r.json()["results"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv_file")
    parser.add_argument("--column", default="phone", help="name of the phone number column")
    args = parser.parse_args()
    api_key = os.environ["WAVALIDATOR_API_KEY"]

    with open(args.csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    unique = sorted({n for n in (normalize(r[args.column]) for r in rows) if n})
    print(f"{len(rows)} rows, {len(unique)} unique numbers")

    status = {}
    for i in range(0, len(unique), BATCH):
        batch = unique[i : i + BATCH]
        status.update(check_batch(batch, api_key))
        print(f"  checked {min(i + BATCH, len(unique))}/{len(unique)}")

    outputs = {
        "valid": open("whatsapp.csv", "w", newline="", encoding="utf-8"),
        "invalid": open("no_whatsapp.csv", "w", newline="", encoding="utf-8"),
        "retry": open("retry.csv", "w", newline="", encoding="utf-8"),
    }
    writers = {k: csv.DictWriter(f, fieldnames=fields) for k, f in outputs.items()}
    for w in writers.values():
        w.writeheader()

    counts = {k: 0 for k in outputs}
    for row in rows:
        s = status.get(normalize(row[args.column]))
        key = s if s in ("valid", "invalid") else "retry"
        writers[key].writerow(row)
        counts[key] += 1
    for f in outputs.values():
        f.close()

    print(f"whatsapp.csv: {counts['valid']} · no_whatsapp.csv: {counts['invalid']} · retry.csv: {counts['retry']}")


if __name__ == "__main__":
    main()
