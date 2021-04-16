import logging

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.utils import get_display_name

from config import api_hash
from config import api_id
from config import bot_token
from config import phone_number

logging.basicConfig(level=logging.WARNING)

client = TelegramClient('session', api_id, api_hash)
client.start(bot_token=bot_token)

user = TelegramClient('user', api_id, api_hash)
user.start(phone_number)


def escape(s: str) -> str:
    return (
        s
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def get_user_info(user):
    lines = [
        f'<b>{escape(get_display_name(user))}</b>',
        f'    id: <code>{user.id}</code>',
        f'    first: <code>{escape(user.first_name)}</code>',
    ]

    if user.last_name is not None:
        lines.append(f'    last: <code>{escape(user.last_name)}</code>')
    if user.username is not None:
        lines.append(f'    username: @{user.username}')
    if user.bot:
        lines.append(f'    bot: <code>{user.bot}</code>')
    if user.scam:
        lines.append(f'    scam: <code>{user.scam}</code>')
    if user.fake:
        lines.append(f'    fake: <code>{user.fake}</code>')
    lines.append(f'    <a href="tg://user?id={user.id}">link</a>')

    return lines


@client.on(NewMessage(func=lambda e: e.is_private, incoming=True))
async def private_message(event):
    await event.reply('Hi, I help with reporting spam in @SpamBlockers.')


@client.on(
    NewMessage(
        func=lambda e: e.is_group and e.is_channel,
        pattern=(
            r'^/report (?:https?://)?(?:t\.me|'
            r'telegram\.(?:dog|me))/(\w+)/(\d+)$'
        ),
    ),
)
async def on_report(event):
    chat = event.pattern_match.group(1)
    id = int(event.pattern_match.group(2))

    message = await user.get_messages(chat, ids=id)
    if message is None:
        await event.reply('Message not found')
        return

    forward = await message.forward_to(event.chat_id)

    sender = await message.get_sender()
    lines = get_user_info(sender)

    await forward.reply('\n'.join(lines), parse_mode='html')


@client.on(
    NewMessage(
        func=lambda e: (
            e.is_group and
            e.is_channel and
            e.forward is not None
        ),
    ),
)
async def on_group_message(event):
    if (await event.get_input_sender()) is None:
        return

    if (await event.forward.get_input_chat()) is not None:
        await event.reply('Channel')
        return

    if await event.forward.get_input_sender() is None:
        await event.reply('Hidden forward')
        return

    sender = await event.forward.get_sender()
    lines = get_user_info(sender)

    await event.reply('\n'.join(lines), parse_mode='html')


client.run_until_disconnected()
