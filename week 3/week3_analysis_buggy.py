import csv


def parse_int(value):
    """Parse numeric strings and simple number words (e.g., 'fifteen')."""
    text = (value or "").strip().lower()
    if not text:
        return None

    if text.isdigit():
        return int(text)

    word_to_num = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
    }
    return word_to_num.get(text)


def clean_role(value):
    """Normalize role values and return None for empty roles."""
    role = (value or "").strip().title()
    if not role:
        return None
    return role


def participant_score_details(row):
    """Return score fields for a row, or None if name/satisfaction/years are missing or invalid."""
    name = (row.get("participant_name") or "").strip()
    role = clean_role(row.get("role")) or "Unknown Role"
    satisfaction = parse_int(row.get("satisfaction_score"))
    years = parse_int(row.get("experience_years"))

    if not name or satisfaction is None or years is None:
        return None

    score = (satisfaction * 20) + years
    summary = (
        f"{name} ({role}) score: {score} - satisfaction {satisfaction}/5 with {years} years experience."
    )
    return {
        "participant_score": score,
        "summary": summary,
    }


def participant_score_summary(row):
    """Calculate a participant score from satisfaction + experience and return a one-line summary."""
    details = participant_score_details(row)
    return details["summary"] if details else None


def write_participant_scores_csv(rows, output_file="participant_scores_cleaned.csv"):
    """Write rows with computed participant_score and summary to a new CSV file."""
    if not rows:
        return

    base_fieldnames = list(rows[0].keys())
    extra = ["participant_score", "summary"]
    fieldnames = base_fieldnames + [c for c in extra if c not in base_fieldnames]

    cleaned_out = []
    for row in rows:
        details = participant_score_details(row)
        if details is None:
            continue
        out_row = {k: row.get(k, "") for k in base_fieldnames}
        out_row["participant_score"] = details["participant_score"]
        out_row["summary"] = details["summary"]
        cleaned_out.append(out_row)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cleaned_out)


# Load the survey data from a CSV file
filename = "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

for row in rows:
    role = clean_role(row.get("role"))
    if role is None:
        continue
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
valid_experience_count = 0
for row in rows:
    years = parse_int(row.get("experience_years"))
    if years is not None:
        total_experience += years
        valid_experience_count += 1

avg_experience = total_experience / valid_experience_count
print(f"\nAverage years of experience: {avg_experience:.1f}")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in rows:
    score = parse_int(row.get("satisfaction_score"))
    name = (row.get("participant_name") or "").strip()
    if score is not None and name:
        scored_rows.append((name, score))

# Sort highest-to-lowest so the first 5 are truly the top scores.
scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]

print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")

print("\nParticipant score summaries:")
for row in rows:
    summary = participant_score_summary(row)
    if summary is not None:
        print(f"  {summary}")

write_participant_scores_csv(rows, "participant_scores_cleaned.csv")
print("\nWrote cleaned participant scores to participant_scores_cleaned.csv")
