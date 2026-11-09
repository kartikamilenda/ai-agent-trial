
from datetime import date
from uuid import UUID

from database import get_connection


VALID_STATUSES = (
    "pending",
    "in_progress",
    "completed"
)


def create_task(
    title: str,
    assignee: str,
    deadline: str,
    source_item_id: str | None = None
) -> dict:
    """Create a task with optional idempotency key."""

    if not isinstance(title, str) or len(title.strip()) < 3:
        raise ValueError("Valid task title is required")

    if not isinstance(assignee, str) or not assignee.strip():
        raise ValueError("PIC is required")

    if not isinstance(deadline, str):
        raise ValueError("Deadline must be YYYY-MM-DD")

    try:
        parsed_deadline = date.fromisoformat(deadline)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid deadline") from exc

    if parsed_deadline.isoformat() != deadline:
        raise ValueError("Deadline must be YYYY-MM-DD")

    title = title.strip()
    assignee = assignee.strip()
    deadline = parsed_deadline.isoformat()

    if source_item_id is not None:
        try:
            source_item_id = str(UUID(source_item_id))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("Invalid source_item_id") from exc

    with get_connection() as conn:

        if source_item_id:
            existing = conn.execute(
                """
                SELECT * FROM tasks
                WHERE source_item_id = ?
                """,
                (source_item_id,)
            ).fetchone()

            if existing:
                if (
                    existing["title"] != title
                    or existing["assignee"] != assignee
                    or existing["deadline"] != deadline
                ):
                    raise ValueError(
                        "source_item_id already belongs "
                        "to a different task"
                    )

                return dict(existing)

        cur = conn.execute(
            """
            INSERT INTO tasks (
                title,
                assignee,
                deadline,
                source_item_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (title, assignee, deadline, source_item_id)
        )

        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (cur.lastrowid,)
        ).fetchone()

        return dict(row)


def list_tasks(status: str = "all") -> list[dict]:
    """List tasks, optionally filtered by status."""

    if status not in (*VALID_STATUSES, "all"):
        raise ValueError("Invalid status")

    with get_connection() as conn:
        if status == "all":
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY id DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,)
            ).fetchall()

    return [dict(row) for row in rows]


def update_task_status(
    task_id: int,
    status: str
) -> dict:
    """Update task status by numeric ID."""

    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
    ):
        raise ValueError("Invalid task ID")

    if status not in VALID_STATUSES:
        raise ValueError("Invalid status")

    with get_connection() as conn:
        cur = conn.execute(
            """
            UPDATE tasks
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, task_id)
        )

        if cur.rowcount == 0:
            raise ValueError(
                f"Task {task_id} not found"
            )

    return {"id": task_id, "status": status}


def check_overdue() -> list[dict]:
    """List unfinished tasks overdue as of today."""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE deadline < ?
              AND status != 'completed'
            ORDER BY deadline
            """,
            (date.today().isoformat(),)
        ).fetchall()

    return [dict(row) for row in rows]


def task_summary() -> dict:
    """Summarize counts by status and overdue."""

    tasks = list_tasks()

    return {
        "total": len(tasks),
        **{
            status: sum(
                task["status"] == status
                for task in tasks
            )
            for status in VALID_STATUSES
        },
        "overdue": len(check_overdue())
    }
