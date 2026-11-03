# WhatsApp Bulk Checker API — verify 100 phone numbers per request

[![API docs](https://img.shields.io/badge/docs-wavalidator.com-25D366)](https://wavalidator.com/api-docs/#bulk-check)
[![OpenAPI 3.0](https://img.shields.io/badge/OpenAPI-3.0-6BA539)](openapi.yaml)
[![Status](https://img.shields.io/badge/status-live-brightgreen)](https://wavalidator.com/status/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Official code examples for the **[WA Validator](https://wavalidator.com) bulk WhatsApp number checker**. Send an array of up to **100 phone numbers** and get back, for each one, whether it is registered on WhatsApp — in one synchronous HTTP response.

- **Endpoint:** `POST https://wavalidator.com/api/v1/bulk-check/`
- **Auth:** `Authorization: Bearer YOUR_API_KEY` (or `apikey: YOUR_API_KEY`)
- **Batch size:** 1–100 numbers per request
- **Cost:** 1 credit per number checked; numbers that fail on our side are not charged

> Checking one number at a time? Use the [WhatsApp Number Checker API](https://github.com/wavalidator/whatsapp-number-checker-api).

## Contents

- [What you can do with a bulk WhatsApp checker](#what-you-can-do-with-a-bulk-whatsapp-checker)
- [Request](#request)
- [Response](#response)
- [Code examples](#code-examples)
- [Clean a CSV of phone numbers](#clean-a-csv-of-phone-numbers)
- [Billing rules](#billing-rules)
- [Errors and rate limits](#errors-and-rate-limits)
- [FAQ](#faq)

## What you can do with a bulk WhatsApp checker

- **Clean a WhatsApp marketing list** before a broadcast, so you only pay WhatsApp Business API fees for numbers that can receive the message.
- **Filter WhatsApp numbers from a lead export** (Facebook Lead Ads, Google Ads, trade-show scans, CRM exports).
- **Enrich a CRM** — add a `has_whatsapp` field to every contact in HubSpot, Salesforce, Zoho or Pipedrive.
- **Verify COD orders in bulk** for e-commerce stores before dispatch.
- **Audit an old database** and separate reachable WhatsApp users from dead numbers.

## Request

```http
POST /api/v1/bulk-check/ HTTP/1.1
Host: wavalidator.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "numbers": ["14155551234", "14155550000", "447911123456"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `numbers` | array of strings | yes | 1–100 phone numbers in international format with country code. `+`, spaces and `-` are stripped. |

## Response

```json
{
  "checked": 3,
  "invalid": 0,
  "total": 3,
  "credits_used": 3,
  "credits_remaining": 97,
  "results": [
    { "number": "14155551234",  "exists": true,  "source": "live", "status": "valid" },
    { "number": "14155550000",  "exists": false, "source": "live", "status": "invalid" },
    { "number": "447911123456", "exists": true,  "source": "live", "status": "valid" }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `checked` | integer | Numbers sent to the live WhatsApp check. |
| `invalid` | integer | Numbers rejected by the format check (empty, non-digit, or not 7–15 digits). |
| `total` | integer | Numbers in your request. |
| `credits_used` | integer | Credits charged for this request. |
| `credits_remaining` | integer | Balance after this request. |
| `results[]` | array | One object per number. |
| `results[].number` | string | Normalized number (digits only). |
| `results[].exists` | boolean | `true` if the number is registered on WhatsApp. |
| `results[].status` | string | `valid`, `invalid`, or `error` (check not completed — retry, not charged). |
| `results[].source` | string | `live`, a cache source, or `format_check` when the number was rejected before the live check. |

If your balance runs out mid-batch, the remaining numbers are skipped: compare `results.length` with `total` and resubmit the rest after topping up.

## Code examples

| Language | File |
|---|---|
| cURL / Shell | [`examples/shell/bulk-check.sh`](examples/shell/bulk-check.sh) |
| Python | [`examples/python/bulk_check.py`](examples/python/bulk_check.py) |
| Python — CSV list cleaner | [`examples/python/clean_csv.py`](examples/python/clean_csv.py) |
| Node.js | [`examples/nodejs/bulk-check.mjs`](examples/nodejs/bulk-check.mjs) |
| PHP | [`examples/php/bulk_check.php`](examples/php/bulk_check.php) |
| Go | [`examples/go/main.go`](examples/go/main.go) |
| Java | [`examples/java/BulkCheck.java`](examples/java/BulkCheck.java) |
| C# / .NET | [`examples/csharp/BulkCheck.cs`](examples/csharp/BulkCheck.cs) |

### Python

```python
import os, requests

r = requests.post(
    "https://wavalidator.com/api/v1/bulk-check/",
    headers={"Authorization": f"Bearer {os.environ['WAVALIDATOR_API_KEY']}"},
    json={"numbers": ["14155551234", "14155550000", "447911123456"]},
    timeout=90,
)
for item in r.json()["results"]:
    print(item["number"], "WhatsApp" if item["exists"] else "no WhatsApp")
```

### Node.js

```js
const res = await fetch("https://wavalidator.com/api/v1/bulk-check/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.WAVALIDATOR_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ numbers: ["14155551234", "14155550000", "447911123456"] }),
});
const { results } = await res.json();
results.forEach((r) => console.log(r.number, r.exists ? "WhatsApp" : "no WhatsApp"));
```

## Clean a CSV of phone numbers

[`examples/python/clean_csv.py`](examples/python/clean_csv.py) reads any CSV, checks the phone column 100 numbers at a time, waits when it hits a rate limit, and writes two files: `whatsapp.csv` (numbers with WhatsApp) and `no_whatsapp.csv`.

```bash
pip install requests
export WAVALIDATOR_API_KEY=your_key
python clean_csv.py leads.csv --column phone
```

## Billing rules

- 1 credit per number that gets a `valid` or `invalid` answer from the live check.
- 1 credit per number rejected by the format check (`source: "format_check"`) — clean your list first.
- 0 credits for empty entries and for numbers that come back `status: "error"`.

## Errors and rate limits

| HTTP | Meaning | What to do |
|---|---|---|
| `400` | Invalid JSON, `numbers` not a non-empty array, or more than 100 numbers | Fix the body; split into batches of 100. |
| `401` | Missing or invalid API key | Check the `Authorization` (or `apikey`) header. |
| `402` | Insufficient credits | [Top up](https://wavalidator.com/pricing/). |
| `429` | Rate limit reached — body has `"status": "limit"` | Wait `retry_after` seconds (also in the `Retry-After` header). |
| `5xx` | Server error | Retry with exponential backoff. |

Bulk requests are limited **per minute, per hour and per day**, depending on your plan. A `429` names the window that was hit:

```json
{
  "status": "limit",
  "error": "Rate limit exceeded",
  "message": "Maximum 10 bulk check requests per minute. Try again in 42 seconds.",
  "limit": 10,
  "window": "minute",
  "retry_after": 42
}
```

## FAQ

**How many numbers can I check at once?**
100 per request. For a list of 10,000 numbers, send 100 requests of 100 — [`clean_csv.py`](examples/python/clean_csv.py) does the batching and rate-limit waiting for you.

**Do I need a WhatsApp account or a phone to use the bulk checker?**
No. WA Validator runs the check; you only call the HTTP API.

**Is a message sent to the numbers I check?**
No. The check only reports whether a WhatsApp account exists.

**How long does a 100-number request take?**
The whole batch is answered in one response. Set your HTTP client timeout to at least 90 seconds so large batches are not cut off.

**Can I upload an Excel or Google Sheets file?**
Export it to CSV and run [`clean_csv.py`](examples/python/clean_csv.py), or paste the numbers into the [WA Validator web checker](https://wavalidator.com/validator/) and export the results as CSV — no code needed.

## Related

- [WhatsApp Number Checker API](https://github.com/wavalidator/whatsapp-number-checker-api) — one number per request
- [WhatsApp Checker MCP Server](https://github.com/wavalidator/whatsapp-checker-mcp-server) — bulk checks from Claude, ChatGPT or Cursor
- [Guides and resources](https://github.com/wavalidator/wavalidator-resources)
- [Full API documentation](https://wavalidator.com/api-docs/)

---

Results are point-in-time and are not identity verification or consent to contact. Only check numbers you are authorized to process. WhatsApp is a trademark of Meta Platforms, Inc.; WA Validator is not affiliated with Meta.
