import csv


# Load each row from the input CSV (expects a `response` column; optional `id` or `participant_id`).
input_filename = "demo_responses.csv"
responses: list[dict[str, str]] = []

with open(input_filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        responses.append(row)


def count_words(text: str) -> int:
    """Return number of words in a response string."""
    cleaned = text.strip()
    return len(cleaned.split()) if cleaned else 0


# For each response, compute word count and show ID, count, and a 60-character preview.
print(f"{'ID':<14} {'Words':<6} Response (first 60 chars)")
print("-" * 90)

word_counts: list[int] = []
results_for_csv: list[dict[str, str | int]] = []

for i, row in enumerate(responses, start=1):
    response_id = row.get("id") or row.get("participant_id") or f"row_{i}"
    response = row.get("response", "")

    count = count_words(response)
    word_counts.append(count)

    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    print(f"{str(response_id):<14} {count:<6} {preview}")
    results_for_csv.append(
        {
            "id": response_id,
            "word_count": count,
            "response_preview": preview,
            "response": response,
        }
    )

# Print aggregate stats: how many rows, min/max length, and mean word count.
print()
print("── Summary ─────────────────────────────────")
n = len(word_counts)
print(f"  Total responses : {n}")
if n == 0:
    print("  Shortest        : (no responses)")
    print("  Longest         : (no responses)")
    print("  Average         : (no responses)")
else:
    print(f"  Shortest        : {min(word_counts)} words")
    print(f"  Longest         : {max(word_counts)} words")
    print(f"  Average         : {sum(word_counts) / n:.1f} words")

# Stretch: save the same per-row details plus full text to a new CSV for reuse or charts.
output_filename = "response_word_counts.csv"
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=["id", "word_count", "response_preview", "response"]
    )
    writer.writeheader()
    writer.writerows(results_for_csv)

print(f"\nSaved detailed results to {output_filename}")
