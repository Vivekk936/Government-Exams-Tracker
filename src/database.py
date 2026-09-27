import os
import sqlite3
from datetime import datetime


DATABASE_FILE = "data/exams.db"


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


def get_connection():
    """
    Create a connection to the SQLite database.
    """

    os.makedirs(
        os.path.dirname(DATABASE_FILE),
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_FILE
    )


def create_database():
    """
    Create the exams table if it does not exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exams (

            id TEXT PRIMARY KEY,

            organization TEXT NOT NULL,

            exam_name TEXT NOT NULL,

            post TEXT,

            vacancies TEXT,

            notification_date TEXT,

            application_start TEXT,

            last_date TEXT,

            exam_date TEXT,

            application_url TEXT,

            notification_url TEXT,

            source TEXT,

            status TEXT,

            last_checked TEXT
        )
        """
    )

    connection.commit()
    connection.close()

    print(
        "[DATABASE] Database initialized."
    )


def insert_or_update_exam(exam):
    """
    Insert a new exam or update an existing exam
    using its stable ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO exams (
            id,
            organization,
            exam_name,
            post,
            vacancies,
            notification_date,
            application_start,
            last_date,
            exam_date,
            application_url,
            notification_url,
            source,
            status,
            last_checked
        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )

        ON CONFLICT(id) DO UPDATE SET

            organization = excluded.organization,
            exam_name = excluded.exam_name,
            post = excluded.post,
            vacancies = excluded.vacancies,
            notification_date = excluded.notification_date,
            application_start = excluded.application_start,
            last_date = excluded.last_date,
            exam_date = excluded.exam_date,
            application_url = excluded.application_url,
            notification_url = excluded.notification_url,
            source = excluded.source,
            status = excluded.status,
            last_checked = excluded.last_checked
        """,
        (
            exam.get("id", ""),
            exam.get("organization", ""),
            exam.get("exam_name", ""),
            exam.get("post", ""),
            exam.get("vacancies", ""),
            exam.get("notification_date", ""),
            exam.get("application_start", ""),
            exam.get("last_date", ""),
            exam.get("exam_date", ""),
            exam.get("application_url", ""),
            exam.get("notification_url", ""),
            exam.get("source", ""),
            exam.get("status", ""),
            exam.get(
                "last_checked",
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
    )

    connection.commit()
    connection.close()


def insert_or_update_exams(exams):
    """
    Insert or update multiple exam records.
    """

    if not exams:
        return

    connection = get_connection()

    cursor = connection.cursor()

    for exam in exams:

        cursor.execute(
            """
            INSERT INTO exams (
                id,
                organization,
                exam_name,
                post,
                vacancies,
                notification_date,
                application_start,
                last_date,
                exam_date,
                application_url,
                notification_url,
                source,
                status,
                last_checked
            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )

            ON CONFLICT(id) DO UPDATE SET

                organization = excluded.organization,
                exam_name = excluded.exam_name,
                post = excluded.post,
                vacancies = excluded.vacancies,
                notification_date = excluded.notification_date,
                application_start = excluded.application_start,
                last_date = excluded.last_date,
                exam_date = excluded.exam_date,
                application_url = excluded.application_url,
                notification_url = excluded.notification_url,
                source = excluded.source,
                status = excluded.status,
                last_checked = excluded.last_checked
            """,
            (
                exam.get("id", ""),
                exam.get("organization", ""),
                exam.get("exam_name", ""),
                exam.get("post", ""),
                exam.get("vacancies", ""),
                exam.get("notification_date", ""),
                exam.get("application_start", ""),
                exam.get("last_date", ""),
                exam.get("exam_date", ""),
                exam.get("application_url", ""),
                exam.get("notification_url", ""),
                exam.get("source", ""),
                exam.get("status", ""),
                exam.get(
                    "last_checked",
                    datetime.now().strftime("%Y-%m-%d")
                ),
            )
        )

    connection.commit()
    connection.close()

    print(
        f"[DATABASE] Saved {len(exams)} records."
    )


def get_all_exams():
    """
    Return every exam in the database.
    """

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM exams
        ORDER BY organization, exam_name
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_exam_by_id(exam_id):
    """
    Find a specific exam by its ID.
    """

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM exams
        WHERE id = ?
        """,
        (exam_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def get_exams_by_source(source):
    """
    Get all exams from a particular source.

    Example:
        get_exams_by_source("SSC")
    """

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM exams
        WHERE source = ?
        ORDER BY exam_name
        """,
        (source,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_database_stats():
    """
    Return basic database statistics.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM exams"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT source, COUNT(*)
        FROM exams
        GROUP BY source
        ORDER BY source
        """
    )

    by_source = cursor.fetchall()

    connection.close()

    return {
        "total": total,
        "by_source": dict(by_source),
    }


def clear_database():
    """
    Delete all records.

    Use carefully.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM exams"
    )

    connection.commit()
    connection.close()

    print(
        "[DATABASE] All records deleted."
    )