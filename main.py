from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
import nextcord
import os
from dotenv import load_dotenv
load_dotenv()


#SETUP
bot = commands.Bot(command_prefix="!", intents = nextcord.Intents.all())

@bot.event
async def on_ready():
        print("Ishigami is online!")


#COMMANDS
@bot.command()
async def test(ctx):
    await ctx.send("Ishigami is working as intended!")


@bot.slash_command(name="test", description="Check command")
async def test(interaction : Interaction):
    await interaction.send("Ishigami's slash command working as intended!", ephemeral=False)

@bot.slash_command(name="yes", description="Ping pong")
async def yes(interaction : Interaction):
    await interaction.send("https://discord.com/developers/active-developer", ephemeral=True)

@bot.slash_command(name="say", description="Type here to send a message!")
async def say(interaction : Interaction, message:str):
    await interaction.response.send_message(f"Quote: '{message}'")

bot.run(os.getenv("TOKEN"))