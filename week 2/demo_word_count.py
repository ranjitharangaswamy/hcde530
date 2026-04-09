import csv


# Load responses from the input CSV file into memory.
input_filename = "demo_responses.csv"
responses = []

with open(input_filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        responses.append(row)


def count_words(response: str) -> int:
    """Return number of words in a response string."""
    cleaned = response.strip()
    return len(cleaned.split()) if cleaned else 0


# Print a row-by-row report with ID, word count, and response preview.
print(f"{'ID':<8} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 85)

word_counts = []
results_for_csv = []

for row in responses:
    response_id = row.get("participant_id", f"row_{len(word_counts) + 1}")
    response = row.get("response", "")

    # Count words in each response and store for summary statistics.
    count = count_words(response)
    word_counts.append(count)

    # Build a short response preview for cleaner terminal output.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    print(f"{response_id:<8} {count:<6} {preview}")
    results_for_csv.append(
        {
            "id": response_id,
            "word_count": count,
            "response_preview": preview,
            "response": response,
        }
    )

# Print a summary block with total, shortest, longest, and average counts.
print()
print("── Summary ─────────────────────────────────")
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")

# Stretch goal: write row-level word count results to a new CSV file.
output_filename = "response_word_counts.csv"
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=["id", "word_count", "response_preview", "response"]
    )
    writer.writeheader()
    writer.writerows(results_for_csv)

print(f"\nSaved detailed results to {output_filename}")
