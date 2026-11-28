#!/usr/bin/env bash
set -euo pipefail

# Persistent Dining-Room & Sales Call Feedback Ledger (/dining-room-feedback)
# Scrubs PII (emails/phones), neutralizes spreadsheet formula injection,
# appends to dining-room-ledger.tsv, and prints the cross-session N=1->3->10 + ARR rollup
# along with "The Schmeer" (the unspoken next step).
#
# Usage:
#   bash .claude/skills/head-chef-mode/scripts/log-guest-feedback.sh \
#     [<ledger-file>] <account_tag> <arr_usd> <topic_slug> <mom_test_tier> <say_vs_do> <quote> <the_schmeer>

if [[ "$#" -eq 7 ]]; then
  LEDGER_FILE="${DINING_ROOM_LEDGER:-dining-room-ledger.tsv}"
  ACCOUNT_TAG="$1"
  ARR_USD="$2"
  TOPIC_SLUG="$3"
  MOM_TEST_TIER="$4"
  SAY_VS_DO="$5"
  RAW_QUOTE="$6"
  THE_SCHMEER="$7"
elif [[ "$#" -ge 8 ]]; then
  LEDGER_FILE="$1"
  ACCOUNT_TAG="$2"
  ARR_USD="$3"
  TOPIC_SLUG="$4"
  MOM_TEST_TIER="$5"
  SAY_VS_DO="$6"
  RAW_QUOTE="$7"
  THE_SCHMEER="$8"
else
  echo "Usage: $0 [<ledger-file>] <account_tag> <arr_usd> <topic_slug> <mom_test_tier> <say_vs_do> <quote> <the_schmeer>" >&2
  exit 1
fi

# Coat-Check PII & NDA Scrubber + TSV Formula-Injection Sanitizer
sanitize_and_scrub() {
  local raw="$1"
  local cleaned
  cleaned="$(printf '%s' "$raw" \
    | tr '\t\r\n' '   ' \
    | sed -E 's/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/[REDACTED_EMAIL]/g' \
    | sed -E 's/(\+?[0-9]{1,3}[-. ]+)?\(?[0-9]{3}\)?[-. ][0-9]{3}[-. ][0-9]{4}/[REDACTED_PHONE]/g' \
    | sed -E 's/  +/ /g; s/^ +//; s/ +$//')"
  case "$cleaned" in
    =*|+*|-*|@*)
      cleaned="'$cleaned"
      ;;
  esac
  printf '%s' "$cleaned"
}

NUMERIC_ARR="$(printf '%s' "$ARR_USD" | tr -cd '0-9')"
[[ -z "$NUMERIC_ARR" ]] && NUMERIC_ARR="0"

mkdir -p "$(dirname "$LEDGER_FILE")"
if [[ ! -f "$LEDGER_FILE" ]] || [[ ! -s "$LEDGER_FILE" ]]; then
  printf 'ts\taccount_tag\tarr_usd\ttopic_slug\tmom_test_tier\tsay_vs_do\tscrubbed_quote\tthe_schmeer\n' > "$LEDGER_FILE"
fi

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
C_ACCT="$(sanitize_and_scrub "$ACCOUNT_TAG")"
C_TOPIC="$(sanitize_and_scrub "$TOPIC_SLUG")"
C_TIER="$(sanitize_and_scrub "$MOM_TEST_TIER")"
C_SAYDO="$(sanitize_and_scrub "$SAY_VS_DO")"
C_QUOTE="$(sanitize_and_scrub "$RAW_QUOTE")"
C_SCHMEER="$(sanitize_and_scrub "$THE_SCHMEER")"

printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$TS" "$C_ACCT" "$NUMERIC_ARR" "$C_TOPIC" "$C_TIER" "$C_SAYDO" "$C_QUOTE" "$C_SCHMEER" >> "$LEDGER_FILE"

# Compute cross-session N=1->3->10 distinct account count and total ARR at stake for this topic_slug
DISTINCT_ACCOUNTS="$(awk -F'\t' -v topic="$C_TOPIC" 'NR>1 && $4==topic {accts[$2]=1} END {print length(accts)}' "$LEDGER_FILE")"
TOTAL_ARR="$(awk -F'\t' -v topic="$C_TOPIC" 'NR>1 && $4==topic {sum[$2]=$3} END {tot=0; for (a in sum) tot+=sum[a]; print tot}' "$LEDGER_FILE")"

if (( DISTINCT_ACCOUNTS >= 10 )); then
  GRADUATION_STATUS="GRADUATED_TO_STAGE_B_PRODUCTION_BUILD (N=$DISTINCT_ACCOUNTS >= 10)"
elif (( DISTINCT_ACCOUNTS >= 3 )); then
  GRADUATION_STATUS="PROMOTED_TO_STAGE_A_DISCOVERY_PROBE (N=$DISTINCT_ACCOUNTS >= 3 — Serve /amuse-bouche!)"
else
  GRADUATION_STATUS="QUARANTINED_ONE_OFF (N=$DISTINCT_ACCOUNTS < 3 — Hold menu shield unless Option 1 Garnish takes <=30m)"
fi

echo "================================================================"
echo " DINING-ROOM & SALES-CALL LEDGER ROLLUP: $C_TOPIC"
echo "   Distinct Accounts (N) : $DISTINCT_ACCOUNTS"
echo "   Total ARR at Stake    : \$$TOTAL_ARR"
echo "   Graduation Verdict    : $GRADUATION_STATUS"
echo "   The Schmeer Idea      : $C_SCHMEER"
echo "================================================================"
