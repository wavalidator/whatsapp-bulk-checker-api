// Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
// Java 11+, no dependencies. Usage:
//   export WAVALIDATOR_API_KEY=your_key
//   java BulkCheck.java 14155551234 14155550000 447911123456

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class BulkCheck {
    private static final String API_URL = "https://wavalidator.com/api/v1/bulk-check/";

    public static String bulkCheck(List<String> numbers, String apiKey) throws Exception {
        if (numbers.size() > 100) {
            throw new IllegalArgumentException("Max 100 numbers per request");
        }
        String json = numbers.stream()
                .map(n -> "\"" + n.replaceAll("[^0-9+]", "") + "\"")
                .collect(Collectors.joining(",", "{\"numbers\":[", "]}"));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .timeout(Duration.ofSeconds(90))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpResponse<String> response = HttpClient.newHttpClient()
                .send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("HTTP " + response.statusCode() + ": " + response.body());
        }
        return response.body();
    }

    public static void main(String[] args) throws Exception {
        List<String> numbers = args.length > 0
                ? Arrays.asList(args)
                : List.of("14155551234", "14155550000", "447911123456");

        // Parse with Jackson or Gson in production; the raw JSON is printed here.
        System.out.println(bulkCheck(numbers, System.getenv("WAVALIDATOR_API_KEY")));
    }
}
