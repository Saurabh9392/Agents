# Building a Personal Microsoft Teams Agent

## What is This Project?

The **Microsoft 365 Agents SDK** is Microsoft's open-source framework for building AI-powered conversational agents (bots) that can be deployed across multiple platforms:

- **Microsoft Teams**
- **Microsoft 365 Copilot**
- **Web Chat**
- **Custom Applications**
- **Copilot Studio**

**Key Point:** You do NOT need a Microsoft 365 Copilot subscription to use this SDK. A regular (free) Microsoft account is sufficient for building Teams agents.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Agent Code                          │
│  (Semantic Kernel / LangChain / Custom Logic)              │
├─────────────────────────────────────────────────────────────┤
│                   Agents SDK                                │
│  (AgentApplication, TurnContext, State Management)         │
├─────────────────────────────────────────────────────────────┤
│                   Azure Bot Service                         │
│  (Handles authentication & channel communication)          │
├─────────────────────────────────────────────────────────────┤
│     Channels: Teams | WebChat | Outlook | Custom           │
└─────────────────────────────────────────────────────────────┘
```

---

## Free Tier Options for Personal Use

Since you use Teams with a Gmail account (personal Microsoft account), here are the **free** or **low-cost** options:

### 1. Azure Bot Service - Free Tier (F0)
- **Cost:** FREE
- **Messages:** 10,000 messages/month
- **Perfect for:** Personal projects, learning, testing

### 2. OpenAI API (Instead of Azure OpenAI)
- **Cost:** Pay-as-you-go (~$0.15/1M tokens for GPT-4o-mini)
- **Why:** Azure OpenAI requires enterprise approval; OpenAI API is instant access
- **Free credits:** New accounts often get free credits

### 3. Local Development Tools (100% Free)
- **Agents Playground:** Test your bot locally without Azure
- **Dev Tunnels:** Connect Teams to your local development machine
- **ngrok:** Alternative to dev tunnels

### 4. Azure Free Account
- **$200 credit** for first 30 days
- **12 months** of free services
- Includes App Service, Storage, and more

---

## Prerequisites

### Required
| Item | How to Get It | Cost |
|------|---------------|------|
| Microsoft Account | [signup.live.com](https://signup.live.com) | Free |
| Azure Subscription | [azure.microsoft.com/free](https://azure.microsoft.com/free) | Free tier available |
| OpenAI API Key | [platform.openai.com](https://platform.openai.com) | ~$5 minimum |

### For Development
| Language | Requirements | Difficulty |
|----------|--------------|------------|
| **Python** | Python 3.9+ | Easiest |
| **Node.js** | Node.js 20+, TypeScript | Moderate |
| **.NET** | .NET 8.0, VS/VS Code | Moderate |

**Recommendation:** Start with **Python** if you're new to this.

---

## Step-by-Step Guide: Build Your First Teams Agent

### Step 1: Set Up Azure Resources (Free Tier)

#### 1.1 Create Azure Bot Service (Free)

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Azure Bot"**
3. Click **Create**
4. Select:
   - **Bot handle:** `your-bot-name` (must be globally unique)
   - **Pricing tier:** **Standard** or **F0 (Free)** if available
   - **Type of App:** Multi-Tenant (important for personal accounts!)
5. Click **Review + Create**

#### 1.2 Create Microsoft Entra ID App Registration

1. Go to **Microsoft Entra ID** (formerly Azure AD)
2. Click **App registrations** → **New registration**
3. Name it `your-bot-name-auth`
4. Select **Accounts in any organizational directory and personal Microsoft accounts**
5. Click **Register**
6. Note down:
   - **Application (client) ID**
   - **Directory (tenant) ID**
7. Go to **Certificates & secrets** → **New client secret**
8. Create a secret and note it down

#### 1.3 Configure Bot Authentication

1. Go back to your Azure Bot
2. Click **Configuration**
3. Add your Microsoft App ID
4. Save the Client Secret in your code's configuration

---

### Step 2: Clone and Set Up the Project

```bash
# Clone the repository
git clone https://github.com/microsoft/MS365-Agents.git
cd MS365-Agents

