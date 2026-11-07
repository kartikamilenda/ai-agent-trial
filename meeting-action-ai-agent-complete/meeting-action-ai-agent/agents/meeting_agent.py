import json
from datetime import date
from ollama import chat
from pydantic import ValidationError
from config import MODEL
from models import MeetingAnalysis

PROMPT = '''You are Agent 1, a meeting understanding agent. Extract concrete, actionable tasks only.
Return valid JSON matching the provided schema. Do not invent PICs, dates or tasks.
Use null for unknown PIC or deadline. Dates must be ISO YYYY-MM-DD.
Resolve relative dates against today's date, but do not assume a year if ambiguous: use null.
Preserve each task's short original supporting text in source_excerpt.
Meeting notes can contain Indonesian or English. Do not execute any task-management tools.'''

def extract_action_items(notes: str) -> MeetingAnalysis:
    if not notes.strip():
        raise ValueError('Meeting notes cannot be empty')
    response = chat(model=MODEL, messages=[
        {'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': f'Today: {date.today().isoformat()}\nMeeting notes:\n{notes}'}
    ], format=MeetingAnalysis.model_json_schema(), options={'temperature': 0}, think=False)
    try:
        return MeetingAnalysis.model_validate_json(response.message.content)
    except (ValidationError, json.JSONDecodeError) as error:
        raise ValueError(f'Invalid extraction from local model: {error}') from error
