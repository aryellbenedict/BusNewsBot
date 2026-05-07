import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
from news_scraper import BusinessNewsScraper

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Global variable to store response channel
RESPONSE_CHANNEL = {}

# ==================== Events ====================

@bot.event
async def on_ready():
    """Bot startup handler"""
    print(f"✓ Bot logged in as {bot.user}")
    print(f"✓ Bot ID: {bot.user.id}")
    if DEBUG:
        print("✓ DEBUG mode enabled")


@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)


# ==================== Commands ====================

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")


@bot.command(name="setchannel")
async def set_channel(ctx, channel: discord.TextChannel):
    """Set the default response channel"""
    RESPONSE_CHANNEL[ctx.guild.id] = channel.id
    await ctx.send(f"✓ Bot will now respond in {channel.mention}")


@bot.command(name="ask")
async def ask(ctx, *, question):
    """Ask the AI a question"""
    # Determine target channel
    target_channel_id = RESPONSE_CHANNEL.get(ctx.guild.id)
    target_channel = bot.get_channel(target_channel_id) if target_channel_id else ctx.channel
    
    async with ctx.typing():
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful Discord bot assistant."},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Split long responses to avoid Discord message length limit
            if len(answer) > 2000:
                chunks = [answer[i:i+2000] for i in range(0, len(answer), 2000)]
                for chunk in chunks:
                    await target_channel.send(chunk)
            else:
                await target_channel.send(answer)
                
        except Exception as e:
            if DEBUG:
                await ctx.send(f"❌ Error: {str(e)}")
            else:
                await ctx.send("❌ An error occurred while processing your request.")
            print(f"Error in ask command: {str(e)}")


@bot.command(name="business-news")
async def business_news(ctx):
    """Fetch and summarize the latest business news"""
    # Show that bot is working
    status_msg = await ctx.send("📰 Fetching latest business news from Yahoo Finance, NYT, CNBC, and Forbes...")
    
    try:
        # Fetch news from all sources
        headlines = await BusinessNewsScraper.fetch_all_news()
        
        if not headlines:
            await status_msg.edit(content="❌ Failed to fetch news from the sources. Please try again later.")
            return
        
        # Format headlines for OpenAI
        headlines_text = BusinessNewsScraper.get_headlines_text(headlines)
        
        # Update status
        await status_msg.edit(content="📰 Generating summary from latest business news...")
        
        # Use OpenAI to create a summary
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial news analyst. Summarize the provided business news headlines into a concise daily business news summary. Showcase the top trending news stories, specifically pointing out stories that are the most popular today. Provide links that users can click to read more. Tell what's happening in the world of business. Highlight key trends and important news items. Keep it professional and informative."
                },
                {
                    "role": "user",
                    "content": f"Please summarize these business news headlines for today:\n\n{headlines_text}"
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        # Balance headlines evenly across all sources for display
        balanced_headlines = BusinessNewsScraper.balance_headlines_by_source(headlines, total_headlines=12)
        
        # Create an embed for the response
        embed = discord.Embed(
            title="📈 Today's Business News Summary",
            description=summary,
            color=discord.Color.green()
        )
        
        # Add individual headlines as clickable links
        embed.add_field(
            name="📰 Latest Headlines",
            value="",
            inline=False
        )
        
        for i, headline in enumerate(balanced_headlines):  # Display balanced headlines
            if headline.url:
                embed.add_field(
                    name=f"{headline.source}",
                    value=f"[{headline.title}]({headline.url})",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{headline.source}",
                    value=headline.title,
                    inline=False
                )
        
        embed.set_footer(text="Sources: Yahoo Finance, New York Times, CNBC, Forbes")
        
        # Send the summary
        await status_msg.edit(content="", embed=embed)
        
    except Exception as e:
        if DEBUG:
            await status_msg.edit(content=f"❌ Error: {str(e)}")
        else:
            await status_msg.edit(content="❌ An error occurred while fetching business news. Please try again later.")
        print(f"Error in business_news command: {str(e)}")


@bot.command(name="commands")
async def help_command(ctx):
    """Display available commands"""
    embed = discord.Embed(
        title="Discord AI Bot Commands",
        description="Available commands for this bot:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name=f"{BOT_PREFIX}ping",
        value="Check bot latency",
        inline=False
    )
    embed.add_field(
        name=f"{BOT_PREFIX}ask <question>",
        value="Ask the AI a question",
        inline=False
    )
    embed.add_field(
        name=f"{BOT_PREFIX}business-news",
        value="Fetch and summarize today's business news from major sources",
        inline=False
    )
    embed.add_field(
        name=f"{BOT_PREFIX}setchannel <#channel>",
        value="Set the default response channel",
        inline=False
    )
    embed.add_field(
        name=f"{BOT_PREFIX}commands",
        value="Show this help message",
        inline=False
    )
    
    await ctx.send(embed=embed)


# ==================== Main ====================

def main():
    """Start the bot"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {str(e)}")
        raise


if __name__ == "__main__":
    main()
