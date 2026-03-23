# Slack AI Code Agent Design Specification

**Date:** 2026-03-23
**Author:** Claude + Saurabh
**Status:** Approved

---

## Overview

A Slack bot that answers questions about your code projects and KuzuDB-stored documents, powered by MiniMax2.7 AI and deployed locally with ngrok tunneling.

---

## Goals

- Enable natural language queries about project code via Slack
- Query KuzuDB for document data (PDFs, Excel, etc.)
- Graceful degradation when KuzuDB is unavailable
- Works for any user in the Slack workspace
- Runs locally on your Mac with ngrok tunnel

---

## Non-Goals

- Multi-project support (single configured project for v1)
- Authentication beyond Slack workspace membership
- Streaming responses
- Persistent session memory

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Slack Workspace                          │
│   (DMs, @mentions, / commands from any workspace user)      │
└────────────────────────────┬─────────────────────────────────┘
                             │ Events via HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      ngrok Tunnel                             │
│              (exposes local port 3000 to public HTTPS)       │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                   Slack Bolt App (Python)                     │
│                                                              │
│  ┌────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │ Event      │──│ Agent Logic   │──│ MiniMax2.7 API    │  │
│  │ Handlers   │  │               │  │                   │  │
│  └────────────┘  └───────────────┘  └───────────────────┘  │
│       │                  │                                   │
│       │           ┌──────┴──────┐                            │
│       │           ▼             ▼                             │
│       │    ┌───────────┐ ┌────────────┐                     │
│       │    │ Project   │ │ KuzuDB     │                     │
│       │    │ Analyzer  │ │ Query      │                     │
│       │    └───────────┘ └────────────┘                     │
└───────┼──────────────────────────────────────────────────────┘
```

---

## Project Structure

```
samples/python/slack-code-agent/
├── src/
│   ├── __init__.py
│   ├── app.py                # Bolt app entry point
│   ├── agent.py              # Main agent logic
│   ├── project_analyzer.py   # Code file scanning (from Teams project)
│   ├── kuzu_client.py        # KuzuDB queries
│   ├── llm_handler.py        # MiniMax2.7 API calls
│   └── config.py             # Environment configuration
├── .env.example              # Template with required vars
├── requirements.txt          # Dependencies
├── ngrok.yml                 # Ngrok configuration
└── README.md
```

---

## Components

### 1. Bolt App (`app.py`)

**Responsibilities:**
- Handle DMs, @mentions, slash commands
- Route messages to agent logic
- Respond to Slack in real-time
- Verify request signatures

**Event handlers:**
- `message()` - Direct messages and mentions
- `slash_command()` - `/claude-agent` command
- `app_mention()` - When bot is @mentioned in channel

### 2. Agent Logic (`agent.py`)

**Responsibilities:**
- Parse user question
- Determine query type: code vs document vs mixed
- Build context from ProjectAnalyzer + KuzuDB
- Construct prompt for MiniMax2.7
- Format and send response to Slack

**Intent detection:**
- Keywords like "document", "pdf", "excel", "spreadsheet" → KuzuDB query
- Keywords like "file", "function", "class", "code" → ProjectAnalyzer
- Default: check both sources

### 3. Project Analyzer (`project_analyzer.py`)

Reused from existing Teams project:
- Scan configured project path recursively
- Extract: file paths, class names, function names, docstrings, imports
- Build searchable index of code symbols
- Smart context selection based on query keywords

**Exclude patterns:**
```
.git, .venv, venv, __pycache__, node_modules, .env, *.pyc, .idea
```

**Features:**
- File size limit: 100KB per file
- Caching: Cache index for 5 minutes
- Context window: Max 8000 tokens

### 4. KuzuDB Client (`kuzu_client.py`)

**Responsibilities:**
- Connect to local KuzuDB instance
- Query graph database for document data
- Support vector/keyword search for semantic queries

**API:**
```python
class KuzuClient:
    def __init__(self, db_path: str)
    def query_documents(self, query: str, limit: int = 10) -> List[Document]
    def search_by_keyword(self, keyword: str) -> List[Document]
    def is_available(self) -> bool
```

### 5. LLM Handler (`llm_handler.py`)

**Uses MiniMax2.7 API:**
```python
import requests

