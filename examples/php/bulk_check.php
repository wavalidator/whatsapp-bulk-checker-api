<?php
// Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
// Usage:
//   export WAVALIDATOR_API_KEY=your_key
//   php bulk_check.php 14155551234 14155550000 447911123456

function bulkCheck(array $numbers, string $apiKey): array
{
    if (count($numbers) > 100) {
        throw new InvalidArgumentException('Max 100 numbers per request');
    }

    $ch = curl_init('https://wavalidator.com/api/v1/bulk-check/');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_TIMEOUT => 90,
        CURLOPT_HTTPHEADER => [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json',
        ],
        CURLOPT_POSTFIELDS => json_encode(['numbers' => array_values($numbers)]),
    ]);
    $body = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $result = json_decode($body, true);
    if ($status === 429) {
        sleep($result['retry_after'] ?? 60);
        return bulkCheck($numbers, $apiKey);
    }
    if ($status !== 200) {
        throw new RuntimeException("HTTP $status: " . ($result['error'] ?? $body));
    }
    return $result;
}

$numbers = array_slice($argv, 1) ?: ['14155551234', '14155550000', '447911123456'];
$data = bulkCheck($numbers, getenv('WAVALIDATOR_API_KEY'));

$labels = ['valid' => 'has WhatsApp', 'invalid' => 'no WhatsApp'];
foreach ($data['results'] as $r) {
    echo $r['number'] . ': ' . ($labels[$r['status']] ?? 'check failed') . PHP_EOL;
}
printf("Checked %d/%d · credits used %d · remaining %d\n",
    $data['checked'], $data['total'], $data['credits_used'], $data['credits_remaining']);
