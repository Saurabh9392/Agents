# Teams Project Agent

A Microsoft Teams bot that answers questions about the MS365_Agents codebase using GLM-4 AI (ZhipuAI).

## Features

- Code Search: Ask questions about the project codebase
- AI-Powered: Uses GLM-4-Flash for intelligent responses
- Teams Integration: Works directly in Microsoft Teams personal chat
- Free Tier: Designed to work with free tier services

## Prerequisites

1. **Azure Bot Service** (F0 Free tier)
   - Multi-tenant bot
   - Personal Microsoft account supported

2. **ZhipuAI Account**
   - Get API key from https://open.bigmodel.cn/

3. **Python 3.11+**

## Setup

### 1. Install Dependencies

```bash
cd samples/python/teams-project-agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
MicrosoftAppId=YOUR_AZURE_BOT_APP_ID
MicrosoftAppPassword=YOUR_AZURE_BOT_CLIENT_SECRET
MicrosoftAppType=MultiTenant
ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY
PROJECT_ROOT_PATH=/path/to/MS365_Agents
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Start the Server

```bash
python src/start_server.py
```

The server runs on http://localhost:3978 by default.

## Azure Setup

### 1. Create Azure Bot

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Azure Bot" and create one
3. Select **Multi-tenant** for personal accounts
4. Note the **Microsoft App ID**

### 2. Create App Registration

1. Go to **Microsoft Entra ID** -> **App registrations**
2. Create new registration
3. Select "Accounts in any organizational directory and personal Microsoft accounts"
4. Create a client secret and note it

### 3. Configure Bot Endpoint

For local development, use dev tunnels:

```bash
# Install dev tunnels (if not installed)
# npm install -g @anthropic-ai/devtunnel

devtunnel host -p 3978 --allow-anonymous
```

Update your Azure Bot's messaging endpoint to: `https://YOUR-TUNNEL-ID.devtunnels.ms/api/messages`

## Teams Installation

### 1. Create App Package

1. Replace `${MICROSOFT_APP_ID}` in `appManifest/manifest.json` with your Azure Bot App ID
2. Zip the contents of `appManifest/` folder (manifest.json, outline.png, color.png)

### 2. Sideload in Teams

1. Open Microsoft Teams
2. Go to **Apps** -> **Manage your apps**
3. Click **Upload an app** -> **Upload a custom app**
4. Select the zip file
5. Add the bot to a personal chat

## Usage

Once installed, you can ask the bot questions like:

- "What files are in this project?"
- "Explain the quickstart agent"
- "How does authentication work?"
- "What plugins are available?"

## Project Structure

```
teams-project-agent/
├── src/
│   ├── agent.py            # Main bot logic
│   ├── app.py              # aiohttp server
│   ├── config.py           # Configuration
│   ├── glm4_handler.py     # GLM-4 API integration
│   ├── project_analyzer.py # Code analysis
│   └── start_server.py     # Entry point
├── tests/                   # Unit and integration tests
├── appManifest/            # Teams app package files
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Cost

| Service | Tier | Cost |
|---------|------|------|
| Azure Bot Service | F0 | FREE (10K msg/mo) |
| ZhipuAI GLM-4-Flash | Free tier | FREE (with limits) |
| Dev Tunnels | Free | FREE |

## Troubleshooting

### Bot not responding
- Check dev tunnel is running
- Verify Azure Bot endpoint is configured
- Check logs for errors

### API errors
- Verify ZHIPUAI_API_KEY is correct
- Check rate limits haven't been exceeded

### Authentication errors
- Verify MicrosoftAppId and MicrosoftAppPassword are correct
- Ensure bot is Multi-tenant for personal accounts

## License

MIT License - See LICENSE file in repository root.