response = requests.post(
    "https://api.minimax.chat/v1/text/chatcompletion_pro",
    headers={"Authorization": f"Bearer {MINIMAX_API_KEY}"},
    json={"model": "MiniMax-Text-01", "messages": [...]}
)
```

**Features:**
- Token tracking per request
- Rate limiting: 10 requests/minute
- Retry logic: 3 retries with exponential backoff
- System prompt with project context

---

## Data Flow

```
User asks question in Slack
         │
         ▼
Bolt receives event (DM/mention/slash)
         │
         ▼
Agent parses question
         │
         ├──────────────────┐
         ▼                  ▼
  Code query?        Document query?
         │                  │
         ▼                  ▼
  ProjectAnalyzer    KuzuDB client
  scans files        queries graph
         │                  │
         └────────┬─────────┘
                  ▼
         Combined context
                  │
                  ▼
         MiniMax2.7 API
         (system prompt + context)
                  │
                  ▼
         AI response
                  │
                  ▼
Bolt sends message to Slack channel
```

---

## Error Handling

```
User question
      │
      ▼
┌─────────────┐
│ Parse error? │──Yes──► "I didn't understand. Type /help for commands"
└─────────────┘
      │No
      ▼
┌─────────────┐
│ Project     │──No───► "Project path not configured"
│ configured? │
└─────────────┘
      │Yes
      ▼
┌─────────────┐
│ KuzuDB     │──No────► Proceed with code-only context
│ available? │         (graceful degradation)
└─────────────┘
      │
      ▼
┌─────────────┐
│ LLM API    │──Fail──► "AI service temporarily unavailable"
│ success?   │          + suggest retry
└─────────────┘
      │Yes
      ▼
Response sent to Slack
```

**Graceful Degradation:**
- KuzuDB missing → Answer based on code files only
- Document query asked → "Document search unavailable, answering from code"
- No error shown to user, just reduced capability

---

## Configuration

```
SLACK_BOT_TOKEN=xoxb-...       # Bot OAuth token
SLACK_SIGNING_SECRET=...       # Signing secret from Slack app
MINIMAX_API_KEY=...            # MiniMax2.7 API key
MINIMAX_BASE_URL=https://api.minimax.chat
KUZU_DB_PATH=/path/to/kuzu.db # Local KuzuDB file (optional)
PROJECT_ROOT_PATH=/Users/saurabh/PycharmProjects/某项目
NGROK_PORT=3000
```

---

## System Prompt

```
You are a helpful code and document assistant that answers questions about the configured project.
You have access to the project's file structure, code files, and optionally document data stored in KuzuDB.

When answering:
1. Be concise and accurate
2. Reference specific files or documents when relevant
3. Include code snippets if helpful
4. If you don't know, say so

Project context:
{project_context}

Document context (from KuzuDB):
{document_context}
```

---

## User Interactions

### Direct Message
- User DMs the bot directly
- Bot responds with answer

### @mention
- User @mentions bot in a channel
- Bot responds in that channel

### Slash Command
- User types `/claude-agent <question>`
- Bot responds with answer

### Example Queries
- "What files are in this project?"
- "Explain the main.py file"
- "Find functions related to authentication"
- "What does the Q3 report say about revenue?"
- "Summarize the meeting notes from last week"

---

## Testing Strategy

- **Unit tests** for ProjectAnalyzer (file scanning, context selection)
- **Unit tests** for KuzuDB client (mock DB responses)
- **Unit tests** for LLM handler (mock API responses)
- **Integration tests** with Slack API (using pytest-mock)
- **Manual testing** via ngrok local tunnel

---

## Success Criteria

- [ ] Bot responds to DMs, @mentions, and `/claude-agent` slash command
- [ ] Answers questions about project code structure
- [ ] Queries KuzuDB for document data when available
- [ ] Falls back to code-only when KuzuDB unavailable
- [ ] Works for any workspace user
- [ ] Runs locally via ngrok tunnel
- [ ] Powered by MiniMax2.7 AI

---

## Free Tier Stack

| Service | Cost | Notes |
|---------|------|-------|
| Slack Bot (Bolt) | FREE | No cost for bot usage |
| ngrok Free | FREE | Session-based tunnel, restarts needed |
| MiniMax2.7 | TBD | Check pricing at minimax.chat |
| KuzuDB | FREE | Local graph DB, open source |
