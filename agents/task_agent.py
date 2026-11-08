import json
from ollama import chat
from config import MODEL, MAX_STEPS
from tools.task_tools import list_tasks, update_task_status, check_overdue, task_summary

# Creation of extracted tasks is controlled by the coordinator and explicit approval.
TOOLS = {'list_tasks': list_tasks, 'update_task_status': update_task_status,
         'check_overdue': check_overdue, 'task_summary': task_summary}
SYSTEM = '''You are Agent 2, a local task management agent. Use tools to answer task queries and update statuses.
Only call tools in the allowlist. Never invent IDs, tasks, or tool results.
Do not create tasks in this chat path; meeting extraction and approval are handled by the coordinator.
If a task ID or requested status is unclear, ask for clarification. Respond in Indonesian.'''

def run_task_agent(query: str) -> str:
    messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': query}]
    for _ in range(MAX_STEPS):
        response = chat(model=MODEL, messages=messages, tools=list(TOOLS.values()), think=False,
                        options={'temperature': 0})
        messages.append(response.message)
        calls = response.message.tool_calls or []
        if not calls:
            return response.message.content or 'Tidak ada jawaban dari agent.'
        for call in calls:
            name, args = call.function.name, call.function.arguments
            try:
                if name not in TOOLS:
                    raise ValueError('Tool not allowed')
                if not isinstance(args, dict):
                    raise ValueError('Tool arguments must be an object')
                result = TOOLS[name](**args)
                content = json.dumps({'ok': True, 'data': result}, ensure_ascii=False, default=str)
            except (TypeError, ValueError) as exc:
                content = json.dumps({'ok': False, 'error': str(exc)})
            messages.append({'role': 'tool', 'tool_name': name, 'content': content})
    return 'Batas langkah agent tercapai. Silakan ulangi permintaan.'
