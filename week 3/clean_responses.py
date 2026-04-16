import csv


def clean_responses(input_file: str = "responses.csv", output_file: str = "responses_cleaned.csv") -> None:
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


if __name__ == "__main__":
    clean_responses()
