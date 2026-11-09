
import unittest
from unittest.mock import patch

from coordinator import Coordinator
from models import ActionItem


class TestCoordinator(unittest.TestCase):

    def setUp(self):
        self.c = Coordinator()

        self.c.pending = [
            ActionItem(
                title="Implementasi API",
                assignee="Andi",
                deadline="2026-11-12"
            ),
            ActionItem(
                title="Desain Dashboard",
                assignee=None,
                deadline="2026-11-15"
            )
        ]

    def test_save_without_approval_rejected(self):
        with self.assertRaises(PermissionError):
            self.c.confirm_and_save()

    def test_approve_complete_items(self):
        result = self.c.approve()

        self.assertTrue(result["approved"])
        self.assertEqual(result["ready"], 1)
        self.assertEqual(result["incomplete"], 1)

    def test_clarification_invalidates_approval(self):
        self.c.approve()

        self.c.clarify(
            index=1,
            assignee="Sinta"
        )

        self.assertFalse(self.c.approved)
        self.assertEqual(
            self.c.preview()["ready"], 2
        )

    @patch("coordinator.create_task")
    def test_only_complete_tasks_saved(self, mock_create):
        mock_create.return_value = {
            "id": 1,
            "title": "Implementasi API"
        }

        self.c.approve()
        result = self.c.confirm_and_save()

        self.assertEqual(len(result["created"]), 1)
        self.assertEqual(
            len(result["needs_clarification"]), 1
        )
        self.assertEqual(len(self.c.pending), 1)
        self.assertFalse(self.c.approved)

        mock_create.assert_called_once()

        arguments = mock_create.call_args.kwargs

        self.assertEqual(
            arguments["source_item_id"],
            mock_create.call_args.kwargs["source_item_id"]
        )

    @patch("coordinator.create_task")
    def test_failed_task_remains_pending(self, mock_create):
        mock_create.side_effect = ValueError(
            "Simulated database failure"
        )

        self.c.approve()
        result = self.c.confirm_and_save()

        self.assertEqual(len(result["created"]), 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(self.c.pending), 2)
        self.assertFalse(self.c.approved)

    @patch("coordinator.create_task")
    def test_duplicate_titles_tracked_by_id(
        self, mock_create
    ):
        self.c.pending = [
            ActionItem(
                title="Implementasi API",
                assignee="Andi",
                deadline="2026-11-12"
            ),
            ActionItem(
                title="Implementasi API",
                assignee="Sinta",
                deadline="2026-11-13"
            )
        ]

        first_id = self.c.pending[0].item_id
        second_id = self.c.pending[1].item_id

        self.assertNotEqual(first_id, second_id)

        def simulate_create(**kwargs):
            if kwargs["source_item_id"] == second_id:
                raise ValueError("Simulated failure")

            return {
                "id": 1,
                "title": kwargs["title"]
            }

        mock_create.side_effect = simulate_create

        self.c.approve()
        result = self.c.confirm_and_save()

        self.assertEqual(len(result["created"]), 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(self.c.pending), 1)

        # Failed item must still be present.
        self.assertEqual(
            self.c.pending[0].item_id,
            second_id
        )


if __name__ == "__main__":
    unittest.main()
