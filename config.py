import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv('TASK_DB_PATH', str(ROOT / 'tasks.db')))
MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:1.7b')
MAX_STEPS = int(os.getenv('MAX_AGENT_STEPS', '6'))
