"""Exercise API endpoints using TestClient and print outputs.

Runs locally (no network) and demonstrates pay -> ranked uplift -> spend guardrail.
"""
from fastapi.testclient import TestClient
from api.server import app
import json


def pretty(resp):
    try:
        return json.dumps(resp.json(), indent=2)
    except Exception:
        return str(resp.text)


def main():
    client = TestClient(app)

    print("1) Initial ranking for job j1")
    r = client.post("/rank_job", json={"job_id": "j1"})
    print(pretty(r))

    print("\n2) Mark candidate s2 as paid for j1")
    r = client.post("/pay", json={"candidate_id": "s2", "job_id": "j1"})
    print(pretty(r))

    print("\n3) Ranking with conversion tuning")
    r = client.post("/rank_job_with_conversion", json={"job_id": "j1", "protect_conversion": True, "conversion_boost": 0.12})
    print(pretty(r))

    print("\n4) Check paid status for s2/j1")
    r = client.post("/is_paid", json={"candidate_id": "s2", "job_id": "j1"})
    print(pretty(r))

    print("\n5) Generate spend guardrail report")
    r = client.post("/admin/spend_guardrail")
    print(pretty(r))


if __name__ == "__main__":
    main()
