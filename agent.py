
from ollama import chat, ResponseError

from database import init_database
from tools import (
    create_task,
    list_tasks,
    update_task_status
)

MODEL = "qwen3:1.7b"
MAX_STEPS = 6

# Tool allowlist: only these functions can execute.
AVAILABLE_TOOLS = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task_status": update_task_status
}

SYSTEM_PROMPT = """
You are a local task management AI agent.

Available capabilities:
- Create a task
- List existing tasks
- Update task status

Rules:
1. Use tools for task-related actions.
2. Never claim an action succeeded without a tool result.
3. Ask for clarification if essential information is missing.
4. Do not invent task IDs or task statuses.
5. Never execute actions outside available tools.
6. Answer in Indonesian.
"""


def run_agent(user_input, messages):
    messages.append({
        "role": "user",
        "content": user_input
    })

    for step in range(MAX_STEPS):
        print(f"\n[Agent step {step + 1}]")

        try:
            response = chat(
                model=MODEL,
                messages=messages,
                tools=list(AVAILABLE_TOOLS.values()),
                think=False,
                options={
                    "temperature": 0,
                    "num_ctx": 4096
                }
            )
        except (ResponseError, ConnectionError) as error:
            print("Inference error:", error)
            return

        messages.append(response.message)

        calls = response.message.tool_calls

        if not calls:
            answer = response.message.content or (
                "Agent tidak menghasilkan jawaban."
            )
            print("\nAgent:", answer)
            return

        for call in calls:
            name = call.function.name
            arguments = call.function.arguments

            print(f"Tool requested: {name}")
            print(f"Arguments: {arguments}")

            if name not in AVAILABLE_TOOLS:
                result = f"ERROR: Tool {name} is not allowed."
            elif not isinstance(arguments, dict):
                result = "ERROR: Invalid tool arguments."
            else:
                try:
                    result = AVAILABLE_TOOLS[name](**arguments)
                except (TypeError, ValueError) as error:
                    result = f"ERROR: Invalid arguments: {error}"
                except Exception:
                    result = "ERROR: Tool execution failed."

            print(f"Tool result: {result}")

            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": str(result)
            })

    print("\nAgent berhenti: batas iterasi tercapai.")


def main():
    init_database()

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
    }]

    print("Local AI Task Agent")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ("exit", "quit"):
            break

        if not user_input:
            continue

        run_agent(user_input, messages)


if __name__ == "__main__":
    main()
