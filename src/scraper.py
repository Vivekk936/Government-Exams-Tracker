import csv
import os

from scrapers.ssc import scrape_ssc
from scrapers.upsc import scrape_upsc
from scrapers.railway import scrape_railway
from scrapers.state_exams import scrape_state_exams

from src.cleaner import clean_exams
from src.database import (
    create_database,
    insert_or_update_exams,
    get_all_exams,
)


CSV_FILE = "data/exams.csv"

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


def save_exams_to_csv(exams):
    """
    Export database records to CSV.
    """

    os.makedirs(
        os.path.dirname(CSV_FILE),
        exist_ok=True
    )

    with open(
        CSV_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()

        writer.writerows(exams)

    print(
        f"[CSV] Exported {len(exams)} records."
    )


def main():

    print("=" * 60)
    print("GOVERNMENT EXAM TRACKER")
    print("=" * 60)

    # -------------------------------------------------
    # 1. Initialize database
    # -------------------------------------------------

    create_database()

    # -------------------------------------------------
    # 2. Run all scrapers
    # -------------------------------------------------

    all_new_exams = []

    print("\n[SCRAPER] Starting all sources...\n")

    try:
        ssc_exams = scrape_ssc()
        all_new_exams.extend(ssc_exams)

    except Exception as error:
        print(
            f"[SSC ERROR] {error}"
        )

    try:
        upsc_exams = scrape_upsc()
        all_new_exams.extend(upsc_exams)

    except Exception as error:
        print(
            f"[UPSC ERROR] {error}"
        )

    try:
        railway_exams = scrape_railway()
        all_new_exams.extend(railway_exams)

    except Exception as error:
        print(
            f"[RAILWAY ERROR] {error}"
        )

    try:
        state_exams = scrape_state_exams()
        all_new_exams.extend(state_exams)

    except Exception as error:
        print(
            f"[STATE ERROR] {error}"
        )

    print(
        f"\n[SCRAPER] New records collected: "
        f"{len(all_new_exams)}"
    )

    # -------------------------------------------------
    # 3. Clean records
    # -------------------------------------------------

    cleaned_exams = clean_exams(
        all_new_exams
    )

    print(
        f"[CLEANER] Clean records: "
        f"{len(cleaned_exams)}"
    )

    # -------------------------------------------------
    # 4. Save to database
    # -------------------------------------------------

    insert_or_update_exams(
        cleaned_exams
    )

    # -------------------------------------------------
    # 5. Read complete database
    # -------------------------------------------------

    all_exams = get_all_exams()

    print(
        f"[DATABASE] Total records: "
        f"{len(all_exams)}"
    )

    # -------------------------------------------------
    # 6. Export database to CSV
    # -------------------------------------------------

    save_exams_to_csv(
        all_exams
    )

    # -------------------------------------------------
    # 7. Final summary
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("SCRAPER COMPLETED")
    print("=" * 60)

    print(
        f"New records: {len(cleaned_exams)}"
    )

    print(
        f"Total database records: "
        f"{len(all_exams)}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()