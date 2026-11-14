"""Create H5 fictional records: python -m scripts.demo_client [--reset]."""
import argparse
import os
from pathlib import Path

import httpx
from dotenv import dotenv_values

STUDENTS = [
    {"student_id": "SV9001", "full_name": "Nguyen Van A", "major": "Computer Science",
     "national_id": "012345678901", "phone": "0901234567", "address": "Ha Noi (fictional)"},
    {"student_id": "SV9002", "full_name": "Tran Thi B", "major": "Information Security",
     "national_id": "098765432109", "phone": "0912345678", "address": "Da Nang (fictional)"},
]


def seed(client: httpx.Client, reset: bool = False) -> int:
    if reset:
        for student in STUDENTS:
            sid = student["student_id"]
            response = client.delete(f"/students/{sid}")
            print(f"DELETE {sid} -> {response.status_code}")
            if response.status_code not in (204, 404):
                return 1
    for student in STUDENTS:
        sid = student["student_id"]
        response = client.post("/students", json=student)
        if response.status_code == 201:
            print(f"{sid}: created (201)")
        elif response.status_code == 409 and response.json().get("code") == "duplicate_student":
            print(f"{sid}: already exists, skipped")
        else:
            print(f"{sid}: unexpected HTTP {response.status_code}")
            return 1
        response = client.get(f"/students/{sid}")
        print(f"GET {sid} -> {response.status_code}")
        if response.status_code != 200:
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true",
                        help="Delete ONLY SV9001 and SV9002 before recreating them.")
    args = parser.parse_args(argv)
    env = {**dotenv_values(Path(__file__).resolve().parents[1] / ".env"), **os.environ}
    token = env.get("ADMIN_TOKEN")
    if not token:
        print("ADMIN_TOKEN is missing. Run python scripts/init_env.py first.")
        return 1
    api = f"http://127.0.0.1:{env.get('API_PORT') or '8000'}"
    try:
        with httpx.Client(base_url=api, headers={"Authorization": f"Bearer {token}"},
                          timeout=10, trust_env=False) as client:
            return seed(client, reset=args.reset)
    except (httpx.HTTPError, ValueError):
        # Do not echo exception/request bodies that might contain secrets.
        print("Demo request failed. Check API_PORT, API health and local configuration.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
