import os
import tempfile
import unittest
from pathlib import Path

class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        import config
        config.DB_PATH = Path(cls.tmp.name) / 'test.db'
        from database import init_database
        init_database()

    def setUp(self):
        from database import get_connection
        with get_connection() as conn:
            conn.execute("DELETE FROM tasks")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_task_lifecycle(self):
        from tools.task_tools import create_task, list_tasks, update_task_status, task_summary
        created = create_task('Implement API login', 'Andi', '2027-01-10')
        self.assertEqual(created['status'], 'pending')
        self.assertEqual(len(list_tasks()), 1)
        self.assertEqual(update_task_status(created['id'], 'completed')['status'], 'completed')
        self.assertEqual(task_summary()['completed'], 1)

    def test_validation(self):
        from models import ActionItem
        item = ActionItem(title='Fix API documentation')
        self.assertEqual(item.missing, ['PIC', 'deadline'])
        from tools.task_tools import create_task
        with self.assertRaises(ValueError):
            create_task('Test', 'Andi', 'tomorrow')

    def test_clarification_and_approval(self):
        from coordinator import Coordinator
        from models import ActionItem
        from tools.task_tools import list_tasks
        c = Coordinator()
        c.pending = [ActionItem(title='Fix API docs')]
        self.assertEqual(c.preview()['incomplete'], 1)
        self.assertEqual(c.confirm_and_save()['created'], [])
        c.clarify(0, 'Sinta', '2027-01-11')
        self.assertEqual(len(c.confirm_and_save()['created']), 1)
        self.assertEqual(len(list_tasks()), 1)

if __name__ == '__main__':
    unittest.main()
