
from database import get_connection


def create_task(title: str, assignee: str) -> str:
    """Create a new task.

    Args:
        title: Description of the task.
        assignee: Person responsible for the task.
    """
    if not title.strip() or not assignee.strip():
        return "ERROR: title and assignee are required."

    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO tasks (title, assignee)
               VALUES (?, ?)""",
            (title, assignee)
        )
        task_id = cursor.lastrowid

    return f"Created task ID {task_id}: {title} for {assignee}"


def list_tasks(status: str = "all") -> str:
    """List tasks filtered by status.

    Args:
        status: One of all, pending, or completed.
    """
    if status not in ("all", "pending", "completed"):
        return "ERROR: Invalid status."

    with get_connection() as conn:
        if status == "all":
            rows = conn.execute(
                "SELECT id, title, assignee, status FROM tasks"
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, title, assignee, status
                   FROM tasks WHERE status = ?""",
                (status,)
            ).fetchall()

    if not rows:
        return "No tasks found."

    return "\n".join(
        f"ID={r[0]} | {r[1]} | PIC={r[2]} | {r[3]}"
        for r in rows
    )


def update_task_status(task_id: int, status: str) -> str:
    """Update the status of an existing task.

    Args:
        task_id: Numeric task identifier.
        status: New status, pending or completed.
    """
    if status not in ("pending", "completed"):
        return "ERROR: Invalid status."

    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )

        if cursor.rowcount == 0:
            return f"ERROR: Task ID {task_id} not found."

    return f"Updated task {task_id} to {status}."
