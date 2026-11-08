from datetime import date
from database import get_connection

VALID_STATUSES = ('pending', 'in_progress', 'completed')

def create_task(title: str, assignee: str, deadline: str) -> dict:
    """Create a task after user confirmation. deadline is YYYY-MM-DD."""
    if not title or not title.strip() or not assignee or not assignee.strip():
        raise ValueError('Task title and PIC are required')
    parsed = date.fromisoformat(deadline)
    with get_connection() as conn:
        cur = conn.execute('INSERT INTO tasks(title,assignee,deadline) VALUES(?,?,?)',
                           (title.strip(), assignee.strip(), parsed.isoformat()))
        return {'id': cur.lastrowid, 'title': title.strip(), 'assignee': assignee.strip(), 'deadline': parsed.isoformat(), 'status': 'pending'}

def list_tasks(status: str = 'all') -> list[dict]:
    """List stored tasks, optionally filtered by status."""
    if status not in (*VALID_STATUSES, 'all'):
        raise ValueError('Invalid status')
    with get_connection() as conn:
        if status == 'all':
            rows = conn.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
        else:
            rows = conn.execute('SELECT * FROM tasks WHERE status=? ORDER BY id DESC', (status,)).fetchall()
    return [dict(row) for row in rows]

def update_task_status(task_id: int, status: str) -> dict:
    """Update an existing task status by its numeric ID."""
    if status not in VALID_STATUSES:
        raise ValueError('Invalid status')
    with get_connection() as conn:
        cur = conn.execute('UPDATE tasks SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?', (status, task_id))
        if cur.rowcount == 0:
            raise ValueError(f'Task {task_id} not found')
    return {'id': task_id, 'status': status}

def check_overdue() -> list[dict]:
    """List unfinished tasks whose deadlines are before today."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks WHERE deadline < ? AND status != 'completed' ORDER BY deadline", (date.today().isoformat(),)).fetchall()
    return [dict(row) for row in rows]

def task_summary() -> dict:
    """Summarize task counts by status and overdue count."""
    tasks = list_tasks()
    return {'total': len(tasks), **{s: sum(t['status'] == s for t in tasks) for s in VALID_STATUSES}, 'overdue': len(check_overdue())}
