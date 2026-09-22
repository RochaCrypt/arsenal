#!/usr/bin/env python3
"""
findings-to-report.py — turn a findings JSON into a CSV + Markdown table.
Author : Alexandre Rocha (github.com/RochaCrypt)
License: MIT

PURPOSE
    Standardise pentest/vuln findings into clean deliverables, sorted by
    severity. Input is a simple JSON list; output is report.csv + report.md.

INPUT (findings.json):
    [
      {"title": "SQL Injection in login", "severity": "Critical",
       "asset": "web01", "cvss": 9.8, "recommendation": "Use parameterised queries"},
      {"title": "Missing security headers", "severity": "Low",
       "asset": "web01", "cvss": 3.1, "recommendation": "Add CSP, HSTS"}
    ]

USAGE:
    python3 findings-to-report.py findings.json -o report
"""
import argparse
import csv
import json
import sys

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
FIELDS = ["title", "severity", "asset", "cvss", "recommendation"]


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"[!] Could not read {path}: {exc}")
    if not isinstance(data, list):
        sys.exit("[!] Expected a JSON list of findings.")
    return data


def norm(f):
    return {k: f.get(k, "") for k in FIELDS}


def sort_key(f):
    return (SEV_ORDER.get(str(f.get("severity", "")).lower(), 99),
            -float(f.get("cvss") or 0))


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def write_md(rows, path):
    lines = ["| # | Severity | CVSS | Title | Asset | Recommendation |",
             "| :-: | :--- | :-: | :--- | :--- | :--- |"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['severity']} | {r['cvss']} | "
                     f"{r['title']} | {r['asset']} | {r['recommendation']} |")
    counts = {}
    for r in rows:
        counts[r["severity"]] = counts.get(r["severity"], 0) + 1
    summary = " · ".join(f"{k}: {v}" for k, v in counts.items())
    header = f"# Findings report\n\n**Total:** {len(rows)}  \n**Breakdown:** {summary}\n\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Findings JSON -> CSV + Markdown")
    ap.add_argument("input", help="findings.json")
    ap.add_argument("-o", "--output", default="report", help="output basename")
    args = ap.parse_args()

    rows = sorted((norm(f) for f in load(args.input)), key=sort_key)
    write_csv(rows, f"{args.output}.csv")
    write_md(rows, f"{args.output}.md")
    print(f"[+] Wrote {args.output}.csv and {args.output}.md ({len(rows)} findings)")


if __name__ == "__main__":
    main()
