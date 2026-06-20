"""Campus navigation API smoke tests: python tests.py"""

import subprocess
import sys
import time

import requests

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

print("[*] Starting test server...")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
time.sleep(2)
print("[*] Server ready\n")


def test(desc: str, route: str, method: str = "post", data: dict | None = None, expect_status: int = 200) -> None:
    global PASS, FAIL
    url = f"{BASE}{route}"
    try:
        started_at = time.perf_counter()
        if method == "post":
            resp = requests.post(url, json=data, timeout=5)
        else:
            resp = requests.get(url, timeout=5)
        elapsed_ms = (time.perf_counter() - started_at) * 1000

        body = resp.json() if resp.text else {}
        ok = resp.status_code == expect_status
        status = "PASS" if ok else "FAIL"

        if ok:
            PASS += 1
        else:
            FAIL += 1

        print(f"[{status}] {desc}")
        print(f"       route: {route}")
        print(f"       http: {resp.status_code} (expected {expect_status})")
        print(f"       elapsed: {elapsed_ms:.2f} ms")
        print(f"       json: {body}")
    except Exception as exc:
        FAIL += 1
        print(f"[FAIL] {desc}")
        print(f"       {exc}")


def test_same_result(desc: str, data: dict) -> None:
    global PASS, FAIL
    try:
        dijkstra_started_at = time.perf_counter()
        dijkstra_resp = requests.post(f"{BASE}/api/navigation", json=data, timeout=5)
        dijkstra_elapsed_ms = (time.perf_counter() - dijkstra_started_at) * 1000

        floyd_started_at = time.perf_counter()
        floyd_resp = requests.post(f"{BASE}/api/navigation/floyd", json=data, timeout=5)
        floyd_elapsed_ms = (time.perf_counter() - floyd_started_at) * 1000

        dijkstra_body = dijkstra_resp.json() if dijkstra_resp.text else {}
        floyd_body = floyd_resp.json() if floyd_resp.text else {}
        ok = (
            dijkstra_resp.status_code == 200
            and floyd_resp.status_code == 200
            and dijkstra_body == floyd_body
        )

        status = "PASS" if ok else "FAIL"
        if ok:
            PASS += 1
        else:
            FAIL += 1

        print(f"[{status}] {desc}")
        print(f"       request: {data}")
        print(f"       dijkstra: status={dijkstra_resp.status_code}, elapsed={dijkstra_elapsed_ms:.2f} ms, json={dijkstra_body}")
        print(f"       floyd:    status={floyd_resp.status_code}, elapsed={floyd_elapsed_ms:.2f} ms, json={floyd_body}")
    except Exception as exc:
        FAIL += 1
        print(f"[FAIL] {desc}")
        print(f"       {exc}")


print("=" * 60)

cases = [
    {"start": 1, "end": 33, "mode": "walk", "period": "normal", "strategy": "distance"},
    {"start": 1, "end": 33, "mode": "bike", "period": "normal", "strategy": "distance"},
    {"start": 1, "end": 33, "mode": "bike", "period": "normal", "strategy": "time"},
    {"start": 1, "end": 33, "mode": "bike", "period": "morning_peak", "strategy": "time"},
    {"start": 1, "end": 33, "mode": "bike", "period": "lunch_peak", "strategy": "time"},
    {"start": 1, "end": 33, "mode": "bike", "period": "evening_peak", "strategy": "time"},
    {"start": 0, "end": 33, "mode": "bike", "period": "normal", "strategy": "distance"},
    {"start": 2, "end": 17, "mode": "walk", "period": "normal", "strategy": "distance"},
    {"start": 26, "end": 35, "mode": "walk", "period": "normal", "strategy": "distance"},
    {"start": 0, "end": 0, "mode": "walk", "period": "normal", "strategy": "distance"},
]

for index, data in enumerate(cases, start=1):
    test(f"Dijkstra case {index}", "/api/navigation", data=data)
    test(f"Floyd case {index}", "/api/navigation/floyd", data=data)
    test_same_result(f"Compare case {index}", data)

test(
    "Dijkstra invalid start",
    "/api/navigation",
    data={"start": 999, "end": 33, "mode": "walk", "period": "normal", "strategy": "distance"},
    expect_status=400,
)
test(
    "Floyd invalid start",
    "/api/navigation/floyd",
    data={"start": 999, "end": 33, "mode": "walk", "period": "normal", "strategy": "distance"},
    expect_status=400,
)
test("health", "/health", method="get")

print("=" * 60)
proc.terminate()
proc.wait()
print(f"Passed: {PASS}  Failed: {FAIL}  Total: {PASS + FAIL}")
if FAIL:
    sys.exit(1)