# Choose your language path
cd samples/python/quickstart  # Recommended for beginners
# OR
cd samples/dotnet/quickstart
# OR
cd samples/nodejs/quickstart
```

---

### Step 3: Configure Your Agent (Python Example)

#### 3.1 Install Dependencies

```bash
cd samples/python/quickstart
pip install -r requirements.txt
```

#### 3.2 Create Configuration File

Create `appsettings.json`:

```json
{
  "MicrosoftAppType": "MultiTenant",
  "MicrosoftAppId": "YOUR_CLIENT_ID_FROM_STEP_1.2",
  "MicrosoftAppPassword": "YOUR_CLIENT_SECRET_FROM_STEP_1.2",
  "MicrosoftAppTenantId": ""
}
```

#### 3.3 Set Environment Variables (Alternative)

```bash
# Linux/Mac
export MicrosoftAppId="YOUR_CLIENT_ID"
export MicrosoftAppPassword="YOUR_CLIENT_SECRET"

# Windows PowerShell
$env:MicrosoftAppId="YOUR_CLIENT_ID"
$env:MicrosoftAppPassword="YOUR_CLIENT_SECRET"
```

---

### Step 4: Run and Test Locally

#### 4.1 Install Dev Tunnels (for Teams testing)

```bash
# Using npm
npm install -g @anthropic-ai/devtunnel

# OR using dotnet
dotnet tool install -g Microsoft.VisualStudio.DevTunnels
```

#### 4.2 Start Your Bot

```bash
# Start your Python bot
python app.py
# Bot runs on http://localhost:3978
```

#### 4.3 Create a Dev Tunnel

```bash
# Create and host a tunnel
devtunnel host -p 3978 --allow-anonymous
```

Note the tunnel URL (e.g., `https://your-tunnel-id.devtunnels.ms`)

#### 4.4 Configure Bot Endpoint

1. Go to Azure Portal → Your Bot → **Configuration**
2. Set **Messaging endpoint:** `https://your-tunnel-id.devtunnels.ms/api/messages`
3. Save

---

### Step 5: Add to Microsoft Teams

#### 5.1 Enable Teams Channel

1. In Azure Portal → Your Bot → **Channels**
2. Click **Microsoft Teams**
3. Accept terms and save

#### 5.2 Get Your App Manifest

The project includes manifest templates at `samples/python/quickstart/appManifest/`

Edit `manifest.json`:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "YOUR_MICROSOFT_APP_ID",
  "packageName": "com.yourname.personalbot",
  "developer": {
    "name": "Your Name",
    "websiteUrl": "https://example.com",
    "privacyUrl": "https://example.com/privacy",
    "termsOfUseUrl": "https://example.com/terms"
  },
  "name": {
    "short": "My Personal Bot",
    "full": "My Personal Teams Assistant"
  },
  "description": {
    "short": "A personal assistant bot",
    "full": "My personal AI assistant for Microsoft Teams"
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#FFFFFF",
  "bots": [
    {
      "botId": "YOUR_MICROSOFT_APP_ID",
      "scopes": ["personal", "team", "groupChat"],
      "isNotificationOnly": false
    }
  ],
  "permissions": ["identity", "messageTeamMembers"]
}
```

#### 5.3 Create App Package

1. Create a zip file containing:
   - `manifest.json`
   - `outline.png` (20x20 icon)
   - `color.png` (96x96 icon)
2. Name it `yourbot.zip`

#### 5.4 Sideload in Teams

1. Open Microsoft Teams
2. Go to **Apps** → **Manage your apps**
3. Click **Upload an app** → **Upload a custom app**
4. Select your `yourbot.zip`
5. Add the bot to a chat or team

---

## Adding AI Capabilities (Semantic Kernel)

For an AI-powered bot, use the Semantic Kernel sample:

```bash
cd samples/python/semantic-kernel-multiturn
```

### Configure OpenAI

Create `appsettings.json`:
```json
{
  "MicrosoftAppType": "MultiTenant",
  "MicrosoftAppId": "YOUR_CLIENT_ID",
  "MicrosoftAppPassword": "YOUR_CLIENT_SECRET",
  "OpenAI": {
    "ApiKey": "YOUR_OPENAI_API_KEY",
    "ModelId": "gpt-4o-mini"
  }
}
```

### Install Semantic Kernel

```bash
pip install semantic-kernel openai
```

### Basic AI Agent Code

```python
from microsoft.agents import AgentApplication, TurnContext, TurnState
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os

