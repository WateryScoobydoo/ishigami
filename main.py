import nextcord, aiosqlite, time, base64, os, aiohttp, asyncio, json, urllib.request, random, requests
from nextcord import Interaction, SlashOption, ChannelType, Embed, File, ButtonStyle
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from nextcord.ui import Button, View
from PIL import Image
from io import BytesIO
from config import API
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
# py -m pip install aiohttp
# py -m pip install requests







#SETUP
bot = commands.Bot(command_prefix="!", intents = nextcord.Intents.all())

warning = ":exclamation:**WARNING: EXPERIMENTAL COMMAND**:exclamation:"

max_retries = 5

#quotes = {}

#HELP COMMAND SETUP
helpGuide = json.load(open("help.json"))

bot.remove_command("ihelp")

def createHelpEmbed(pageNum=0, inline=False):
    pageNum = pageNum % len(list(helpGuide))
    pageTitle = list(helpGuide)[pageNum]
    embed = Embed(colour=0x0080ff, title=pageTitle)
    for key, val in helpGuide[pageTitle].items():
        embed.add_field(name=key, value=val, inline=inline)
        embed.set_footer(text=f"Page {pageNum+1} of {len(list(helpGuide))}")
    return embed

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

@bot.command()
@commands.is_owner()
async def die(ctx):
    await ctx.send(warning)
    userDisplayName = ctx.author.display_name
    shutdownDesc = (f"**{userDisplayName}#0000** Ishigami will now shutdown... ;-;")
    embed = nextcord.Embed(description=(shutdownDesc), colour=0xFF0000)
    await ctx.send(embed=embed)
    await bot.close()

@bot.command()
async def ihelp(ctx):
    await ctx.send(warning)
    currentPage = 0

    async def next_callback(interaction):
        nonlocal currentPage, sentMessage
        currentPage += 1
        await sentMessage.edit(embed=createHelpEmbed(pageNum=currentPage), view=theView)

    async def previous_callback(interaction):
        nonlocal currentPage, sentMessage
        currentPage -=1
        await sentMessage.edit(embed=createHelpEmbed(pageNum=currentPage), view=theView)
    
    nextButton = Button(label=">", style=ButtonStyle.blurple)
    nextButton.callback = next_callback
    previousButton = Button(label="<", style=ButtonStyle.blurple)
    previousButton.callback = previous_callback

    theView = View(timeout=180)
    theView.add_item(previousButton)
    theView.add_item(nextButton)
    sentMessage = await ctx.send(embed=createHelpEmbed(pageNum=1), view=theView)

@bot.command(name="anime", description="Generate a random anime")
async def anime(ctx):
    await ctx.send(warning)
    retries = 0
    while retries < max_retries:
        try: 
            fakeChrome = 'http://api.jikan.moe/v4/anime/' + str(random.randint(1,55555))
            response = requests.get(fakeChrome)
            animeData = response.json()
            animeTitle = animeData["data"]["title"]
            animeSynopsis = animeData["data"]['synopsis']
            animeUrl = animeData["data"]['url']
            animeImage = animeData["data"]['images']['jpg']['large_image_url']
            animeScore = animeData["data"]['score']
            animeRank = animeData["data"]['rank']
            animePopularity = animeData["data"]['popularity']
            animeMembers = animeData["data"]['members']
            embed = nextcord.Embed(title=animeTitle, description=animeSynopsis, url=animeUrl, colour=0x7289da)
            embed.set_image(url=animeImage)
            embed.set_footer(text=f"Score: {animeScore} | Rank: {animeRank} | Members: {animeMembers} | Popularity: {animePopularity}")
            await ctx.send(embed=embed)
            return
        except Exception as e:
            #await ctx.send(f"An error has occurred: {str(e)}, please try again.")
            retries += 1
            if retries < max_retries:
                await ctx.send(f"An error has occurred: {str(e)}, Retrying (Attempts: {retries}/{max_retries})")
            else:
                await ctx.send(f"Max retries reached. Command failed.")
                break

@bot.command(name="rdmmsg")
async def rdmmsg(ctx, user: nextcord.User):
    await ctx.send(warning)
    messages = await ctx.channel.history(limit=1000).flatten()
    userMessages = [message for message in messages if message.author == user]
    #avatarUrl = user.avatar.url
    if userMessages:
        randomUserMessage = random.choice(userMessages)
        embed = nextcord.Embed(title=f"{user.display_name} said:", description=randomUserMessage.content, colour=0xFF0000)
        #embed.set_image(avatarUrl)
        embed.set_footer(text=f"Message sent at: {randomUserMessage.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No messages found from {user.display_name}. Please try again later")

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

#CHAT GPT
@bot.command()
async def ask(ctx: commands.Context, *, prompt: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "text-ada-001",
            #"model": "text-babbage-001",
            #"model": "text-curie-001",
            #"model": "text-davinci-003",
            "prompt": prompt,
            "temperature": 0.5,
            "max_tokens": 50,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "best_of": 1
        }
        headers = {"Authorization": f"Bearer {API}"}
        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as resp:
            response = await resp.json()
            embed = nextcord.Embed(title="Hayasaka says:", description=response["choices"][0]["text"])
            await ctx.reply(warning)
            await ctx.reply(embed=embed)

