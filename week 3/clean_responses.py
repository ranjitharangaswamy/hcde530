import csv


def clean_responses(input_file: str = "responses.csv", output_file: str = "responses_cleaned.csv") -> list[dict[str, str]]:
    # Read the raw CSV and prepare to build a cleaned list of rows.
    with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("Input CSV has no header row.")

        # Support both assignment schemas: `name` and `participant_name`.
        name_key = "name" if "name" in fieldnames else "participant_name"

        cleaned_rows = []
        # Loop through each row, drop invalid records, and normalize values we care about.
        for row in reader:
            # Skip rows where the person/name field is empty.
            name_value = (row.get(name_key) or "").strip()
            if not name_value:
                continue

            # Keep only rows where experience_years can be converted to a real integer.
            if "experience_years" in row:
                try:
                    years = int(row["experience_years"])
                except (TypeError, ValueError):
                    continue
                row["experience_years"] = str(years)

            # Normalize role text so grouping/counting is consistent.
            row["role"] = (row.get("role") or "").upper()
            cleaned_rows.append(row)

    # Write the cleaned rows to the output CSV with the original headers.
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    return cleaned_rows


def summarize_data(cleaned_data: list[dict[str, str]]) -> str:
    # Build a plain-language summary of the cleaned dataset.
    row_count = len(cleaned_data)
    unique_roles = sorted({(row.get("role") or "").strip() for row in cleaned_data if (row.get("role") or "").strip()})
    empty_name_count = 0

    # Count any rows that still have an empty name-style field after cleaning.
    for row in cleaned_data:
        name_value = (row.get("name") or row.get("participant_name") or "").strip()
        if not name_value:
            empty_name_count += 1

    return (
        f"Cleaned data has {row_count} rows, {len(unique_roles)} unique roles "
        f"({', '.join(unique_roles) if unique_roles else 'none'}), and {empty_name_count} empty name fields."
    )


if __name__ == "__main__":
    cleaned_rows = clean_responses()
    print(summarize_data(cleaned_rows))
