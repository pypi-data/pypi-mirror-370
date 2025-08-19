from re import search

from discord import Embed, Message, NotFound
from discord.ext import commands

__all__ = [
    'dshell_send_message',
    'dshell_delete_message',
    'dshell_purge_message',
    'dshell_edit_message',
    'dshell_get_hystory_messages',
    'dshell_research_regex_in_content',
    'dshell_add_reactions',
    'dshell_remove_reactions',
    'dshell_clear_message_reactions',
    'dshell_clear_one_reactions'
]


async def dshell_send_message(ctx: Message, message=None, delete=None, channel=None, embeds=None):
    """
    Sends a message on Discord
    """
    if delete is not None and not isinstance(delete, (int, float)):
        raise Exception(f'Delete parameter must be a number (seconds) or None, not {type(delete)} !')

    channel_to_send = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_send is None:
        raise Exception(f'Channel {channel} not found!')

    from .._DshellParser.ast_nodes import ListNode

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    else:
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    sended_message = await channel_to_send.send(message,
                                                delete_after=delete,
                                                embeds=embeds)

    return sended_message.id


async def dshell_delete_message(ctx: Message, message=None, reason=None, delay=0):
    """
    Deletes a message
    """

    delete_message = ctx if message is None else ctx.channel.get_partial_message(
        message)  # builds a reference to the message (even if it doesn't exist)

    if not isinstance(delay, int):
        raise Exception(f'Delete delay must be an integer, not {type(delay)} !')

    if delay > 3600:
        raise Exception(f'The message deletion delay is too long! ({delay} seconds)')

    await delete_message.delete(delay=delay, reason=reason)


async def dshell_purge_message(ctx: Message, message_number, channel=None, reason=None):
    """
    Purges messages from a channel
    """

    if not isinstance(message_number, int):
        raise Exception(f'Message number must be an integer, not {type(message_number)} !')

    purge_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if purge_channel is None:
        raise Exception(f"Channel {channel} to purge not found!")

    await purge_channel.purge(limit=message_number, reason=reason)


async def dshell_edit_message(ctx: Message, message, new_content=None, embeds=None):
    """
    Edits a message
    """
    edit_message = ctx.channel.get_partial_message(
        message)  # builds a reference to the message (even if it doesn't exist)

    if embeds is None:
        embeds = []

    elif isinstance(embeds, Embed):
        embeds = [embeds]

    await edit_message.edit(content=new_content, embeds=embeds)

    return edit_message.id


async def dshell_get_hystory_messages(ctx: Message, channel=None, limit=None):
    """
    Searches for messages matching a regex in a channel
    """

    if limit is not None and not isinstance(limit, int):
        raise Exception(f"Limit must be an integer or None, not {type(limit)}!")

    search_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if search_channel is None:
        raise Exception(f"Channel {channel} to search not found!")

    from .._DshellParser.ast_nodes import ListNode

    messages = ListNode([])
    async for message in search_channel.history(limit=limit):
        messages.add(message)

    if not messages:
        raise commands.CommandError(f"No messages in {search_channel.mention}.")

    return messages


async def dshell_research_regex_in_content(ctx: Message, regex, content=None):
    """
    Searches for a regex in a specific message content
    """

    if not isinstance(regex, str):
        raise Exception(f"Regex must be a string, not {type(regex)}!")

    if not search(regex, str(content) if content is not None else ctx.content):
        return False

    return True


async def dshell_add_reactions(ctx: Message, reactions, message=None):
    """
    Adds reactions to a message
    """
    message = ctx if message is None else ctx.channel.get_partial_message(
        message)  # builds a reference to the message (even if it doesn't exist)

    if isinstance(reactions, str):
        reactions = (reactions,)

    for reaction in reactions:
        await message.add_reaction(reaction)

    return message.id


async def dshell_remove_reactions(ctx: Message, reactions, message=None):
    """
    Removes reactions from a message
    """
    message = ctx if message is None else ctx.channel.get_partial_message(
        message)  # builds a reference to the message (even if it doesn't exist)

    if isinstance(reactions, str):
        reactions = [reactions]

    for reaction in reactions:
        await message.clear_reaction(reaction)

    return message.id

async def dshell_clear_message_reactions(ctx: Message, message):
    """
    Clear all reaction on the target message
    """
    if not isinstance(message, int):
        raise Exception(f'Message must be integer, not {type(message)}')

    target_message = await ctx.channel.fetch_message(message)

    if target_message is None:
        raise Exception(f'Message not found !')

    await target_message.clear_reactions()

async def dshell_clear_one_reactions(ctx: Message, message, emoji):
    """
    Clear one emoji on the target message
    """
    if not isinstance(message, int):
        raise Exception(f'Message must be integer, not {type(message)}')

    if not isinstance(emoji, str):
        raise Exception(f'Emoji must be string, not {type(emoji)}')

    try:
        target_message = await ctx.channel.fetch_message(message)
    except NotFound:
        raise Exception(f'Message not found !')

    await target_message.clear_reaction(emoji)
