// Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
// Node.js 18+ (built-in fetch). Usage:
//   export WAVALIDATOR_API_KEY=your_key
//   node bulk-check.mjs 14155551234 14155550000 447911123456

const API_URL = "https://wavalidator.com/api/v1/bulk-check/";
const MAX_BATCH = 100;

export async function bulkCheck(numbers, apiKey, retries = 3) {
  if (numbers.length > MAX_BATCH) throw new Error(`Max ${MAX_BATCH} numbers per request`);

  for (let attempt = 0; attempt < retries; attempt++) {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ numbers }),
    });

    if (res.status === 429) {
      const body = await res.json();
      await new Promise((r) => setTimeout(r, (body.retry_after ?? 60) * 1000));
      continue;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  }
  throw new Error("Rate limit still reached after retries");
}

// Split any list into batches of 100 and check them one after another.
export async function bulkCheckAll(numbers, apiKey) {
  const results = [];
  for (let i = 0; i < numbers.length; i += MAX_BATCH) {
    const data = await bulkCheck(numbers.slice(i, i + MAX_BATCH), apiKey);
    results.push(...data.results);
  }
  return results;
}

const numbers = process.argv.slice(2);
const data = await bulkCheck(
  numbers.length ? numbers : ["14155551234", "14155550000", "447911123456"],
  process.env.WAVALIDATOR_API_KEY,
);

for (const r of data.results) {
  const label = { valid: "has WhatsApp", invalid: "no WhatsApp" }[r.status] ?? "check failed";
  console.log(`${r.number}: ${label}`);
}
console.log(`Checked ${data.checked}/${data.total} · credits used ${data.credits_used} · remaining ${data.credits_remaining}`);
