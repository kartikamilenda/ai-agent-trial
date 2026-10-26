
import os
import tempfile
import unittest
from unittest.mock import patch

import database
from database import init_database
from tools import (
    create_task,
    list_tasks,
    update_task_status
)


class TestAgentTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(
            self.temp_dir.name, "test_tasks.db"
        )
        self.db_patch = patch.object(
            database, "DB_PATH", self.db_file
        )
        self.db_patch.start()
        init_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_create_task(self):
        result = create_task(
            "Implement API",
            "Andi"
        )
        self.assertIn("Created task", result)

    def test_list_pending_tasks(self):
        create_task("Implement API", "Andi")
        result = list_tasks("pending")
        self.assertIn("Implement API", result)

    def test_update_task(self):
        create_task("Implement API", "Andi")
        result = update_task_status(1, "completed")
        self.assertIn("completed", result)

    def test_invalid_status(self):
        result = update_task_status(1, "deleted")
        self.assertIn("ERROR", result)

    def test_missing_task(self):
        result = update_task_status(999, "completed")
        self.assertIn("not found", result)


if __name__ == "__main__":
    unittest.main()
