
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database

from database import init_database
from tools.task_tools import (
    create_task,
    list_tasks,
    update_task_status
)


class TestAgentTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.db_file = (
            Path(self.temp_dir.name) / "test_tasks.db"
        )

        self.db_patch = patch.object(
            database,
            "DB_PATH",
            self.db_file
        )

        self.db_patch.start()
        init_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_create_task(self):
        result = create_task(
            "Implement API",
            "Andi",
            "2026-11-12"
        )

        self.assertEqual(
            result["title"],
            "Implement API"
        )
        self.assertEqual(
            result["assignee"],
            "Andi"
        )
        self.assertEqual(
            result["status"],
            "pending"
        )

    def test_list_pending_tasks(self):
        create_task(
            "Implement API",
            "Andi",
            "2026-11-12"
        )

        result = list_tasks("pending")

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["title"],
            "Implement API"
        )

    def test_update_task(self):
        task = create_task(
            "Implement API",
            "Andi",
            "2026-11-12"
        )

        result = update_task_status(
            task["id"],
            "completed"
        )

        self.assertEqual(
            result["status"],
            "completed"
        )

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            update_task_status(
                1,
                "deleted"
            )

    def test_missing_task(self):
        with self.assertRaises(ValueError):
            update_task_status(
                999,
                "completed"
            )


if __name__ == "__main__":
    unittest.main()
