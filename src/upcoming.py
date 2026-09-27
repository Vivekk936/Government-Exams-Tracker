from datetime import datetime

from src.database import get_all_exams


def parse_exam_date(value):
    """
    Convert exam date text into a Python date.
    """

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None


def show_upcoming_exams():

    exams = get_all_exams()

    today = datetime.now().date()

    upcoming = []

    for exam in exams:

        exam_date = parse_exam_date(
            exam.get("exam_date", "")
        )

        if exam_date is None:
            continue

        if exam_date >= today:
            upcoming.append(
                (exam_date, exam)
            )

    upcoming.sort(
        key=lambda item: item[0]
    )

    print()
    print("=" * 100)
    print("UPCOMING GOVERNMENT EXAMS")
    print("=" * 100)

    if not upcoming:
        print("No upcoming exams with valid exam dates found.")
        return

    for exam_date, exam in upcoming:

        print()
        print(
            f"Exam          : "
            f"{exam['exam_name']}"
        )

        print(
            f"Organization  : "
            f"{exam['organization']}"
        )

        print(
            f"Post          : "
            f"{exam['post'] or 'Not specified'}"
        )

        print(
            f"Vacancies     : "
            f"{exam['vacancies'] or 'Not specified'}"
        )

        print(
            f"Exam Date     : "
            f"{exam_date}"
        )

        print(
            f"Last Date     : "
            f"{exam['last_date'] or 'Not specified'}"
        )

        print(
            f"Status        : "
            f"{exam['status']}"
        )

        print(
            f"Application   : "
            f"{exam['application_url']}"
        )

        print("-" * 100)

    print()
    print(
        f"Total upcoming exams: {len(upcoming)}"
    )


if __name__ == "__main__":
    show_upcoming_exams()