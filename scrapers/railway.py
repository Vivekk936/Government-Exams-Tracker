import hashlib
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


RRB_ALP_URL = (
    "https://www.rrbcdg.gov.in/2026-01-alp.php"
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


def scrape_railway():

    print("[RAILWAY] Starting scraper...")

    response = requests.get(
        RRB_ALP_URL,
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

    tables = soup.find_all("table")

    for table in tables:

        rows = table.find_all("tr")

        for row in rows:

            cells = row.find_all(
                ["td", "th"]
            )

            if len(cells) < 2:
                continue

            date = clean_text(
                cells[0].get_text(" ")
            )

            notice = clean_text(
                cells[1].get_text(" ")
            )

            if not notice:
                continue

            if "Employment Notice" not in notice:
                continue

            exam = {
                "id": "",
                "organization": "Railway Recruitment Board",
                "exam_name": "RRB ALP 2026",
                "post": "Assistant Loco Pilot",
                "notification_date": date,
                "last_date": "",
                "exam_date": "",
                "application_url": RRB_ALP_URL,
                "notification_url": RRB_ALP_URL,
                "source": "RRB",
                "status": "Published",
                "last_checked": datetime.now().strftime("%Y-%m-%d"),
            }

            exam["id"] = generate_id(exam)

            exams.append(exam)

    unique = {}

    for exam in exams:
        unique[exam["id"]] = exam

    exams = list(unique.values())

    print(
        f"[RAILWAY] Found {len(exams)} records."
    )

    return exams