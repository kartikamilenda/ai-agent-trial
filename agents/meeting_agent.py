
import json
from datetime import date
from uuid import uuid4

from ollama import chat
from pydantic import ValidationError

from config import MODEL
from models import (
    ActionItem,
    MeetingAnalysis,
    MeetingExtraction
)


PROMPT = """
You are Agent 1, a meeting action item extraction agent.

Extract ALL actionable work items from meeting notes,
including tasks with missing information.

Meeting notes may be in Indonesian or English.

DEFINITION OF AN ACTION ITEM:

An action item is work that has been explicitly:
- Assigned to a person;
- Requested by a meeting participant;
- Agreed upon by the team as necessary work.

IMPORTANT:
An action item does NOT require an assigned person
or deadline to be extracted.

EXTRACT TWO CATEGORIES:

1. COMPLETE ACTION ITEMS
   Tasks with an explicitly identified assignee
   and a known deadline.

2. INCOMPLETE ACTION ITEMS
   Tasks that have been requested or agreed upon,
   but are missing an assignee, deadline, or both.

For every action item, return exactly:

- title: concise action description
- assignee: responsible person's name, or null
- deadline: ISO YYYY-MM-DD date, or null
- source_excerpt: original supporting text

RULES:

1. Never omit assignee or deadline fields.
2. Use null if the relevant information is missing.
3. Do not invent names, dates, or tasks.
4. Do not infer a PIC from a person's job title alone.
5. The person requesting a task is not necessarily
   responsible for completing it.
6. Convert explicitly stated dates to YYYY-MM-DD.
7. Resolve unambiguous relative dates using
   the meeting date, if available.
8. Do not extract general discussion, completed work,
   or undecided hypothetical proposals.
9. Preserve the supporting source excerpt.
10. Include all relevant tasks, even when incomplete.

EXAMPLE 1 — COMPLETE TASK:

Input:
"Maya meminta Andi memperbaiki API login
paling lambat 12 November 2026."

Output:
{
  "title": "Memperbaiki API login",
  "assignee": "Andi",
  "deadline": "2026-11-12",
  "source_excerpt": "Maya meminta Andi memperbaiki API login paling lambat 12 November 2026."
}

EXAMPLE 2 — INCOMPLETE TASK:

Input:
"Tim menyepakati dokumentasi API perlu diperbarui,
tetapi PIC dan deadline belum ditentukan."

Output:
{
  "title": "Memperbarui dokumentasi API",
  "assignee": null,
  "deadline": null,
  "source_excerpt": "Tim menyepakati dokumentasi API perlu diperbarui, tetapi PIC dan deadline belum ditentukan."
}

EXAMPLE 3 — NOT AN ACTION ITEM:

Input:
"Tim mempertimbangkan fitur grafik mingguan,
tetapi belum memutuskan apakah akan dikembangkan."

Output:
Do not extract this statement.

FINAL CHECK BEFORE RESPONDING:

Review the entire meeting note again.
Identify all agreed or assigned work.
Ensure tasks with missing PIC or deadline are included.
Ensure undecided proposals are excluded.

Return one JSON object containing an
"action_items" array matching the provided schema.

Return JSON only.
"""


def extract_action_items(notes: str) -> MeetingAnalysis:
    if not notes.strip():
        raise ValueError(
            "Meeting notes cannot be empty"
        )

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Today: {date.today().isoformat()}\n"
                    f"Meeting notes:\n{notes}"
                )
            }
        ],
        format=MeetingExtraction.model_json_schema(),
        options={"temperature": 0},
        think=False
    )

    print(
        "\n========== RAW OLLAMA OUTPUT ==========",
        flush=True
    )
    print(response.message.content, flush=True)

    try:
        extracted = MeetingExtraction.model_validate_json(
            response.message.content
        )

        items = []

        for item in extracted.action_items:
            validated_item = ActionItem.model_validate({
                "item_id": str(uuid4()),
                "title": item.title,
                "assignee": item.assignee,
                "deadline": item.deadline,
                "source_excerpt": item.source_excerpt
            })

            items.append(validated_item)

        analysis = MeetingAnalysis(
            action_items=items
        )

        print(
            "\n========== VALIDATED ACTION ITEMS ==========",
            flush=True
        )

        for item in analysis.action_items:
            print({
                "title": item.title,
                "assignee": item.assignee,
                "deadline": (
                    item.deadline.isoformat()
                    if item.deadline else None
                ),
                "missing": item.missing
            }, flush=True)

        return analysis

    except (
        ValidationError,
        json.JSONDecodeError
    ) as error:
        raise ValueError(
            f"Invalid extraction from local model: {error}"
        ) from error
