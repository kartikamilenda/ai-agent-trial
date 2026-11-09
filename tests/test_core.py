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
        c.pending = [
            ActionItem(title="Fix API docs")
        ]

        # 1. Task initially incomplete
        self.assertEqual(c.preview()["incomplete"], 1)

        # 2. Saving without approval must be rejected
        with self.assertRaises(PermissionError):
            c.confirm_and_save()

        # 3. Complete the missing information
        c.clarify(
            index=0,
            assignee="Sinta",
            deadline="2027-01-11"
        )

        # 4. Task should now be complete
        self.assertEqual(c.preview()["ready"], 1)
        self.assertEqual(c.preview()["incomplete"], 0)

        # 5. Clarification does not grant approval
        with self.assertRaises(PermissionError):
            c.confirm_and_save()

        # 6. User explicitly approves
        approval = c.approve()
        self.assertTrue(approval["approved"])

        # 7. Save the approved task
        result = c.confirm_and_save()

        # 8. Verify execution result
        self.assertEqual(len(result["created"]), 1)
        self.assertEqual(result["errors"], [])

        # 9. Verify actual database persistence
        tasks = list_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Fix API docs")
        self.assertEqual(tasks[0]["assignee"], "Sinta")
        self.assertEqual(tasks[0]["deadline"], "2027-01-11")

        # 10. Saved task should no longer be pending
        self.assertEqual(len(c.pending), 0)

        # 11. Approval is reset after saving
        self.assertFalse(c.approved)

if __name__ == '__main__':
    unittest.main()
