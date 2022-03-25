import discord
from reddit import search_user
from enums import ReturnType

client = discord.Client()

with open('token.txt', 'r') as t:
    token = t.read()
    t.close()


@client.event
async def on_ready():
    print("Log on as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel).lower() == 'roles':
        discord_sent_username = str(message.content).lower()
        user = message.author
        # Search Messages through reddit for Discord Sent User
        returnType = search_user(discord_sent_username)
        if returnType == ReturnType.Accepted:
            # Assign the id of the role
            role = discord.Role
            role.id = 956182931485900800
            # Give the user the role
            print("Verified user: ", user, " with user id: ", user.id)
            await user.add_roles(role)
            discord_message = "Verified user: " + str(user) + " with user id: " + str(user.id)
            await message.channel.send(discord_message)
        elif returnType == ReturnType.Declined:
            print("Not Validated user: ", user, " with user id: ", user.id)
            discord_message = "Sorry but it seems that the user: " + str(user) + " with user id: " + str(
                user.id) + " can't be verified."
            await message.channel.send(discord_message)
            await message.channel.send("Try again after you get some activity on /r/greece.")
        elif returnType == ReturnType.NoSuchUsername:
            print("There's no message on reddit from the user: ", discord_sent_username, " and subject 'Discord'")
            discord_message = "There's no message on reddit from the user: " + str(
                discord_sent_username) + " and subject 'Discord'"
            await message.channel.send(discord_message)
        elif returnType == ReturnType.AlreadyInDiscord:
            print("The user: ", user, " is already on the server.")
            discord_message = "The user: " + str(user) + " is already on the server."
            await message.channel.send(discord_message)


client.run(token)