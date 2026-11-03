// Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
// .NET 6+. Usage:
//   dotnet new console -n BulkCheck && replace Program.cs with this file
//   export WAVALIDATOR_API_KEY=your_key
//   dotnet run 14155551234 14155550000 447911123456

using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

var numbers = args.Length > 0 ? args : new[] { "14155551234", "14155550000", "447911123456" };
var apiKey = Environment.GetEnvironmentVariable("WAVALIDATOR_API_KEY");

using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(90) };
http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

var response = await http.PostAsJsonAsync(
    "https://wavalidator.com/api/v1/bulk-check/",
    new { numbers });

if (!response.IsSuccessStatusCode)
{
    Console.Error.WriteLine($"HTTP {(int)response.StatusCode}: {await response.Content.ReadAsStringAsync()}");
    return 1;
}

var data = await response.Content.ReadFromJsonAsync<BulkResponse>();
foreach (var r in data!.Results)
{
    var label = r.Status switch
    {
        "valid" => "has WhatsApp",
        "invalid" => "no WhatsApp",
        _ => "check failed",
    };
    Console.WriteLine($"{r.Number}: {label}");
}
Console.WriteLine($"Checked {data.Checked}/{data.Total} · credits used {data.CreditsUsed} · remaining {data.CreditsRemaining}");
return 0;

record Result(
    [property: JsonPropertyName("number")] string Number,
    [property: JsonPropertyName("exists")] bool Exists,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("status")] string Status);

record BulkResponse(
    [property: JsonPropertyName("checked")] int Checked,
    [property: JsonPropertyName("invalid")] int Invalid,
    [property: JsonPropertyName("total")] int Total,
    [property: JsonPropertyName("credits_used")] int CreditsUsed,
    [property: JsonPropertyName("credits_remaining")] int CreditsRemaining,
    [property: JsonPropertyName("results")] List<Result> Results);
