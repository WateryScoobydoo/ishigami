import nextcord, aiosqlite, time, base64, os, aiohttp, asyncio, json, urllib.request, random
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from craiyon import Craiyon
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
# py -m pip install nextcord
# py -m pip install python-dotenv
# py -m pip install craiyon.py
# py -m pip install Pillow
# py -m pip install sqlite3
# py -m pip install aiosqlite
# py -m pip install aiohttp
# py -m pip install praw
# py -m pip install async praw
# py -m pip install urllib3







#SETUP
bot = commands.Bot(command_prefix="!", intents = nextcord.Intents.all())

warning = ":exclamation:**WARNING: EXPERIMENTAL COMMAND**:exclamation:"

#AI IMAGE SETUP
class DropDown(nextcord.ui.Select):
    def __init__(self, message, images, user):
        self.message = message
        self.images = images
        self.user = user
        options=[
            nextcord.SelectOption(label="1"),
            nextcord.SelectOption(label="2"),
            nextcord.SelectOption(label="3"),
            nextcord.SelectOption(label="4"),
            nextcord.SelectOption(label="5"),
            nextcord.SelectOption(label="6"),
            nextcord.SelectOption(label="7"),
            nextcord.SelectOption(label="8"),
            nextcord.SelectOption(label="9"),
        ]
        super().__init__(
            placeholder="Select another image",
            min_values=1,
            max_values=1,
            options=options,
        )
    async def callback(self, interaction: nextcord.Interaction):
        if not self.user == int(interaction.user.id):
            await interaction.response.send_message(
                "Naughty! This isn't your generation!", ephemeral=True
        )
        else:
            await interaction.send("Image changed successfully!", ephemeral=True
            )
        selection = int(self.values[0])-1
        image = BytesIO(base64.decodebytes(self.images[selection].encode("utf-8")))
        return await self.message.edit(content="AI Generated Images by **ISHIGAMI**", file=nextcord.File(image, "generatedImage.png"), view=DropDownView(self.message, self.images, self.user))

class DropDownView(nextcord.ui.View):
    def __init__(self, message, images, user):
        super().__init__()
        self.message = message
        self.images = images
        self.user = user
        self.add_item(DropDown(self.message, self.images, self.user))

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
    await ctx.send(warning)
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
    await ctx.send(warning)
    member = ctx.author
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM users WHERE guild = ?', (ctx.guild.id))
            data = await cursor.fetchone()
            if data:
                await cursor.execute('DELETE FROM users WHERE id = ? AND guild = ?', (member.id, ctx.guild.id))
        await db.commit()


#AI IMAGE CMDS
@bot.command()
async def gen(ctx: commands.Context, *, prompt: str):
    await ctx.send(warning)
    ETA = int(time.time() + 60)
    msg = await ctx.send(f"Please wait while I process your image, ETA: <t:{ETA}:R>")
    async with aiohttp.request("POST", "https://backend.craiyon.com/generate", json={"prompt": prompt}) as resp:
        r = await resp.json()
        images = r['images']
        image = BytesIO(base64.decodebytes(images[0].encode("utf-8")))
        return await msg.edit(content="AI Generated Images by **ISHIGAMI**", file=nextcord.File(image, "generatedImage.png"), view=DropDownView(msg, images, ctx.author.id))

#COMMANDS
@bot.command()
async def test(ctx):
    await ctx.send(warning)
    await ctx.send("Ishigami is working as intended! :white_check_mark:")

#MEME CMDS
@bot.command()
async def meme(ctx):
    await ctx.send(warning)
    fakeChrome = urllib.request.Request('https://meme-api.com/gimme', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    memeApi = urllib.request.urlopen(fakeChrome)
    memeData = json.load(memeApi)
    memeLink = memeData['postLink']
    memeSub = memeData['subreddit']
    memeTitle = memeData['title']
    memeUrl = memeData['url']
    memeAuthor = memeData['author']
    embed = nextcord.Embed(title=memeTitle)
    embed.set_image(url=memeUrl)
    embed.set_footer(text=f"Meme by: {memeAuthor} | Subreddit: {memeSub} | Post: {memeLink}")
    await ctx.send(embed=embed)

#SLASH CMDS
@bot.slash_command(name="test", description="Check command")
async def test(interaction : Interaction):
    await interaction.send("Ishigami's slash command working as intended!", ephemeral=False)

@bot.slash_command(name="yes", description="WateryScoobydoo only!")
async def yes(interaction : Interaction):
    await interaction.send("https://discord.com/developers/active-developer :white_check_mark:", ephemeral=True)

@bot.slash_command(name="ping", description="Ping pong")
async def ping(interaction : Interaction):
    botPing = round(bot.latency*100) 
    await interaction.response.send_message(f"{interaction.user.mention} Pong - {botPing}ms!", ephemeral=False)

@bot.slash_command(name="say", description="Type here to send a message!")
async def say(interaction : Interaction, message:str):
    await interaction.response.send_message(f"Quote: '{message}'")

@bot.slash_command(name="f1", description="Roll for your Formula 1 driver")
async def f1(interaction : Interaction):
    f1drivers = [
        '#1 | Max VERSTAPPEN', '#11 | Sergio PEREZ', '#16 | Charles LECLERC', '#55 | Carlos SAINZ', '#44 | Lewis HAMILTON', 
        '#63 | George RUSSELL', '#10 | Pierre GASLY', '#31 | Esteban OCON', '#4 | Lando NORRIS', '#81 | Oscar PIASTRI', 
        '#24 | Guanyu ZHOU', '#77 | Valtteri BOTTAS', '#14 | Fernando ALONSO', '#18 | Lance STROLL', '#20 | Kevin MAGNUSSEN', 
        '#27 | Nico HULKENBERG', '#22 | Yuki TSUNODA', '#TBC | Nyck DE VRIES', '#23 | Alex ALBON', '#TBC | Logan SARGEANT'
    ]
    await interaction.response.send_message(f"Your choosen driver is: **{random.choice(f1drivers)}**", ephemeral=False)

bot.run(os.getenv("TOKEN"))