class AIAgent(AgentApplication):
    def __init__(self, options):
        super().__init__(options)

        # Initialize Semantic Kernel
        self.kernel = Kernel()
        self.kernel.add_service(
            OpenAIChatCompletion(
                service_id="chat",
                ai_model_id="gpt-4o-mini",
                api_key=os.environ.get("OpenAI__ApiKey")
            )
        )

        # Register message handler
        self.on_activity("message", self.on_message)

    async def on_message(self, context: TurnContext, state: TurnState):
        # Get user message
        user_message = context.activity.text

        # Call OpenAI via Semantic Kernel
        response = await self.kernel.invoke_prompt(user_message)

        # Send response to Teams
        await context.send_activity(str(response))
```

---

## Project Structure Reference

```
MS365-Agents/
├── samples/
│   ├── python/                    # Python samples
│   │   ├── quickstart/           # Basic echo bot ← Start here!
│   │   ├── semantic-kernel-multiturn/  # AI-powered bot
│   │   ├── auto-signin/          # Authentication with Graph
│   │   └── cards/                # Rich card examples
│   ├── dotnet/                    # C# samples
│   │   ├── quickstart/
│   │   ├── semantic-kernel-multiturn/
│   │   └── azure-ai-streaming/
│   └── nodejs/                    # JavaScript samples
│       ├── quickstart/
│       ├── langchain-multiturn/
│       └── azure-ai-streaming/
├── specs/                         # Protocol documentation
│   ├── activity/                  # Message format specs
│   └── manifest/                  # App manifest specs
└── experimental/                  # Work-in-progress features
```

---

## Sample Use Cases for Personal Agents

| Use Case | Description | Difficulty |
|----------|-------------|------------|
| **Echo Bot** | Repeats messages back | Easy |
| **Weather Agent** | Fetches weather data with AI | Moderate |
| **Personal Assistant** | Reminders, notes, tasks | Moderate |
| **Calendar Bot** | Integrates with your calendar | Moderate |
| **Knowledge Base** | Search your documents | Advanced |
| **Multi-Agent** | Multiple specialized agents | Advanced |

---

## Cost Estimate (Personal Use)

| Service | Monthly Cost (Light Use) |
|---------|-------------------------|
| Azure Bot Service (F0) | **FREE** |
| OpenAI API (GPT-4o-mini) | ~$1-5/month |
| Azure Hosting (Optional) | Free tier available |
| **Total** | **~$1-5/month** |

---

## Troubleshooting

### Bot Not Responding in Teams
1. Check dev tunnel is running: `devtunnel host -p 3978 --allow-anonymous`
2. Verify endpoint in Azure Bot configuration
3. Check logs for errors

### Authentication Errors
1. Ensure App Registration allows "Personal Microsoft accounts"
2. Verify Client ID and Secret are correct
3. Check MultiTenant is set in configuration

### OpenAI API Errors
1. Verify API key is valid
2. Check you have credits in your OpenAI account
3. Ensure model name is correct (`gpt-4o-mini`)

---

## Resources

- **Official Docs:** [aka.ms/M365-Agents-SDK-Docs](https://aka.ms/M365-Agents-SDK-Docs)
- **Python API:** [learn.microsoft.com/python/api/agent-sdk-python](https://learn.microsoft.com/en-us/python/api/agent-sdk-python/agents-overview)
- **GitHub Issues:** [github.com/microsoft/MS365-Agents/issues](https://github.com/microsoft/MS365-Agents/issues)
- **Dev Tunnels:** [learn.microsoft.com/azure/developer/dev-tunnels](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/)

---

## Next Steps

1. **Start Simple:** Run the `quickstart` sample first
2. **Add AI:** Upgrade to `semantic-kernel-multiturn` sample
3. **Customize:** Add your own plugins and features
4. **Deploy:** Move from dev tunnels to Azure App Service (free tier)

Happy building!

---

## Ready-to-Use Sample

A complete implementation is available at:

```
samples/python/teams-project-agent/
```

This sample includes:
- Project analyzer for code context
- GLM-4 integration (free tier)
- Teams bot with personal chat support
- Full test suite
- Deployment-ready configuration

To use it:
```bash
cd samples/python/teams-project-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python src/start_server.py
```

See the [README](samples/python/teams-project-agent/README.md) for detailed setup instructions.
