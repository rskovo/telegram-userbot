import asyncio
from telethon import TelegramClient
from telethon.tl.types import UserStatusOnline
import datetime
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
target = os.getenv('TARGET_USERNAME')

client = TelegramClient('session', api_id, api_hash)

last_status = None
last_change_time = None

total_online = 0
total_offline = 0

def format_duration(seconds):
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours} час{'а' if 2 <= hours % 10 <= 4 else 'ов'}")
    if minutes > 0:
        parts.append(f"{minutes} минут{'ы' if 2 <= minutes % 10 <= 4 else ''}")
    if not parts:
        parts.append("менее минуты")
    return ' '.join(parts)

async def notify_me(message):
    me = await client.get_me()
    await client.send_message(me.id, message)

async def monitor_status():
    global last_status, last_change_time, total_online, total_offline

    user = await client.get_entity(target)
    last_change_time = datetime.datetime.now()

    while True:
        current_status = user.status
        now = datetime.datetime.now()

        if isinstance(current_status, UserStatusOnline):
            current = 'online'
        else:
            current = 'offline'

        if last_status is None:
            last_status = current
            last_change_time = now
            await notify_me(f"{target} текущий статус: {current}")
        elif current != last_status:
            delta = (now - last_change_time).total_seconds()

            if last_status == 'online':
                total_online += delta
                message = (f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {target} вышла из сети, "
                           f"была онлайн {format_duration(delta)}\n"
                           f"Общее время в сети сегодня: {format_duration(total_online)}")
                await notify_me(message)

            else:
                total_offline += delta
                message = (f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {target} снова в сети, "
                           f"была офлайн {format_duration(delta)}")
                await notify_me(message)

            last_status = current
            last_change_time = now

        await asyncio.sleep(30)  # Проверяем каждые 30 секунд

async def main():
    await client.start()
    await monitor_status()

with client:
    client.loop.run_until_complete(main())