#SLASH CMDS
@bot.slash_command(name="test", description="Check command")
async def test(interaction : Interaction):
    await interaction.send("Ishigami's slash command working as intended!", ephemeral=False)

@bot.slash_command(name="yes", description="WateryScoobydoo only!")
async def yes(interaction : Interaction):
    await interaction.send("https://discord.com/developers/active-developer :white_check_mark:", ephemeral=True)

@bot.slash_command(name="ping", description="Ping pong")
async def ping(interaction : Interaction):
    botPing = round(bot.latency*1000) 
    await interaction.response.send_message(f"{interaction.user.mention} Pong - {botPing}ms!", ephemeral=False)

@bot.slash_command(name="say", description="Type here to send a message!")
async def say(interaction : Interaction, message:str):
    await interaction.response.send_message(f"**{interaction.user.mention} says:** {message}")

#@bot.slash_command(name="quote", description="Get a quote from a user", type=6, required=True)
#async def quote(interaction : Interaction, user: nextcord.Member):
#    if user.id in quotes and quotes[user.id]:
#        randomQuote = random.choice(quotes[user.id])
#        await interaction.response.send_message(f"Quote from {interaction.user.mention}: {randomQuote}")
#    else:
#        await interaction.response.send_message(f"No quotes specified for {interaction.user.mention}, please try again")

#@bot.slash_command(name="userinfo", description="Get information about a user", options=[nextcord.Option(name='user', description='Select a user', type=6, required=True)])
#async def userinfo(interaction : Interaction, user: nextcord.Member):
#    embed = nextcord.Embed(title=f"User Information for {user.display_name}", colour=user.colour)
#    embed.add_field(name="Username", value=user.name, inline=True)
#    embed.add_field(name="Discriminator", value=user.discriminator, inline=True)
#    embed.add_field(name="User ID", value=user.id, inline=True)
#    embed.add_field(name="Joined Server", value=user.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
#    embed.add_field(name="Created Account", value=user.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
#    embed.set_thumbnail(url=user.avatar_url)
#    await interaction.response.send_message(embed=embed)
                                                
@bot.slash_command(name="f1", description="Roll for your Formula 1 driver")
async def f1(interaction : Interaction):
    f1drivers = [
        '#1 | Max VERSTAPPEN', '#11 | Sergio PEREZ', '#16 | Charles LECLERC', '#55 | Carlos SAINZ', '#44 | Lewis HAMILTON', 
        '#63 | George RUSSELL', '#10 | Pierre GASLY', '#31 | Esteban OCON', '#4 | Lando NORRIS', '#81 | Oscar PIASTRI', 
        '#24 | Guanyu ZHOU', '#77 | Valtteri BOTTAS', '#14 | Fernando ALONSO', '#18 | Lance STROLL', '#20 | Kevin MAGNUSSEN', 
        '#27 | Nico HULKENBERG', '#22 | Yuki TSUNODA', '#3 | Daniel RICCIARDO', '#23 | Alex ALBON', '#2 | Logan SARGEANT'
    ]
    await interaction.response.send_message(f"Your choosen driver is: **{random.choice(f1drivers)}**", ephemeral=False)

@bot.slash_command(name="f1team", description="Roll for your Formula 1 team")
async def f1team(interaction : Interaction):
    f1teams = [
        'MERCEDES', 'FERRARI', 'ALPINE', 'ALPHATAURI', 'MCLAREN', 
        'HAAS', 'WILLIAMS', 'ALFA ROMEO', 'RED BULL RACING', 'ASTON MARTIN'
    ]
    await interaction.response.send_message(f"Your choosen team is: **{random.choice(f1teams)}**", ephemeral=False)

@bot.slash_command(name="8ball", description="Let 8Ball predict the future")
async def ball(interaction : Interaction, question:str):
    eightball = [
            'It is certain.', 'It is decidedly so.', 'Without a doubt.', "I'm feeling well.", 'Yes - definitely.',
            'You may rely on it.', 'As I see it yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.',
            'Reply hazy, try again.', 'Better not tell you now.', 'Concentrate and ask again.', "Don't count on it.",
            'I cannot predict now.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtfull.',
            'I am tired. *proceeds with sleeping*.', 'As I see it, yes.', 'Yes.', 'Positive.', 'From my point of view, yes.',
            'Convinced.', 'Most likley.', 'Chances point to high.', 'No.', 'Negative.', 'Not convinced.', 'Perhaps.',
            'Not sure', 'Maybe', "I'm too lazy to predict."
        ]
    await interaction.response.send_message(f"Hey, {interaction.user.mention}!\n:8ball: *Question:* **{question}**\n:8ball: *Answer:* **{random.choice(eightball)}**", ephemeral=False)

bot.run(os.getenv("TOKEN"))