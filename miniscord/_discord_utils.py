import discord


async def delete_message(message: discord.Message) -> bool:
    try:
        await message.delete()
        return True
    except discord.Forbidden:
        pass
    except discord.NotFound:
        pass
    return False

def channel_id(message: discord.Message) -> str:
    is_direct = message.channel.type == discord.ChannelType.private
    if not is_direct:
        return f'{message.guild.id}/{message.channel.id}'
    else:
        return message.author.id

def sender_id(message: discord.Message) -> str:
    is_direct = message.channel.type == discord.ChannelType.private
    if not is_direct:
        return f'{channel_id(message)}/{message.author.id}'
    else:
        return message.author.id
