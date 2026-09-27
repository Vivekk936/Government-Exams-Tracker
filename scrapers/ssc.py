import hashlib
import re
from datetime import datetime

import pdfplumber
import requests


SSC_CALENDAR_URL = (
    "https://ssc.gov.in/api/attachment/uploads/masterData/"
    "ExamCalendar/Tentative_Calendar2026_27_08012026.pdf"
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


def download_calendar():
    response = requests.get(
        SSC_CALENDAR_URL,
        timeout=30
    )

    response.raise_for_status()

    return response.content


def scrape_ssc():
    print("[SSC] Starting scraper...")

    pdf_data = download_calendar()

    exams = []

    with open("ssc_calendar_temp.pdf", "wb") as file:
        file.write(pdf_data)

    with pdfplumber.open("ssc_calendar_temp.pdf") as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if not table:
                continue

            for row in table:

                if not row or len(row) < 5:
                    continue

                # Skip header
                if str(row[0]).strip() in ["S. No.", "S.No."]:
                    continue

                serial = clean_text(str(row[0] or ""))
                exam_name = clean_text(str(row[1] or ""))
                advertisement = clean_text(str(row[3] or ""))
                closing = clean_text(str(row[4] or ""))
                exam_date = clean_text(str(row[5] or ""))

                if not serial.isdigit():
                    continue

                if not exam_name:
                    continue

                exam = {
                    "id": "",
                    "organization": "Staff Selection Commission",
                    "exam_name": exam_name,
                    "post": "",
                    "notification_date": advertisement,
                    "last_date": closing,
                    "exam_date": exam_date,
                    "application_url": "https://ssc.gov.in",
                    "notification_url": SSC_CALENDAR_URL,
                    "source": "SSC",
                    "status": "Upcoming",
                    "last_checked": datetime.now().strftime("%Y-%m-%d"),
                }

                exam["id"] = generate_id(exam)

                exams.append(exam)

    print(f"[SSC] Found {len(exams)} exams.")

    return exams