# Discord AI Bot

A Discord bot powered by OpenAI that provides intelligent responses to user questions.

## Features

- **AI-Powered Responses**: Uses OpenAI's GPT-3.5 to generate intelligent answers
- **Command-Based Interface**: Easy-to-use Discord commands
- **Error Handling**: Graceful error handling and user feedback
- **Environment Configuration**: Secure configuration using environment variables

## Prerequisites

- Python 3.10 or higher
- Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- OpenAI API key (from [OpenAI Platform](https://platform.openai.com/account/api-keys))

## Installation

1. **Clone or download the project**
   ```bash
   cd DiscordBot
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `OPENAI_API_KEY`: Your OpenAI API key

## Setup Instructions

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section and click "Add Bot"
4. Under TOKEN, click "Copy" to copy your bot token
5. Paste it in your `.env` file as `DISCORD_TOKEN`

### 2. Set Bot Permissions

1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`, `Embed Links`
4. Copy the generated URL and open it to invite the bot to your server

### 3. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Create a new API key
3. Paste it in your `.env` file as `OPENAI_API_KEY`

## Usage

Run the bot:
```bash
python src/main.py
```

### Available Commands

- `!ping` - Check bot latency
- `!ask <question>` - Ask the AI a question
- `!business-news` - Fetch and summarize today's business news from major sources
- `!setchannel <#channel>` - Set the default response channel
- `!commands` - Show all available commands

### Example

```
User: !ask What is the capital of France?
Bot: The capital of France is Paris.
```

## Troubleshooting

- **Bot doesn't appear online**: Check your Discord token and bot permissions
- **API errors**: Verify your OpenAI API key and ensure you have available credits
- **Command not working**: Make sure the bot has permission to send messages in the channel
- **Enable debug mode**: Set `DEBUG=True` in `.env` for verbose logging

## Development

To extend the bot, add new commands in `src/main.py` following the existing pattern:

```python
@bot.command(name="your_command")
async def your_command(ctx, *, args):
    """Command description"""
    # Your code here
    await ctx.send("Response")
```

## License

This project is open source and available under the MIT License.
