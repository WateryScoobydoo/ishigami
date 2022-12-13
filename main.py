from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
import nextcord, aiosqlite
import os
from dotenv import load_dotenv
load_dotenv()
# py -m pip install module





#SETUP
bot = commands.Bot(command_prefix="!", intents = nextcord.Intents.all())

@bot.event
async def on_ready():
        print("Ishigami is online!")
        async with aiosqlite.connect("main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER , guild INTEGER)')
            await db.commit()

#DB CMDS
@bot.command()
async def adduser(ctx, member:nextcord.Member):
    member = ctx.author
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM users WHERE guild = ?', (ctx.guild.id))
            data = await cursor.fetchone()
            if data:
                await cursor.execute('UPDATE users SET id = ? WHERE guild = ?', (member.id, ctx.guild.id))
            else:
                await cursor.execute('INSERT INTO users (id, guild) VALUES (?, ?)', (member.id, ctx.guild.id))
        await db.commit()

@bot.command()
async def removeuser(ctx, member:nextcord.Member):
    member = ctx.author
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM users WHERE guild = ?', (ctx.guild.id))
            data = await cursor.fetchone()
            if data:
                await cursor.execute('DELETE FROM users WHERE id = ? AND guild = ?', (member.id, ctx.guild.id))
        await db.commit()


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