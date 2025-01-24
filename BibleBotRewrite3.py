import discord
from discord.ext import commands, tasks
import random
import aiohttp

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)
time_between_ads = 60  # Default time between ads in seconds

# Helper functions
async def fetch_random_verse():
    url = "http://labs.bible.org/api/?passage=random&type=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            verse = data[0]
            return f"{verse['bookname']} {verse['chapter']}:{verse['verse']} - {verse['text']}"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    ad_message.start()

# Commands
@bot.command()
async def help(ctx):
    commands_list = (
        "!askgod [question] - Ask God a question\n"
        "!verse - Get a random Bible verse\n"
        "!confess [sin] - Confess your sins\n"
        "!pray [request] - Send a prayer request\n"
        "!help - Show this help message"
    )
    await ctx.send(f"Here are my commands:\n{commands_list}")

@bot.command()
async def askgod(ctx, *, question: str):
    yes_no_answers = ["Yes", "No", "Perhaps", "Ask again later"]
    detailed_answers = [
        "It may be best for you not to know.",
        "Blasphemy! Ask no more.",
        "Your question is beyond mortal comprehension.",
        "I refuse to answer that.",
        "Think twice about what you ask of me."
    ]
    if any(word in question.lower() for word in ["are", "is", "will"]):
        response = random.choice(yes_no_answers)
    else:
        response = random.choice(detailed_answers)
    await ctx.send(response)

@bot.command()
async def verse(ctx):
    verse_text = await fetch_random_verse()
    await ctx.send(f"Here's a Bible verse for you: {verse_text}")

@bot.command()
async def confess(ctx, *, sin: str):
    forgiveness_responses = [
        "Your sin has been forgiven, rejoice!",
        "God forgives you. Be at peace.",
        "Repent sincerely and your sins will be washed away.",
        "This sin is grave. Say 20 'Hail Marys' as penance.",
        "Your actions mock God's commandments. Seek forgiveness deeply."
    ]
    await ctx.send(random.choice(forgiveness_responses))

@bot.command()
async def pray(ctx, *, request: str):
    prayer_responses = [
        "Amen. Your prayer has been heard.",
        "Your prayer will be answered in due time.",
        "God has received your prayer. Be patient.",
        "Your request is noted. Keep faith strong."
    ]
    await ctx.send(random.choice(prayer_responses))

# Background task for periodic ads
@tasks.loop(seconds=time_between_ads)
async def ad_message():
    channels = [channel for guild in bot.guilds for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
    if channels:
        ad_texts = [
            "Greetings all, I am BibleBot. Use !help to learn about my commands.",
            "Need guidance? Type !verse for a random Bible verse!",
            "Remember to pray daily. Use !pray to send your prayers.",
            "Confess your sins and seek forgiveness. Type !confess [your sin]."
        ]
        for channel in channels:
            try:
                await channel.send(random.choice(ad_texts))
            except discord.Forbidden:
                continue

# Start the bot
bot.run("BOT_TOKEN")