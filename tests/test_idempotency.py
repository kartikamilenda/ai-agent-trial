import os
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import patch

import database
from database import init_database
from tools.task_tools import create_task, list_tasks


class TestTaskIdempotency(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.db_path = os.path.join(
            self.temp_dir.name,
            "test_tasks.db"
        )

        self.db_patch = patch.object(
            database,
            "DB_PATH",
            database.DB_PATH.__class__(self.db_path)
        )

        self.db_patch.start()
        init_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_same_item_is_not_duplicated(self):
        item_id = str(uuid4())

        first = create_task(
            "Implementasi API",
            "Andi",
            "2026-11-12",
            source_item_id=item_id
        )

        second = create_task(
            "Implementasi API",
            "Andi",
            "2026-11-12",
            source_item_id=item_id
        )

        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(list_tasks()), 1)

    def test_same_title_different_ids(self):
        first = create_task(
            "Implementasi API",
            "Andi",
            "2026-11-12",
            source_item_id=str(uuid4())
        )

        second = create_task(
            "Implementasi API",
            "Andi",
            "2026-11-12",
            source_item_id=str(uuid4())
        )

        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(len(list_tasks()), 2)

    def test_same_id_different_data_rejected(self):
        item_id = str(uuid4())

        create_task(
            "Implementasi API",
            "Andi",
            "2026-11-12",
            source_item_id=item_id
        )

        with self.assertRaises(ValueError):
            create_task(
                "Membuat Dashboard",
                "Sinta",
                "2026-11-15",
                source_item_id=item_id
            )


if __name__ == "__main__":
    unittest.main()
