import hashlib
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


UPSC_ARCHIVE_URL = (
    "https://www.upsc.gov.in/"
    "exams-related-info/exam-notification/archives"
)


def generate_id(exam):
    unique_string = "|".join([
        exam["organization"],
        exam["exam_name"],
        exam["post"],
    ])

    return hashlib.sha256(
        unique_string.encode("utf-8")
    ).hexdigest()[:16]


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def scrape_upsc():

    print("[UPSC] Starting scraper...")

    response = requests.get(
        UPSC_ARCHIVE_URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Government Exam Tracker)"
            )
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    exams = []

    # UPSC pages may change their HTML structure.
    # We look for headings/blocks containing
    # examination information.

    text = soup.get_text("\n")

    lines = [
        clean_text(line)
        for line in text.splitlines()
        if clean_text(line)
    ]

    for index, line in enumerate(lines):

        if "Examination" not in line:
            continue

        if len(line) < 10:
            continue

        exam_name = line

        # Avoid navigation/menu text
        if any(skip in exam_name for skip in [
            "Examination Notifications",
            "Previous Question Papers",
            "Active Examinations",
        ]):
            continue

        exam = {
            "id": "",
            "organization": "Union Public Service Commission",
            "exam_name": exam_name,
            "post": "",
            "notification_date": "",
            "last_date": "",
            "exam_date": "",
            "application_url": "https://upsconline.nic.in",
            "notification_url": UPSC_ARCHIVE_URL,
            "source": "UPSC",
            "status": "Published",
            "last_checked": datetime.now().strftime("%Y-%m-%d"),
        }

        exam["id"] = generate_id(exam)

        exams.append(exam)

    # Remove duplicates
    unique = {}

    for exam in exams:
        unique[exam["id"]] = exam

    exams = list(unique.values())

    print(f"[UPSC] Found {len(exams)} records.")

    return exams