import discord
import asyncio
import imageio
import textwrap
import pickle
import json
from PIL import Image, ImageFont, ImageDraw
from random import randint

with open('../token.json') as tok:
    data = json.load(tok)
token = data["token"]

client = discord.Client()

def save(f, i):
    with open(f, 'wb+') as fo:
        pickle.dump(i, fo)

def load(f):
    with open(f, 'rb') as fo:
        return pickle.load(fo)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

    #Cage Face
    if message.content.startswith('!cage'):
        with open('./memes/cage.png', 'rb') as f:
            await client.send_file(message.channel, f)

    #Random OHNO
    if message.content.startswith('!ohno'):
        i = randint(1,9)
        img_path = './memes/ohno/' + str(i) + '.jpg'
        with open(img_path, 'rb') as f:
            await client.send_file(message.channel, f)

    #Spoilers
    if message.content.startswith('!spoiler'):
        #Get the text of the message
        msg = message.content[9:]

        #Build the image of the text
        text = msg
        font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSansMono.ttf', 14, encoding='unic')
        img = Image.new('RGBA', (350, 350))
        draw = ImageDraw.Draw(img)

        #Wrap the text
        y = 10
        lines = textwrap.wrap(text, width = 40)
        for line in lines:
            _, height = font.getsize(line)
            draw.text((10, y), line, font=font, fill=(215, 215, 215))
            y += height

        #Save the image
        img.save('./memes//spoiler/spoiler.png')

        #Build the gif
        images = []
        images.append(imageio.imread('./memes/spoiler/spoiler_header.png'))
        images.append(imageio.imread('./memes/spoiler/spoiler.png'))
        imageio.mimsave('./memes/spoiler/spoiler.gif', images, loop=1, duration=5)

        #Delete the original message
        await client.delete_message(message)

        #Print a notification of who posted the spoiler
        msg = "Spoiler posted by " + '<@' + message.author.id + '>'
        await client.send_message(message.channel, msg)

        #Post spoiler gif
        with open('./memes/spoiler/spoiler.gif', 'rb') as f:
            await client.send_file(message.channel, f)

    #Auto-tag trigger warnings
    if message.content.startswith('TW:') or message.content.startswith('tw:'):
        emj = discord.Emoji(name=':Trigger:', id='403757911920082955', 
                            require_colons=True, server=message.server)
        await client.add_reaction(message, emj)

    #Curse tracker
    if message.content.startswith('!curse'):
        try:
            curse = load('curse.bin')
        except FileNotFoundError:
            curse = 0

        try:
            yrs = int(message.content[7:])
        except ValueError:
            msg = '<@' + message.author.id + '>, the curse must be a number'
            await client.send_message(message.channel, msg)

            yrs = 0

        new_curse = curse + yrs
        if new_curse < 0:
            new_curse = 0
        save('curse.bin', new_curse)

        if yrs < 0 and new_curse > 0:
            msg = '<@' + message.author.id + '> decreased the curse by ' + str(yrs)[1:] + ' years!\nCurrent curse is ' + str(new_curse) + ' years'
        elif yrs < 0 and new_curse <= 0 and curse > 0:
            msg = '<@' + message.author.id + '> lifted the curse!'
        elif yrs < 0 and new_curse <= 0 and curse <= 0:
            msg = '<@' + message.author.id + '>, the curse cannot be lower than 0'
        elif yrs == 0:
            msg = '<@' + message.author.id + '>, the current curse is ' + str(new_curse) + ' years'
        elif yrs > 0 and new_curse > 0 and curse <= 0:
            msg = '<@' + message.author.id + '> reinstated the curse!\nCurrent curse is ' + str(new_curse) + ' years'
        else:
            msg = '<@' + message.author.id + '> increased the curse by ' + str(yrs) + ' years!\nCurrent curse is ' + str(new_curse) + ' years'

        await client.send_message(message.channel, msg)


client.run(token)
