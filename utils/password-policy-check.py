#!/usr/bin/env python3
"""
password-policy-check.py — validate passwords against a policy + estimate entropy.
Author : Alexandre Rocha (github.com/RochaCrypt)
License: MIT

PURPOSE
    Defensive utility to test whether passwords meet a configurable policy and
    to estimate their entropy. Reads from stdin (never from arguments, so
    secrets don't land in shell history). Useful for validating policy strength.

USAGE:
    python3 password-policy-check.py                 # prompts, hidden input
    echo 'Sample123!' | python3 password-policy-check.py --min-length 12
"""
import argparse
import getpass
import math
import re
import sys


def entropy_bits(pw):
    pool = 0
    if re.search(r"[a-z]", pw):
        pool += 26
    if re.search(r"[A-Z]", pw):
        pool += 26
    if re.search(r"\d", pw):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", pw):
        pool += 32
    return round(len(pw) * math.log2(pool), 1) if pool else 0.0


def check(pw, args):
    issues = []
    if len(pw) < args.min_length:
        issues.append(f"shorter than {args.min_length} characters")
    if args.require_upper and not re.search(r"[A-Z]", pw):
        issues.append("no uppercase letter")
    if args.require_lower and not re.search(r"[a-z]", pw):
        issues.append("no lowercase letter")
    if args.require_digit and not re.search(r"\d", pw):
        issues.append("no digit")
    if args.require_symbol and not re.search(r"[^A-Za-z0-9]", pw):
        issues.append("no symbol")
    return issues


def strength(bits):
    if bits < 40:
        return "Weak"
    if bits < 60:
        return "Fair"
    if bits < 80:
        return "Strong"
    return "Very strong"


def main():
    ap = argparse.ArgumentParser(description="Password policy + entropy checker")
    ap.add_argument("--min-length", type=int, default=12)
    ap.add_argument("--require-upper", action="store_true", default=True)
    ap.add_argument("--require-lower", action="store_true", default=True)
    ap.add_argument("--require-digit", action="store_true", default=True)
    ap.add_argument("--require-symbol", action="store_true", default=True)
    args = ap.parse_args()

    if sys.stdin.isatty():
        pw = getpass.getpass("Password (hidden): ")
    else:
        pw = sys.stdin.readline().rstrip("\n")

    if not pw:
        sys.exit("[!] No password provided.")

    bits = entropy_bits(pw)
    issues = check(pw, args)
    print(f"Length      : {len(pw)}")
    print(f"Entropy     : ~{bits} bits ({strength(bits)})")
    if issues:
        print("Policy      : FAIL")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    print("Policy      : PASS")


if __name__ == "__main__":
    main()
