import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import closing
import os
DB_NAME = os.getenv("DB_NAME","cases.db")

TEAM_ROUTING = {
    "billing": "billing_team",
    "network": "network_team",
    "technical": "technical_support_team",
}


def initialize_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    assigned_team TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)


def create_case(description: str, category: str) -> dict:

    category = category.strip().lower()
    description = description.strip()

    if not description:
        raise ValueError("Description cannot be empty")

    if category not in TEAM_ROUTING:
        raise ValueError(
            f"Unsupported category: {category}. "
            f"Choose from {list(TEAM_ROUTING.keys())}"
        )

    case = {
        "case_id": str(uuid.uuid4()),
        "description": description,
        "category": category,
        "assigned_team": TEAM_ROUTING[category],
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO cases
                (case_id, description, category, assigned_team, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    case["case_id"],
                    case["description"],
                    case["category"],
                    case["assigned_team"],
                    case["status"],
                    case["created_at"],
                ),
            )

    return case


def get_case(case_id: str) -> dict | None:

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT *
                FROM cases
                WHERE case_id = ?
                """,
                (case_id,),
            ).fetchone()

    return dict(row) if row else None