import os
import discord
import asyncio
import random
import openai
from discord.ext import commands
from dotenv import load_dotenv

#################################################################################
#                                                                               #
#                           HU TAO BOT FROM SEOO                                #
#                                                                               #
#################################################################################

# Initialisation du bot

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

os.chdir(os.path.dirname(os.path.abspath(__file__)))
bot = commands.Bot(command_prefix="!", intents=intents)

#################################################################################
#                           COMMANDES - TEST                                    #
#################################################################################

# Commande pour le ping
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 Latence : `{latency} ms`")

# Commande pour un bonne nuit
@bot.command()
async def goodnight(ctx):
    await ctx.send(f"Oh, you sleepy {ctx.author}?")
    await asyncio.sleep(2)
    await ctx.send("Get some rest...")
    await asyncio.sleep(1)
    await ctx.send("I'm gonna take a walk by myself.")

# Commande pour un pile ou face
@bot.command()
async def piece(ctx):
    await ctx.send(random.choice(["Pile", "Face"]))

# Commande pour lancer un dé à 6 face
@bot.command()
async def roll(ctx):
    await ctx.send(random.randint(1, 6))

# Evenement pour savoir si le bot est lancé
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")

# Evenement si pas de permissions pour utiliser une cmd
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("⛔ Vous n’avez pas la permission d’utiliser cette commande.")
    else:
        raise error

# Un about sur le bot
@bot.command()
async def about(ctx):
    embed = discord.Embed(
        title="À propos du bot",
        description="Ce bot a été invoqué pour veiller sur vous même après votre mort ! 🥀",
        color=discord.Color.from_str("#FF0000")
    )
    embed.set_thumbnail(url="https://i.pinimg.com/originals/d9/ab/80/d9ab80f638411facf70ab1ad542ff380.gif")
    embed.set_footer(text="Hu Tao • By Seoo")
    await ctx.send(embed=embed)

# Chatbox (OpenAI)
@bot.command()
async def chat(ctx, *, message):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("❌ Cette commande ne peut pas être utilisée en message privé.")
        return

    try:
        async with ctx.typing():
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "Tu es un bot assistant dans un serveur Discord."},
                    {"role": "user", "content": message}
                ]
            )
            content = response.choices[0].message.content
            await ctx.send(content)

    except Exception as exception:
        await ctx.send("❌ Erreur lors de la génération de la réponse.")
        print(exception)

#################################################################################
#                           LANCEMENT DU BOT                                    #
#################################################################################

load_dotenv()

# TOKEN DISCORD
token = os.getenv("TOKEN_BOT_DISCORD")

# KEY ChatGPT
openai.api_key = os.getenv("OPENAI_API_KEY")

async def main():
    async with bot:
        await bot.load_extension("cogs.Hu_Tao_MODERATIONCMD")  # Chargement du Cog MODERATIONCMD
        await bot.load_extension("cogs.Hu_Tao_EMBEDS")  # Chargement du Cog EMBEDS
        await bot.load_extension("cogs.Hu_Tao_PROFILE")  # Chargement du Cog PROFILE
        await bot.load_extension("cogs.Hu_Tao_OCCREATION")  # Chargement du Cog OCCREATION
        await bot.load_extension("cogs.Hu_Tao_STATS") # Chargement du Cog STATS
        await bot.start(token)

asyncio.run(main())
