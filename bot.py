import logging

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.utils import get_display_name

from config import api_hash
from config import api_id
from config import bot_token

logging.basicConfig(level=logging.WARNING)

client = TelegramClient('session', api_id, api_hash)
client.start(bot_token=bot_token)


def escape(s: str) -> str:
    return (
        s
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


@client.on(NewMessage(func=lambda e: e.is_private))
async def private_message(event):
    await event.reply('Hi, I help with reporting spam in @SpamBlockers.')


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
    if (await event.forward.get_input_chat()) is not None:
        await event.reply('Channel')
        return

    if await event.forward.get_input_sender() is None:
        await event.reply('Hidden forward')
        return

    sender = await event.forward.get_sender()
    lines = [
        f'<b>{escape(get_display_name(sender))}</b>',
        f'    id: <code>{sender.id}</code>',
        f'    first: <code>{escape(sender.first_name)}</code>',
    ]

    if sender.last_name is not None:
        lines.append(f'    last: <code>{escape(sender.last_name)}</code>')
    if sender.username is not None:
        lines.append(f'    username: @{sender.username}')
    lines.append(f'    scam: <code>{sender.scam}</code>')

    await event.reply('\n'.join(lines), parse_mode='html')


client.run_until_disconnected()
