from asyncio import sleep
from re import search
from typing import Union

from discord import MISSING, PermissionOverwrite, Member, Role, Message, Thread
from discord.utils import _MissingSentinel
from discord import NotFound

__all__ = [
    'dshell_get_channel',
    'dshell_get_channels',
    'dshell_get_thread',
    'dshell_get_channels_in_category',
    'dshell_create_text_channel',
    'dshell_create_thread_message',
    'dshell_delete_channel',
    'dshell_delete_channels',
    'dshell_delete_thread',
    'dshell_create_voice_channel',
    'dshell_edit_text_channel',
    'dshell_edit_voice_channel',
    'dshell_edit_thread'
]

async def utils_get_message(ctx: Message, message: Union[int, str]) -> Message:
    """
    Returns the message object of the specified message ID or link.
    Message is only available in the same server as the command and in the same channel.
    If the message is a link, it must be in the format: https://discord.com/channels/{guild_id}/{channel_id}/{message_id}
    """

    if isinstance(message, int):
        return await ctx.channel.fetch_message(message)

    elif isinstance(message, str):
        match = search(r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)', message)
        if not match:
            raise Exception("Invalid message link format. Use a valid Discord message link.")
        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        if guild_id != ctx.guild.id:
            raise Exception("The message must be from the same server as the command !")

        return await ctx.guild.get_channel(channel_id).fetch_message(message_id)

    raise Exception(f"Message must be an integer or a string, not {type(message)} !")

async def utils_get_thread(ctx: Message, thread: Union[int, str]) -> Thread:
    """
    Returns the thread object of the specified thread ID or link.
    Thread is only available in the same server as the command and in the same channel.
    If the thread is a link, it must be in the format: https://discord.com/channels/{guild_id}/{channel_id}/{message_id}
    """

    if isinstance(thread, int):
        return ctx.channel.get_thread(thread)

    elif isinstance(thread, str):
        match = search(r'https://discord\.com/channels/(\d+)/(\d+)(/\d+)?', thread)
        if not match:
            raise Exception("Invalid thread link format. Use a valid Discord thread link.")
        guild_id = int(match.group(1))
        message_id = int(match.group(2))
        channel_id = ctx.channel.id if len(match.groups()) == 3 else ctx.channel.id

        if guild_id != ctx.guild.id:
            raise Exception("The thread must be from the same server as the command !")

        try:
            c = await ctx.guild.get_channel(channel_id).fetch_message(message_id)
            return c.thread
        except NotFound:
            raise Exception(f"Thread with ID {message_id} not found in channel {channel_id} !")

    raise Exception(f"Thread must be an integer or a string, not {type(thread)} !")


async def dshell_get_channel(ctx: Message, name):
    """
    Returns the channel object of the channel where the command was executed or the specified channel.
    """

    if isinstance(name, str):
        return next((c.id for c in ctx.channel.guild.channels if c.name == name), None)

    raise Exception(f"Channel must be an integer or a string, not {type(name)} !")


async def dshell_get_channels(ctx: Message, name=None, regex=None):
    """
    Returns a list of channels with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the server.
    """
    if name is not None and not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if regex is not None and not isinstance(regex, str):
        raise Exception(f"Regex must be a string, not {type(regex)} !")

    from .._DshellParser.ast_nodes import ListNode
    channels = ListNode([])

    for channel in ctx.channel.guild.channels:
        if name is not None and channel.name == str(name):
            channels.add(channel.id)

        elif regex is not None and search(regex, channel.name):
            channels.add(channel.id)

    return channels

async def dshell_get_channels_in_category(ctx: Message, category=None, name=None, regex=None):
    """
    Returns a list of channels in a specific category with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the specified category.
    """

    if category is None and ctx.channel.category is not None:
        category = ctx.channel.category.id

    if category is None:
        raise Exception("Category must be specified !")

    if not isinstance(category, int):
        raise Exception(f"Category must be an integer, not {type(category)} !")

    if name is not None and not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if regex is not None and not isinstance(regex, str):
        raise Exception(f"Regex must be a string, not {type(regex)} !")

    from .._DshellParser.ast_nodes import ListNode
    channels = ListNode([])

    category_channel = ctx.channel.guild.get_channel(category)
    if category_channel is None or not hasattr(category_channel, 'channels'):
        raise Exception(f"Category {category} not found or does not contain channels !")

    for channel in category_channel.channels:
        if name is not None and channel.name == str(name):
            channels.add(channel.id)

        elif regex is not None and search(regex, channel.name):
            channels.add(channel.id)

    return channels

async def dshell_create_text_channel(ctx: Message,
                                     name,
                                     category=None,
                                     position=MISSING,
                                     slowmode=MISSING,
                                     topic=MISSING,
                                     nsfw=MISSING,
                                     permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                     reason=None):
    """
    Creates a text channel on the server
    """

    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode must be an integer, not {type(slowmode)} !")

    if not isinstance(topic, _MissingSentinel) and not isinstance(topic, str):
        raise Exception(f"Topic must be a string, not {type(topic)} !")

    if not isinstance(nsfw, _MissingSentinel) and not isinstance(nsfw, bool):
        raise Exception(f"NSFW must be a boolean, not {type(nsfw)} !")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_text_channel(str(name),
                                                          category=channel_category,
                                                          position=position,
                                                          slowmode_delay=slowmode,
                                                          topic=topic,
                                                          nsfw=nsfw,
                                                          overwrites=permission,
                                                          reason=reason)

    return created_channel.id


