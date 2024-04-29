import asyncio
import os
import config
import requests

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


async def download_video(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        filename = 'downloaded_video.mp4'
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        return None


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Send me the link to the video you want to download.")


@dp.message_handler()
async def process_video(message: types.Message):
    url = message.text
    if url.endswith('.mkv') or url.endswith('.mp4'):
        file_path = await download_video(url)
        if file_path:
            await message.reply_document(InputFile(file_path))
            os.remove(file_path)
        else:
            await message.reply("Failed to download the video. Please check the URL and try again.")
    else:
        await message.reply("Unsupported file format. Please provide a link to a video in MKV or MP4 format.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()