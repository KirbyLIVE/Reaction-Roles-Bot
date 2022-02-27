import discord
from discord.ext import commands
import asyncio
import random
import json
import os
import datetime

intents = discord.Intents().all()
client = commands.Bot(command_prefix = "(Prefix)", intents=intents)

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('(Game)'))
  print("Bot is ready")

@client.command(name="create")
async def self_role(ctx):
    await ctx.send("Answer These Question In Next 2Min!")

    questions = ["Enter Message: ", "Enter Emojis: ", "Enter Roles: ", "Enter Channel: "]
    answers = []

    def check(user):
        return user.author == ctx.author and user.channel == ctx.channel
    
    for question in questions:
        await ctx.send(question)

        try:
            msg = await client.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Type Faster Next Time!")
            return
        else:
            answers.append(msg.content)

    emojis = answers[1].split(" ")
    roles = answers[2].split(" ")
    c_id = int(answers[3][2:-1])
    channel = client.get_channel(c_id)

    client_msg = await channel.send(answers[0])

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)

    self_roles[str(client_msg.id)] = {}
    self_roles[str(client_msg.id)]["emojis"] = emojis
    self_roles[str(client_msg.id)]["roles"] = roles

    with open("selfrole.json", "w") as f:
        json.dump(self_roles, f)

    for emoji in emojis:
        await client_msg.add_reaction(emoji)

@client.event
async def on_raw_reaction_add(payload):
    msg_id = payload.message_id

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)

    if payload.member == client.user:
        return 
    
    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]['emojis']:
            emojis.append(emoji)

        for role in self_roles[str(msg_id)]['roles']:
            roles.append(role)
        
        guild = client.get_guild(payload.guild_id)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == emojis[i]:
                selected_role = roles[i]

                role = discord.utils.get(guild.roles, name=selected_role)

                await payload.member.add_roles(role)
                await payload.member.send(f"You Got {selected_role} Role!")

@client.event
async def on_raw_reaction_remove(payload):
    msg_id = payload.message_id

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)
    
    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]['emojis']:
            emojis.append(
                emoji)

        for role in self_roles[str(msg_id)]['roles']:
            roles.append(role)
        
        guild = client.get_guild(payload.guild_id)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == emojis[i]:
                selected_role = roles[i]

                role = discord.utils.get(guild.roles, name=selected_role)

                member = await(guild.fetch_member(payload.user_id))
                if member is not None:
                    await member.remove_roles(role)


client.run(os.environ["TOKEN"])
