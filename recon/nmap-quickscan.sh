#!/usr/bin/env bash
#
# nmap-quickscan.sh — structured Nmap sweep with organised output
# Author : Alexandre Rocha (github.com/RochaCrypt)
# License: MIT
#
# PURPOSE
#   Run a consistent, repeatable Nmap workflow and save results in a tidy,
#   timestamped folder: host discovery -> open ports -> service/version.
#
# AUTHORISED USE ONLY
#   Only scan systems you own or are explicitly authorised to test.
#
# REQUIREMENTS: nmap
# USAGE:  ./nmap-quickscan.sh <target|CIDR> [output_dir]
# EXAMPLE:./nmap-quickscan.sh 10.0.0.0/24
#
set -euo pipefail

TARGET="${1:-}"
OUTDIR="${2:-scan_$(date +%Y%m%d_%H%M%S)}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <target|CIDR> [output_dir]"
  exit 1
fi
if ! command -v nmap >/dev/null 2>&1; then
  echo "[!] nmap is not installed."
  exit 1
fi

echo "[*] Authorised scan of: $TARGET"
echo "[*] Output directory  : $OUTDIR"
mkdir -p "$OUTDIR"

echo "[1/3] Host discovery..."
nmap -sn "$TARGET" -oG "$OUTDIR/discovery.gnmap" >/dev/null
LIVE=$(awk '/Up$/{print $2}' "$OUTDIR/discovery.gnmap")
echo "$LIVE" | sed '/^$/d' > "$OUTDIR/live-hosts.txt"
COUNT=$(grep -c . "$OUTDIR/live-hosts.txt" || true)
echo "      -> $COUNT live host(s)"

echo "[2/3] Port + service scan per host..."
while read -r host; do
  [[ -z "$host" ]] && continue
  echo "      - $host"
  nmap -sV -sC -T4 "$host" -oN "$OUTDIR/host_${host}.txt" >/dev/null
done < "$OUTDIR/live-hosts.txt"

echo "[3/3] Building summary..."
{
  echo "Nmap quickscan summary — $(date)"
  echo "Target: $TARGET"
  echo "Live hosts: $COUNT"
  echo "----------------------------------------"
  for f in "$OUTDIR"/host_*.txt; do
    [[ -e "$f" ]] || continue
    echo ""; echo "### $(basename "$f" .txt | sed 's/host_//')"
    grep -E "^[0-9]+/tcp" "$f" || echo "  (no open TCP ports found)"
  done
} > "$OUTDIR/summary.txt"

echo "[+] Done. See: $OUTDIR/summary.txt"
