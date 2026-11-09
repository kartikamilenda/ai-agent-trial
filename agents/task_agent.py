
import json

from ollama import chat

from config import MODEL, MAX_STEPS

from tools.task_tools import (
    list_tasks,
    update_task_status,
    check_overdue,
    task_summary
)


# =========================================================
# Available Tools
# =========================================================

TOOLS = {
    "list_tasks": list_tasks,
    "update_task_status": update_task_status,
    "check_overdue": check_overdue,
    "task_summary": task_summary
}


# =========================================================
# System Prompt
# =========================================================

SYSTEM = """
You are Agent 2, a local task management agent.

You manage tasks stored in SQLite through Python tools.

AVAILABLE TOOLS:

1. list_tasks(status="all")
   Returns stored tasks.
   Valid statuses:
   all, pending, in_progress, completed.

2. update_task_status(task_id, status)
   Updates an existing task.
   Valid statuses:
   pending, in_progress, completed.

3. check_overdue()
   Returns unfinished tasks past their deadline.

4. task_summary()
   Returns task counts by status and overdue.
   This tool requires NO arguments.

MANDATORY RULES:

- When asked about stored tasks, CALL list_tasks.
- When asked about unfinished tasks, CALL list_tasks.
- When asked for task statistics, CALL task_summary.
- When asked about overdue tasks, CALL check_overdue.
- When explicitly asked to update task status,
  CALL update_task_status using the actual task ID.
- Never claim tasks are missing without checking tools.
- Never invent task IDs, task statuses, or tool results.
- Never invent tool errors.
- Never claim an update succeeded without tool confirmation.
- Never create tasks in this agent.
- If task ID is unclear, ask for clarification.
- Treat tool results as the source of truth.
- Respond in Indonesian.
"""


# =========================================================
# Agent Execution Loop
# =========================================================

def run_task_agent(query: str) -> str:

    if not query.strip():
        return "Masukkan perintah terlebih dahulu."

    # Initialize conversation ONCE
    messages = [
        {
            "role": "system",
            "content": SYSTEM
        },
        {
            "role": "user",
            "content": query
        }
    ]

    for step in range(MAX_STEPS):

        print(
            f"\n[Agent 2] Step {step + 1}/{MAX_STEPS}",
            flush=True
        )

        # Step 1: Call Ollama
        response = chat(
            model=MODEL,
            messages=messages,
            tools=list(TOOLS.values()),
            think=False,
            options={"temperature": 0}
        )

        print(
            "\n========== AGENT 2 RESPONSE ==========",
            flush=True
        )

        print(
            "Content:",
            response.message.content,
            flush=True
        )

        print(
            "Tool calls:",
            response.message.tool_calls,
            flush=True
        )

        print(
            "======================================\n",
            flush=True
        )

        # Step 2: Preserve response in conversation
        messages.append(response.message)

        calls = response.message.tool_calls or []

        # Step 3: No tool call means final response
        if not calls:
            return (
                response.message.content
                or "Tidak ada jawaban dari agent."
            )

        # Step 4: Execute each tool call
        for call in calls:

            name = call.function.name
            args = call.function.arguments

            print(
                f"[Agent 2] Calling tool: {name}",
                flush=True
            )

            print(
                f"[Agent 2] Arguments: {args}",
                flush=True
            )

            try:
                if name not in TOOLS:
                    raise ValueError(
                        f"Tool '{name}' is not allowed"
                    )

                if not isinstance(args, dict):
                    raise ValueError(
                        "Tool arguments must be an object"
                    )

                # Execute actual Python tool
                result = TOOLS[name](**args)

                print(
                    f"[Agent 2] Tool result: {result}",
                    flush=True
                )

                content = json.dumps(
                    {
                        "ok": True,
                        "data": result
                    },
                    ensure_ascii=False,
                    default=str
                )

            except (TypeError, ValueError) as exc:

                print(
                    f"[Agent 2] Tool error: {exc}",
                    flush=True
                )

                content = json.dumps(
                    {
                        "ok": False,
                        "error": str(exc)
                    },
                    ensure_ascii=False
                )

            # Step 5: Return tool result to the model
            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": content
            })

    return (
        "Batas langkah agent tercapai. "
        "Silakan ulangi permintaan."
    )
