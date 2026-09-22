#!/usr/bin/env python3
"""
auth-log-triage.py — summarise Linux SSH auth logs for quick triage.
Author : Alexandre Rocha (github.com/RochaCrypt)
License: MIT

PURPOSE
    Defensive/monitoring helper. Parses an auth log and reports failed vs
    accepted SSH logins, plus the top source IPs and usernames — useful for
    spotting brute-force activity during triage.

USAGE:
    python3 auth-log-triage.py /var/log/auth.log
    python3 auth-log-triage.py /var/log/auth.log --top 15
"""
import argparse
import re
import sys
from collections import Counter

FAIL = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)")
OK = re.compile(r"Accepted \w+ for (\S+) from (\d+\.\d+\.\d+\.\d+)")


def main():
    ap = argparse.ArgumentParser(description="Summarise SSH auth logs")
    ap.add_argument("logfile")
    ap.add_argument("--top", type=int, default=10, help="rows per table")
    args = ap.parse_args()

    fail_ip, fail_user, ok_ip, ok_user = Counter(), Counter(), Counter(), Counter()
    failed = accepted = 0
    try:
        with open(args.logfile, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                m = FAIL.search(line)
                if m:
                    failed += 1
                    fail_user[m.group(1)] += 1
                    fail_ip[m.group(2)] += 1
                    continue
                m = OK.search(line)
                if m:
                    accepted += 1
                    ok_user[m.group(1)] += 1
                    ok_ip[m.group(2)] += 1
    except OSError as exc:
        sys.exit(f"[!] Could not read {args.logfile}: {exc}")

    def show(title, counter):
        print(f"\n== {title} ==")
        if not counter:
            print("  (none)")
        for item, n in counter.most_common(args.top):
            print(f"  {n:6d}  {item}")

    print(f"[*] Accepted logins: {accepted}")
    print(f"[*] Failed logins  : {failed}")
    show("Top source IPs (failed)", fail_ip)
    show("Top usernames (failed)", fail_user)
    show("Top source IPs (accepted)", ok_ip)

    flags = [ip for ip, n in fail_ip.items() if n >= 20]
    if flags:
        print("\n[!] Possible brute-force sources (>=20 failures):")
        for ip in flags:
            print(f"    {ip} ({fail_ip[ip]} failures)")


if __name__ == "__main__":
    main()
