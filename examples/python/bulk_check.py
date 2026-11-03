"""Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).

Usage:
    pip install requests
    export WAVALIDATOR_API_KEY=your_key
    python bulk_check.py 14155551234 14155550000 447911123456
"""
import os
import sys
import time

import requests

API_URL = "https://wavalidator.com/api/v1/bulk-check/"
MAX_BATCH = 100


def bulk_check(numbers: list[str], api_key: str, retries: int = 3) -> dict:
    if len(numbers) > MAX_BATCH:
        raise ValueError(f"Max {MAX_BATCH} numbers per request")
    for _ in range(retries):
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"numbers": numbers},
            timeout=90,
        )
        if response.status_code == 429:
            time.sleep(int(response.json().get("retry_after", 60)))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Rate limit still reached after retries")


if __name__ == "__main__":
    numbers = sys.argv[1:] or ["14155551234", "14155550000", "447911123456"]
    data = bulk_check(numbers, os.environ["WAVALIDATOR_API_KEY"])

    for item in data["results"]:
        label = {"valid": "has WhatsApp", "invalid": "no WhatsApp"}.get(item["status"], "check failed")
        print(f"{item['number']}: {label}")
    print(f"Checked {data['checked']}/{data['total']} · credits used {data['credits_used']} · remaining {data['credits_remaining']}")
