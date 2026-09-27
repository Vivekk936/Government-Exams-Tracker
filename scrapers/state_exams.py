import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup


STATE_PSC_SOURCES = {

    "Uttarakhand": {
        "organization": "Uttarakhand Public Service Commission",
        "url": "https://psc.uk.gov.in/"
    },

    "Bihar": {
        "organization": "Bihar Public Service Commission",
        "url": "https://www.bpsc.bih.nic.in/"
    },

    "Madhya Pradesh": {
        "organization": "Madhya Pradesh Public Service Commission",
        "url": "https://mppsc.mp.gov.in/"
    },

    "Rajasthan": {
        "organization": "Rajasthan Public Service Commission",
        "url": "https://rpsc.rajasthan.gov.in/"
    },

    "Uttar Pradesh": {
        "organization": "Uttar Pradesh Public Service Commission",
        "url": "https://uppsc.up.nic.in/"
    },
}


def generate_id(exam):

    unique_string = "|".join([
        exam["organization"],
        exam["exam_name"],
        exam["post"],
    ])

    return hashlib.sha256(
        unique_string.encode("utf-8")
    ).hexdigest()[:16]


def scrape_state_source(
    state,
    organization,
    url
):

    print(
        f"[STATE] Checking {state}..."
    )

    try:

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Government Exam Tracker)"
                )
            }
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print(
            f"[STATE] {state} failed: {error}"
        )

        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    exams = []

    # We intentionally don't treat every link
    # as an exam. This is a first-stage collector.
    for link in soup.find_all("a"):

        text = link.get_text(
            " ",
            strip=True
        )

        href = link.get(
            "href",
            ""
        )

        if not text:
            continue

        keywords = [
            "recruitment",
            "notification",
            "advertisement",
            "examination",
            "exam",
            "vacancy",
            "recruit",
        ]

        if not any(
            keyword in text.lower()
            for keyword in keywords
        ):
            continue

        exam = {
            "id": "",
            "organization": organization,
            "exam_name": text,
            "post": "",
            "notification_date": "",
            "last_date": "",
            "exam_date": "",
            "application_url": url,
            "notification_url": href,
            "source": state,
            "status": "Published",
            "last_checked": datetime.now().strftime(
                "%Y-%m-%d"
            ),
        }

        exam["id"] = generate_id(exam)

        exams.append(exam)

    return exams


def scrape_state_exams():

    all_exams = []

    for state, config in STATE_PSC_SOURCES.items():

        exams = scrape_state_source(
            state,
            config["organization"],
            config["url"]
        )

        all_exams.extend(exams)

    # Deduplicate
    unique = {}

    for exam in all_exams:
        unique[exam["id"]] = exam

    all_exams = list(unique.values())

    print(
        f"[STATE] Found "
        f"{len(all_exams)} records."
    )

    return all_exams