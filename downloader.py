import asyncio
import os
import config
import requests

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile
import logging

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


async def download_video(url: str) -> str:
    logging.info(f"Downloading video from: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        filename = 'downloaded_video.mp4'
        with open(filename, 'wb') as f:
            f.write(response.content)
        logging.info("Video downloaded successfully.")
        return filename
    else:
        logging.error(f"Failed to download video. Status code: {response.status_code}")
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
    logging.info("Starting bot...")
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()