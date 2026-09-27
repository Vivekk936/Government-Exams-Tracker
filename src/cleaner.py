import re
from datetime import datetime
from urllib.parse import urljoin, urlparse


FIELDS = [
    "id",
    "organization",
    "exam_name",
    "post",
    "vacancies",
    "notification_date",
    "application_start",
    "last_date",
    "exam_date",
    "application_url",
    "notification_url",
    "source",
    "status",
    "last_checked",
]


# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

def clean_text(value):
    """
    Remove unnecessary whitespace and invisible characters.
    """

    if value is None:
        return ""

    value = str(value)

    # Replace non-breaking spaces
    value = value.replace("\xa0", " ")

    # Remove excessive whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# --------------------------------------------------
# URL CLEANING
# --------------------------------------------------

def clean_url(value, base_url=None):

    value = clean_text(value)

    if not value:
        return ""

    # Convert relative URL into absolute URL
    if base_url:
        value = urljoin(base_url, value)

    parsed = urlparse(value)

    # Reject obviously invalid URLs
    if parsed.scheme not in ["http", "https"]:
        return ""

    if not parsed.netloc:
        return ""

    return value


# --------------------------------------------------
# DATE CLEANING
# --------------------------------------------------

def clean_date(value):

    value = clean_text(value)

    if not value:
        return ""

    # Normalize separators
    value = value.replace(".", "/")
    value = value.replace("-", "/")

    formats = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %Y",
        "%b %Y",
    ]

    for fmt in formats:

        try:

            date = datetime.strptime(
                value,
                fmt
            )

            return date.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    # If we cannot parse it, preserve the
    # original information rather than deleting it.
    return value


# --------------------------------------------------
# VACANCY CLEANING
# --------------------------------------------------

def clean_vacancies(value):

    value = clean_text(value)

    if not value:
        return ""

    # Examples:
    # 10,000 → 10000
    # 10,000+ → 10000+
    # 10000 posts → 10000

    cleaned = value.replace(",", "")

    match = re.search(
        r"\d+(?:\+)?",
        cleaned
    )

    if match:
        return match.group(0)

    return value


# --------------------------------------------------
# STATUS NORMALIZATION
# --------------------------------------------------

def clean_status(value):

    value = clean_text(value).lower()

    if not value:
        return "Unknown"

    status_map = {

        "open": "Open",

        "active": "Open",

        "ongoing": "Open",

        "application open": "Open",

        "upcoming": "Upcoming",

        "scheduled": "Upcoming",

        "published": "Published",

        "closed": "Closed",

        "expired": "Closed",

        "completed": "Completed",

        "cancelled": "Cancelled",

        "canceled": "Cancelled",
    }

    return status_map.get(
        value,
        value.title()
    )


# --------------------------------------------------
# RECORD CLEANING
# --------------------------------------------------

def clean_exam(exam):

    cleaned = {}

    for field in FIELDS:

        cleaned[field] = clean_text(
            exam.get(field, "")
        )

    # Text fields
    cleaned["organization"] = clean_text(
        cleaned["organization"]
    )

    cleaned["exam_name"] = clean_text(
        cleaned["exam_name"]
    )

    cleaned["post"] = clean_text(
        cleaned["post"]
    )

    cleaned["source"] = clean_text(
        cleaned["source"]
    )

    # Dates
    cleaned["notification_date"] = clean_date(
        cleaned["notification_date"]
    )

    cleaned["application_start"] = clean_date(
        cleaned["application_start"]
    )

    cleaned["last_date"] = clean_date(
        cleaned["last_date"]
    )

    cleaned["exam_date"] = clean_date(
        cleaned["exam_date"]
    )

    cleaned["last_checked"] = clean_date(
        cleaned["last_checked"]
    )

    # Vacancy
    cleaned["vacancies"] = clean_vacancies(
        cleaned["vacancies"]
    )

    # Status
    cleaned["status"] = clean_status(
        cleaned["status"]
    )

    # URLs
    cleaned["application_url"] = clean_url(
        cleaned["application_url"]
    )

    cleaned["notification_url"] = clean_url(
        cleaned["notification_url"]
    )

    return cleaned


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def is_valid_exam(exam):

    # Organization is required
    if not exam["organization"]:
        return False

    # Exam name is required
    if not exam["exam_name"]:
        return False

    # Source is required
    if not exam["source"]:
        return False

    return True


# --------------------------------------------------
# DUPLICATE DETECTION
# --------------------------------------------------

def generate_duplicate_key(exam):

    """
    Creates a normalized key used to detect
    duplicates even if two scrapers produce
    slightly different IDs.
    """

    values = [
        exam["organization"],
        exam["exam_name"],
        exam["post"],
    ]

    normalized = "|".join(
        clean_text(value).lower()
        for value in values
    )

    return normalized


def remove_duplicates(exams):

    unique = {}

    duplicates = 0

    for exam in exams:

        key = generate_duplicate_key(
            exam
        )

        if key in unique:

            duplicates += 1

            # Prefer the newer/more complete
            # record.
            existing = unique[key]

            for field in FIELDS:

                if (
                    not existing.get(field)
                    and exam.get(field)
                ):
                    existing[field] = exam[field]

        else:

            unique[key] = exam

    print(
        f"[CLEANER] Removed "
        f"{duplicates} duplicates."
    )

    return list(
        unique.values()
    )


# --------------------------------------------------
# COMPLETE CLEANING PIPELINE
# --------------------------------------------------

def clean_exams(exams):

    print(
        f"[CLEANER] Received "
        f"{len(exams)} records."
    )

    cleaned_exams = []

    invalid = 0

    for exam in exams:

        cleaned = clean_exam(exam)

        if not is_valid_exam(cleaned):

            invalid += 1

            continue

        cleaned_exams.append(
            cleaned
        )

    print(
        f"[CLEANER] Invalid records removed: "
        f"{invalid}"
    )

    cleaned_exams = remove_duplicates(
        cleaned_exams
    )

    # Sort by organization then exam name
    cleaned_exams.sort(
        key=lambda exam: (
            exam["organization"].lower(),
            exam["exam_name"].lower()
        )
    )

    print(
        f"[CLEANER] Final records: "
        f"{len(cleaned_exams)}"
    )

    return cleaned_exams