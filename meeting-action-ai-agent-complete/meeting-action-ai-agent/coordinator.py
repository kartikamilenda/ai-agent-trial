from models import ActionItem
from tools.task_tools import create_task

class Coordinator:
    """Sequential orchestration with human approval and clarification state."""
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
        return {'items': [dict(item.model_dump(mode='json'), missing=item.missing) for item in self.pending],
                'ready': sum(not item.missing for item in self.pending),
                'incomplete': sum(bool(item.missing) for item in self.pending)}

    def clarify(self, index: int, assignee: str | None = None, deadline: str | None = None) -> dict:
        if not (0 <= index < len(self.pending)):
            raise ValueError('Invalid item index')
        values = self.pending[index].model_dump()
        if assignee is not None:
            values['assignee'] = assignee
        if deadline is not None:
            values['deadline'] = deadline or None
        self.pending[index] = ActionItem.model_validate(values)
        self.approved = False
        return self.preview()

    def confirm_and_save(self) -> dict:
        """Save only complete items after explicit UI/CLI confirmation."""
        created, skipped, errors = [], [], []
        for item in self.pending:
            if item.missing:
                skipped.append({'title': item.title, 'missing': item.missing})
                continue
            try:
                created.append(create_task(item.title, item.assignee, item.deadline.isoformat()))
            except (ValueError, TypeError) as exc:
                errors.append({'title': item.title, 'error': str(exc)})
        # Remove saved items, keeping unresolved items for subsequent clarification.
        saved_titles = {task['title'] for task in created}
        self.pending = [item for item in self.pending if item.title not in saved_titles]
        return {'created': created, 'needs_clarification': skipped, 'errors': errors}

    def command(self, query: str) -> str:
        from agents.task_agent import run_task_agent
        return run_task_agent(query)
