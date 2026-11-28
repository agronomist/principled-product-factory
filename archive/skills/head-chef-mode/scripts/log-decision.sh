#!/usr/bin/env bash
set -euo pipefail

# Append-only TSV prep log (/prep-log)
# Usage: scripts/log-decision.sh <logfile> <phase> <decision> <why> <evidence> <result>

if [ "$#" -eq 5 ]; then
  LOGFILE="${DECISIONS_TSV:-decisions.tsv}"
  PHASE="$1"
  DECISION="$2"
  WHY="$3"
  EVIDENCE="$4"
  RESULT="$5"
elif [ "$#" -ge 6 ]; then
  LOGFILE="$1"
  PHASE="$2"
  DECISION="$3"
  WHY="$4"
  EVIDENCE="$5"
  RESULT="$6"
else
  echo "Usage: $0 [<logfile>] <phase> <decision> <why> <evidence> <result>" >&2
  exit 1
fi

sanitize_cell() {
  local raw="$1"
  local cleaned
  cleaned="$(printf '%s' "$raw" | tr '\t\r\n' '   ' | sed -E 's/  +/ /g; s/^ +//; s/ +$//')"
  case "$cleaned" in
    =*|+*|-*|@*)
      cleaned="'$cleaned"
      ;;
  esac
  printf '%s' "$cleaned"
}

mkdir -p "$(dirname "$LOGFILE")"
if [ ! -f "$LOGFILE" ] || [ ! -s "$LOGFILE" ]; then
  printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' > "$LOGFILE"
fi

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
C_PHASE="$(sanitize_cell "$PHASE")"
C_DECISION="$(sanitize_cell "$DECISION")"
C_WHY="$(sanitize_cell "$WHY")"
C_EVIDENCE="$(sanitize_cell "$EVIDENCE")"
C_RESULT="$(sanitize_cell "$RESULT")"

printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$TS" "$C_PHASE" "$C_DECISION" "$C_WHY" "$C_EVIDENCE" "$C_RESULT" >> "$LOGFILE"
