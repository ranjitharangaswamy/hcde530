import csv


def clean_responses(input_file: str = "responses.csv", output_file: str = "responses_cleaned.csv") -> list[dict[str, str]]:
    with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("Input CSV has no header row.")

        # Support both assignment schemas: `name` and `participant_name`.
        name_key = "name" if "name" in fieldnames else "participant_name"

        cleaned_rows = []
        for row in reader:
            name_value = (row.get(name_key) or "").strip()
            if not name_value:
                continue

            if "experience_years" in row:
                try:
                    years = int(row["experience_years"])
                except (TypeError, ValueError):
                    continue
                row["experience_years"] = str(years)

            row["role"] = (row.get("role") or "").upper()
            cleaned_rows.append(row)

    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    return cleaned_rows


def summarize_data(cleaned_data: list[dict[str, str]]) -> str:
    row_count = len(cleaned_data)
    unique_roles = sorted({(row.get("role") or "").strip() for row in cleaned_data if (row.get("role") or "").strip()})
    empty_name_count = 0

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
