import discord
from discord.utils import get
from reddit import search_user, read_csv, search_user_stats
import re

from enums import ReturnType


import asyncpraw

client = discord.Client()
client_id, client_secret, password, user_agent, username = read_csv()




with open('token.txt', 'r') as t:
    token = t.read()
    t.close()


@client.event
async def on_ready():
    print("Log on as {0.user}".format(client))


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#     if str(message.channel).lower() == 'roles':
#         discord_sent_username = str(message.content).lower()
#         user = message.author
#         # Search Messages through reddit for Discord Sent User
#         returnType = search_user(discord_sent_username)
#         if returnType == ReturnType.Accepted:
#             # Assign the id of the role
#             role = discord.Role
#             role.id = 956182931485900800
#             # Give the user the role
#             print("Verified user: ", user, " with user id: ", user.id)
#             await user.add_roles(role)
#             discord_message = "Verified user: " + str(user) + " with user id: " + str(user.id)
#             await message.channel.send(discord_message)
#         elif returnType == ReturnType.Declined:
#             print("Not Validated user: ", user, " with user id: ", user.id)
#             discord_message = "Sorry but it seems that the user: " + str(user) + " with user id: " + str(
#                 user.id) + " can't be verified."
#             await message.channel.send(discord_message)
#             await message.channel.send("Try again after you get some activity on /r/greece.")
#         elif returnType == ReturnType.NoSuchUsername:
#             print("There's no message on reddit from the user: ", discord_sent_username, " and subject 'Discord'")
#             discord_message = "There's no message on reddit from the user: " + str(
#                 discord_sent_username) + " and subject 'Discord'"
#             await message.channel.send(discord_message)
#         elif returnType == ReturnType.AlreadyInDiscord:
#             print("The user: ", user, " is already on the server.")
#             discord_message = "The user: " + str(user) + " is already on the server."
#             await message.channel.send(discord_message)

@client.event
async def on_raw_reaction_add(payload):

    channel = client.get_channel(957100463369617470)
    postchannel = client.get_channel(956182853006270464)
    guild = client.get_guild(956182780251873311)
    message_id = 957032030036713575
    admin_role = guild.get_role(956182931485900800)
    verify_role = guild.get_role(957168862737104958)

    # print(payload)
    if payload.message_id == message_id:
        print('reacted to message')
        reddit = asyncpraw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    password=password,
                    user_agent=user_agent,
                    username=username,
                )
        async for message in reddit.inbox.unread():
            if str(message.subject).lower() == 'discord':

                user = message.author
                # TODO:Check db for existing account
                # parsed_disc_user = re.findall(".*#\d{4}", message.body)
                parsed_disc_user = message.body.strip().split('#')
                print('parsed: ', parsed_disc_user)
                print('payload: ', payload.member.name)

                if len(parsed_disc_user) > 0:
                    # Check if the user has reacted
                    if payload.member.name.lower() == parsed_disc_user[0].lower():

                        print(payload.member.name)
                        print(parsed_disc_user)
                        await user.load()
                        summary = await search_user_stats(user)
                        summary.append(f"Name on Discord: **{'#'.join(parsed_disc_user)}**")
                        summary.append(f"__Options for *{'#'.join(parsed_disc_user)}*:__ \n✅ - Verify\n⁉️- Verify and probate\n⛔ - No Verification")
                        # TODO: send @everyone to make a ping and then delete msg
                        msg = await postchannel.send('\n'.join(summary))
                        await msg.add_reaction(emoji='✅')
                        await msg.add_reaction(emoji='⁉️')
                        await msg.add_reaction(emoji='⛔')

                        def check(reaction, user):
                            for role in user.roles:
                                if role == admin_role:
                                    return True

                            return False

                        try:
                            # checking if there is a react on the added reactions
                            reaction, mod_user = await client.wait_for('reaction_add', check=check)

                            # print(dir(reaction))
                            # TODO: Add on the DB who approved.
                            # TODO: Welcome message on #general
                            # TODO: PM the user notifying that they have been verified/probated
                            print("UserID: ", payload.user_id)
                            # disc_user = guild.get_member(payload.user_id)

                            # print(dir(disc_user))

                            if reaction.emoji == '✅': #add role
                                print("HERE!!!!!")
                                await payload.member.add_roles(verify_role)
                                await msg.clear_reactions()

                            elif reaction.emoji == '⁉️': #add_role and probate
                                await payload.member.add_roles(verify_role)
                                msg2 = await postchannel.send(f'paste this to probate user `!probate <@{payload.user_id}>`')
                                await msg.clear_reactions()
                            elif reaction.emoji == '⛔': #deny and send message
                                print("NO ENTRY BIATCH")
                                await msg.clear_reactions()
                                # TODO: Kick user
                            message.mark_read()


                        except Exception as e:
                            print(e)











client.run(token)


