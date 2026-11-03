#!/usr/bin/env sh
# Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
# Usage:
#   export WAVALIDATOR_API_KEY=your_key
#   ./bulk-check.sh 14155551234 14155550000 447911123456

if [ "$#" -eq 0 ]; then
  set -- 14155551234 14155550000 447911123456
fi

NUMBERS=$(printf '"%s",' "$@")
NUMBERS="[${NUMBERS%,}]"

curl -sS -X POST "https://wavalidator.com/api/v1/bulk-check/" \
  -H "Authorization: Bearer ${WAVALIDATOR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"numbers\": ${NUMBERS}}"
echo
