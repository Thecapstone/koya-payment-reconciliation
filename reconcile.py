#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal

latest_events = {}

with open("payments.jsonl", "r") as f:
    # prevent overwrite of payment file, count fron 1 for synchronous line numbers
    for line_num, line in enumerate(f, start=1):
        try:
            # skip all malformed lines, no txn_id, or non-dict events
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        timestamp = event.get("ts", "")
        # prevent repeat events by tracking timestamps
        previous = latest_events.get(txn_id)
        if previous is None or timestamp >= previous["ts"]:
            latest_events[txn_id] = event

successful_events = [
    event for event in latest_events.values() if event.get("status") == "success"
]
count = len(successful_events)
total = sum(
    (
        Decimal(str(event["amount"]).replace(",", ""))
        for event in successful_events
    ),
    Decimal("0"),
)

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