async def dshell_create_voice_channel(ctx: Message,
                                      name,
                                      category=None,
                                      position=MISSING,
                                      bitrate=MISSING,
                                      permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                      reason=None):
    """
    Creates a voice channel on the server
    """
    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(bitrate, _MissingSentinel) and not isinstance(bitrate, int):
        raise Exception(f"Bitrate must be an integer, not {type(bitrate)} !")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_voice_channel(str(name),
                                                           category=channel_category,
                                                           position=position,
                                                           bitrate=bitrate,
                                                           overwrites=permission,
                                                           reason=reason)

    return created_channel.id


async def dshell_delete_channel(ctx: Message, channel=None, reason=None, timeout=0):
    """
    Deletes a channel.
    You can add a waiting time before it is deleted (in seconds)
    """
    if not isinstance(timeout, int):
        raise Exception(f'Timeout must be an integer, not {type(timeout)} !')

    channel_to_delete = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_delete is None:
        raise Exception(f"Channel {channel} not found !")

    await sleep(timeout)

    await channel_to_delete.delete(reason=reason)

    return channel_to_delete.id


async def dshell_delete_channels(ctx: Message, name=None, regex=None, reason=None):
    """
    Deletes all channels with the same name and/or matching the same regex.
    If neither is set, it will delete all channels with the same name as the one where the command was executed.
    """
    if name is not None and not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if regex is not None and not isinstance(regex, str):
        raise Exception(f"Regex must be a string, not {type(regex)} !")

    for channel in ctx.channel.guild.channels:

        if name is not None and channel.name == str(name):
            await channel.delete(reason=reason)

        elif regex is not None and search(regex, channel.name):
            await channel.delete(reason=reason)


async def dshell_edit_text_channel(ctx: Message,
                                   channel=None,
                                   name=None,
                                   position=MISSING,
                                   slowmode=MISSING,
                                   topic=MISSING,
                                   nsfw=MISSING,
                                   permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                   reason=None):
    """
    Edits a text channel on the server
    """

    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode must be an integer, not {type(slowmode)} !")

    if not isinstance(topic, _MissingSentinel) and not isinstance(topic, str):
        raise Exception(f"Topic must be a string, not {type(topic)} !")

    if not isinstance(nsfw, _MissingSentinel) and not isinstance(nsfw, bool):
        raise Exception(f"NSFW must be a boolean, not {type(nsfw)} !")

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               slowmode_delay=slowmode if slowmode is not MISSING else channel_to_edit.slowmode_delay,
                               topic=topic if topic is not MISSING else channel_to_edit.topic,
                               nsfw=nsfw if nsfw is not MISSING else channel_to_edit.nsfw,
                               overwrites=permission if permission is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id


async def dshell_edit_voice_channel(ctx: Message,
                                    channel=None,
                                    name=None,
                                    position=MISSING,
                                    bitrate=MISSING,
                                    permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                    reason=None):
    """
    Edits a voice channel on the server
    """
    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(bitrate, _MissingSentinel) and not isinstance(bitrate, int):
        raise Exception(f"Bitrate must be an integer, not {type(bitrate)} !")

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               bitrate=bitrate if bitrate is not MISSING else channel_to_edit.bitrate,
                               overwrites=permission if permission is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id


async def dshell_create_thread_message(ctx: Message,
                                       name,
                                       message: Union[int, str] = None,
                                       archive=MISSING,
                                       slowmode=MISSING):
    """
    Creates a thread from a message.
    """

    if message is None:
        message = ctx.id

    message = await utils_get_message(ctx, message)


    if not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if not isinstance(archive, _MissingSentinel) and not isinstance(archive, int):
        raise Exception(f"Auto archive duration must be an integer, not {type(archive)} !")

    if not isinstance(archive, _MissingSentinel) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode delay must be an integer, not {type(slowmode)} !")

    if not isinstance(slowmode, _MissingSentinel) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    thread = await message.create_thread(name=name,
                                         auto_archive_duration=archive,
                                         slowmode_delay=slowmode)

    return thread.id

async def dshell_edit_thread(ctx: Message,
                             thread: Union[int, str] = None,
                             name=None,
                             archive=MISSING,
                             slowmode=MISSING,
                             reason=None):
    """ Edits a thread.
    """
    if thread is None:
        thread = ctx.thread

    if thread is None:
        raise Exception("Thread must be specified !")

    thread = await utils_get_thread(ctx, thread)

    if not isinstance(name, _MissingSentinel) and not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if not isinstance(archive, _MissingSentinel) and not isinstance(archive, int):
        raise Exception(f"Auto archive duration must be an integer, not {type(archive)} !")

    if not isinstance(archive, _MissingSentinel) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode delay must be an integer, not {type(slowmode)} !")

    if not isinstance(slowmode, _MissingSentinel) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    await thread.edit(name=name if name is not None else thread.name,
                      auto_archive_duration=archive if archive is not MISSING else thread.auto_archive_duration,
                      slowmode_delay=slowmode if slowmode is not MISSING else thread.slowmode_delay,
                      reason=reason)


async def dshell_get_thread(ctx: Message, message: Union[int, str] = None):
    """
    Returns the thread object of the specified thread ID.
    """

    if message is None:
        message = ctx.id

    message = await utils_get_message(ctx, message)

    if not hasattr(message, 'thread'):
        return None

    thread = message.thread

    if thread is None:
        return None

    return thread.id


async def dshell_delete_thread(ctx: Message, thread: Union[int, str] = None, reason=None):
    """
    Deletes a thread.
    """

    if thread is None:
        thread = ctx.id

    thread = await utils_get_message(ctx, thread)

    if not hasattr(thread, 'thread'):
        raise Exception("The specified message does not have a thread !")

    if thread.thread is None:
        raise Exception("The specified message does not have a thread !")

    await thread.thread.delete(reason=reason)

    return thread.thread.id

