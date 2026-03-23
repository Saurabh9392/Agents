# Slack AI Code Agent

A Slack bot that answers questions about your code projects and KuzuDB-stored documents, powered by MiniMax2.7 AI.

## Prerequisites

- Python 3.10+
- ngrok account (free tier available)
- Slack workspace with permissions to create apps
- MiniMax2.7 API key

## Setup

### 1. Create Slack App

1. Go to https://api.slack.com/apps and click "Create New App"
2. Select "From scratch"
3. Name your app (e.g., "Claude Code Agent") and choose your workspace
4. Under "OAuth & Permissions", add these scopes:
   - `chat:write`
   - `app_mentions:read`
   - `messages:read`
5. Under "Socket Mode", enable Socket Mode
6. Copy the Bot Token (starts with `xoxb-`) and Signing Secret

### 2. Configure Environment

```bash
cd samples/python/slack-code-agent
cp .env.example .env
```

Edit `.env` with your values:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
MINIMAX_API_KEY=your-minimax-api-key
PROJECT_ROOT_PATH=/path/to/your/project
KUZU_DB_PATH=/path/to/kuzu.db  # Optional
NGROK_PORT=3000
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start ngrok

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
ngrok http 3000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 5. Update Slack App

1. In your Slack app settings, go to "Event Subscriptions"
2. Enable Events
3. Set Request URL to: `https://abc123.ngrok.io/slack/events`
4. Under "Subscribe to bot events", add:
   - `message.im` (Direct messages)
   - `app_mention` (Mentions in channels)

5. Go to "Slash Commands"
6. Create `/claude-agent` command
7. Set Request URL to: `https://abc123.ngrok.io/slack/events`

### 6. Run the Agent

```bash
python src/app.py
```

## Usage

### Direct Message
DM the bot directly in Slack

### @mention
In any channel, type `@YourBotName your question`

### Slash Command
```
/claude-agent What does main.py do?
```

## Features

- **Code queries**: Ask about file structure, functions, classes
- **Document queries**: Ask about PDFs, Excel files stored in KuzuDB
- **Graceful degradation**: Works with code only if KuzuDB unavailable

## Troubleshooting

### "Socket Mode" error
Make sure Socket Mode is enabled in your Slack app settings.

### ngrok tunnel not connecting
Restart ngrok: `ngrok http 3000`

### Bot not responding
Check that the Request URL in Slack matches your ngrok URL exactly.
