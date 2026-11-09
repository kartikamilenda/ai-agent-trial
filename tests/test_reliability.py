
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import database

from database import init_database
from tools.task_tools import (
    create_task,
    list_tasks,
    update_task_status,
    check_overdue,
    task_summary,
)


class TestReliability(unittest.TestCase):

    def setUp(self):
        # Isolated temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.db_patch = patch.object(
            database,
            "DB_PATH",
            self.db_path
        )

        self.db_patch.start()
        init_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_overdue_detection(self):
        yesterday = (
            date.today() - timedelta(days=1)
        ).isoformat()

        task = create_task(
            "Perbaiki dokumentasi API",
            "Andi",
            yesterday
        )

        overdue = check_overdue()

        self.assertEqual(len(overdue), 1)
        self.assertEqual(
            overdue[0]["id"],
            task["id"]
        )
        self.assertEqual(
            task_summary()["overdue"],
            1
        )

    def test_completed_task_not_overdue(self):
        yesterday = (
            date.today() - timedelta(days=1)
        ).isoformat()

        task = create_task(
            "Perbaiki dokumentasi API",
            "Andi",
            yesterday
        )

        update_task_status(
            task["id"],
            "completed"
        )

        self.assertEqual(check_overdue(), [])
        self.assertEqual(
            task_summary()["completed"],
            1
        )
        self.assertEqual(
            task_summary()["overdue"],
            0
        )

    def test_invalid_task_id(self):
        with self.assertRaises(ValueError):
            update_task_status(
                999999,
                "completed"
            )

        self.assertEqual(list_tasks(), [])

    def test_invalid_status(self):
        task = create_task(
            "Implementasi login",
            "Budi",
            "2027-01-10"
        )

        with self.assertRaises(ValueError):
            update_task_status(
                task["id"],
                "deleted"
            )

        stored = list_tasks()

        self.assertEqual(len(stored), 1)
        self.assertEqual(
            stored[0]["status"],
            "pending"
        )

    def test_invalid_deadline(self):
        with self.assertRaises(ValueError):
            create_task(
                "Implementasi login",
                "Budi",
                "2026-13-40"
            )

        self.assertEqual(list_tasks(), [])

    def test_missing_assignee(self):
        with self.assertRaises(ValueError):
            create_task(
                "Implementasi login",
                "",
                "2027-01-10"
            )

        self.assertEqual(list_tasks(), [])


if __name__ == "__main__":
    unittest.main()
