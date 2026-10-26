# Local AI Agent from Scratch

A lightweight, locally running AI Agent built from scratch using Python, Ollama, Qwen3, and SQLite, without commercial AI APIs or agent orchestration frameworks.

## Overview

This project demonstrates the fundamental architecture of a tool-using AI Agent, including:

- Local LLM inference using Ollama
- Custom agent execution loop
- Function calling and tool execution
- SQLite-based task management
- Tool allowlisting and basic error handling
- Unit testing

## Architecture

```text
User (CLI)
    |
    v
Agent Controller (Python)
    |
    +----> Local LLM (Ollama / Qwen3)
    |          |
    |          v
    |      Tool Selection
    |          |
    v          v
Tool Registry / Executor
    |
    v
SQLite Database
    |
    v
Tool Result -> Agent Controller
    |
    v
Final Response / Next Action
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Qwen3 1.7B |
| Inference | Ollama |
| Database | SQLite |
| Interface | CLI |
| Agent Framework | None |

## Features

- Create tasks
- List tasks by status
- Update task status
- Select tools using a local LLM
- Execute multiple tool calls
- Basic error handling

## Getting Started

### 1. Prerequisites

Install Python and Ollama.

Download the model:

```bash
ollama pull qwen3:1.7b
```

### 2. Set up Python

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Initialize database

```powershell
.\.venv\Scripts\python.exe database.py
```

### 4. Run the agent

```powershell
.\.venv\Scripts\python.exe agent.py
```

### 5. Run unit tests

```powershell
.\.venv\Scripts\python.exe -m unittest test_tools.py -v
```

## Example Prompts

- Create a task to implement an API for Andi.
- Show all pending tasks.
- Mark task ID 1 as completed.
- Create a task and then list all pending tasks.

## Current Limitations

- Single-user CLI application
- Conversation state is not persisted between sessions
- Limited context management
- Basic validation and error handling
- No systematic LLM reliability evaluation yet

## Roadmap

- [x] Local LLM integration
- [x] Custom agent controller
- [x] Tool calling
- [x] SQLite persistence
- [x] Unit testing
- [ ] Agent evaluation
- [ ] Persistent conversation memory
- [ ] Human-in-the-loop approval
- [ ] Observability and monitoring
- [ ] FastAPI integration
- [ ] Multi-agent experimentation

## Project Goal

To understand AI Agent architecture, orchestration, tool execution, state management, reliability, and AI infrastructure through hands-on implementation using open-source technologies.