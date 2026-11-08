# Meeting Action AI Agent

A local, sequential **two-agent** meeting-to-task prototype based on the supplied use-case design. Agent 1 extracts action items from Indonesian or English meeting notes using Qwen3 1.7B. Pydantic validates structured JSON. A Python coordinator asks for missing PIC/deadline and requires **explicit human approval** before creating SQLite tasks. Agent 2 uses Ollama tool calling to list, update, summarize and check overdue tasks.

## Requirements
- Python 3.10+
- Ollama installed and running locally
- Qwen3 1.7B pulled locally

## Install

```bash
ollama pull qwen3:1.7b
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Ensure Ollama is running (`ollama serve` if it is not already running).

## Run

**Web interface:** `streamlit run app.py`

**Command line:** `python main.py`

**Offline unit tests (no Ollama call):** `python -m unittest discover -s tests -v`

## Example

Input: `Andi menyelesaikan API login tanggal 6 November, Sinta membuat desain dashboard tanggal 9 November, dan dokumentasi API perlu diperbaiki.`

Expected: three candidate tasks, with missing information flagged. The user corrects ambiguous dates and supplies PIC/deadline as needed. After approval, only complete tasks are saved. Ask Agent 2 to show tasks, update statuses, or find overdue work.

## Architecture

```text
Meeting notes -> Coordinator -> Agent 1 (Ollama Qwen3) -> Pydantic validation
                      -> Human review / clarification -> Approved complete items
                      -> Task tools -> SQLite
Task command -> Agent 2 (Ollama Qwen3 tool calling) -> allowlisted tools -> SQLite
```

## Files
- `agents/meeting_agent.py`: structured extraction
- `agents/task_agent.py`: tool-calling agent
- `coordinator.py`: state, clarification, human approval
- `models.py`: Pydantic schemas
- `tools/task_tools.py`: CRUD/status, overdue, summary
- `tools/context_tools.py`: context excerpt helper
- `database.py`: SQLite schema and migration
- `app.py`: Streamlit UI
- `main.py`: CLI
- `tests/`: deterministic unit tests

## Limitations
- Requires a locally running Ollama service and model. The model's actual extraction accuracy depends on the meeting language, ambiguity and model performance.
- Agent 1's small local model may miss tasks or produce invalid JSON. Review its results before approval.
- Date ambiguity is intentionally not resolved by guessing; correct dates in the review UI.
- Pending clarification is kept in the current Streamlit session or CLI process, not persisted across restarts.
- Single-user local prototype; no authentication, external calendar, email or cloud integrations.
- Avoid processing sensitive meeting notes without appropriate local device safeguards.
