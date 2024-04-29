import asyncio
import os
import config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile
import aiohttp
import youtube_dl
from youtube_dl.utils import ExtractorError

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


async def download_video(url: str) -> str:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': 'downloaded_video.mp4'
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except youtube_dl.DownloadError:
        return None
    return 'downloaded_video.mp4'


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
            await message.reply("Failed to download the video. The requested format may not be available.")
    else:
        await message.reply("Unsupported file format. Please provide a link to a video in MKV or MP4 format.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()