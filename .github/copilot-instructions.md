# Discord AI Bot - Development Instructions

## Project Overview
A Discord bot that integrates with OpenAI to provide AI-powered responses and interactions.

## Technology Stack
- Python 3.10+
- discord.py - Discord bot framework
- openai - OpenAI API client
- python-dotenv - Environment configuration

## Setup Instructions
1. Install Python dependencies: `pip install -r requirements.txt`
2. Create a `.env` file based on `.env.example` with your Discord token and OpenAI API key
3. Run the bot: `python src/main.py`

## Development Workflow
- Keep bot logic in `src/` directory
- Use environment variables for sensitive data
- Follow PEP 8 style guidelines
- Test bot commands in a test Discord server

## Debugging
- Set environment variable `DEBUG=True` for verbose logging
- Check Discord Developer Portal for bot permissions
- Verify API keys are correctly set in `.env`
