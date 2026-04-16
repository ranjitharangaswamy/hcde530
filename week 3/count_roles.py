import csv
from collections import Counter
from pathlib import Path


def normalize_role(role_value: str) -> str:
    """Normalize role text so casing/extra spaces are grouped together."""
    return " ".join((role_value or "").strip().split()).title()


def count_roles(csv_file: str = "responses.csv") -> Counter:
    role_counts: Counter = Counter()
    csv_path = Path(__file__).resolve().parent / csv_file

    with open(csv_path, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            role = normalize_role(row.get("role", ""))
            if role:
                role_counts[role] += 1

    return role_counts


def print_grouped_role_counts(role_counts: Counter) -> None:
    print("Role counts:")
    for role, count in sorted(role_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"- {role}: {count}")


if __name__ == "__main__":
    counts = count_roles("responses.csv")
    print_grouped_role_counts(counts)
