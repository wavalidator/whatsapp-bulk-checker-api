// Check up to 100 phone numbers for WhatsApp in one request (WA Validator bulk API).
// Usage:
//
//	export WAVALIDATOR_API_KEY=your_key
//	go run main.go 14155551234 14155550000 447911123456
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

const apiURL = "https://wavalidator.com/api/v1/bulk-check/"

type Result struct {
	Number string `json:"number"`
	Exists bool   `json:"exists"`
	Source string `json:"source"`
	Status string `json:"status"`
}

type BulkResponse struct {
	Checked          int      `json:"checked"`
	Invalid          int      `json:"invalid"`
	Total            int      `json:"total"`
	CreditsUsed      int      `json:"credits_used"`
	CreditsRemaining int      `json:"credits_remaining"`
	Results          []Result `json:"results"`
}

func BulkCheck(numbers []string, apiKey string) (*BulkResponse, error) {
	if len(numbers) > 100 {
		return nil, fmt.Errorf("max 100 numbers per request")
	}
	body, _ := json.Marshal(map[string][]string{"numbers": numbers})
	req, err := http.NewRequest(http.MethodPost, apiURL, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 90 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var data BulkResponse
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return nil, err
	}
	return &data, nil
}

func main() {
	numbers := os.Args[1:]
	if len(numbers) == 0 {
		numbers = []string{"14155551234", "14155550000", "447911123456"}
	}

	data, err := BulkCheck(numbers, os.Getenv("WAVALIDATOR_API_KEY"))
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	for _, r := range data.Results {
		label := "check failed"
		switch r.Status {
		case "valid":
			label = "has WhatsApp"
		case "invalid":
			label = "no WhatsApp"
		}
		fmt.Printf("%s: %s\n", r.Number, label)
	}
	fmt.Printf("Checked %d/%d · credits used %d · remaining %d\n",
		data.Checked, data.Total, data.CreditsUsed, data.CreditsRemaining)
}
