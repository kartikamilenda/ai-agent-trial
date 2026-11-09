
import sqlite3

from models import ActionItem
from tools.task_tools import create_task


class Coordinator:
    """Coordinate extraction, clarification, approval,
    and persistence of meeting action items."""

    def __init__(self):
        self.pending: list[ActionItem] = []
        self.approved: bool = False

    def analyze(self, notes: str) -> dict:
        from agents.meeting_agent import extract_action_items

        analysis = extract_action_items(notes)

        self.pending = analysis.action_items
        self.approved = False

        return self.preview()

    def preview(self) -> dict:
        return {
            "items": [
                dict(
                    item.model_dump(mode="json"),
                    missing=item.missing
                )
                for item in self.pending
            ],
            "ready": sum(
                not item.missing
                for item in self.pending
            ),
            "incomplete": sum(
                bool(item.missing)
                for item in self.pending
            )
        }

    def clarify(
        self,
        index: int,
        assignee: str | None = None,
        deadline: str | None = None
    ) -> dict:
        if not (0 <= index < len(self.pending)):
            raise ValueError("Invalid item index")

        values = self.pending[index].model_dump()

        if assignee is not None:
            values["assignee"] = assignee

        if deadline is not None:
            values["deadline"] = deadline or None

        self.pending[index] = ActionItem.model_validate(
            values
        )

        # Any correction invalidates prior approval.
        self.approved = False

        return self.preview()

    def approve(self) -> dict:
        """Record explicit user approval."""

        if not self.pending:
            raise ValueError(
                "No action items available for approval"
            )

        ready = [
            item for item in self.pending
            if not item.missing
        ]

        if not ready:
            raise ValueError(
                "No complete tasks available for approval"
            )

        self.approved = True

        return {
            "approved": True,
            "ready": len(ready),
            "incomplete": len(self.pending) - len(ready)
        }

    def confirm_and_save(self) -> dict:
        """Persist only complete, approved action items."""

        if not self.approved:
            raise PermissionError(
                "User approval required before saving"
            )

        created = []
        skipped = []
        errors = []
        saved_ids = set()

        try:
            for item in self.pending:
                if item.missing:
                    skipped.append({
                        "item_id": item.item_id,
                        "title": item.title,
                        "missing": item.missing
                    })
                    continue

                try:
                    result = create_task(
                        title=item.title,
                        assignee=item.assignee,
                        deadline=item.deadline.isoformat(),
                        source_item_id=item.item_id
                    )

                    created.append(result)
                    saved_ids.add(item.item_id)

                except (
                    ValueError,
                    TypeError,
                    sqlite3.Error
                ) as exc:
                    errors.append({
                        "item_id": item.item_id,
                        "title": item.title,
                        "error": str(exc)
                    })

        finally:
            # Approval is one-time only.
            self.approved = False

            # Remove only successfully persisted items.
            self.pending = [
                item
                for item in self.pending
                if item.item_id not in saved_ids
            ]

        return {
            "created": created,
            "needs_clarification": skipped,
            "errors": errors
        }

    def command(self, query: str) -> str:
        from agents.task_agent import run_task_agent

        return run_task_agent(query)
