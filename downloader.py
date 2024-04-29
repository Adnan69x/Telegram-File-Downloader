import logging
import os
import config
import aiohttp
import youtube_dl

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


async def download_file(url: str, filename: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filename, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    return filename
                else:
                    logger.error(f"Failed to download file. Status code: {response.status}")
                    return None
    except Exception as e:
        logger.exception("Error occurred while downloading file:")
        return None


async def download_video(url: str) -> str:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': 'downloaded_video.mp4',
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['formats'][0]['url']
            filename = 'downloaded_video.mp4'
            await download_file(video_url, filename)
            return filename
    except Exception as e:
        logger.exception("Error occurred while downloading video:")
        return None


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Send me the link to the video you want to download.")


@dp.message_handler()
async def process_video(message: types.Message):
    url = message.text.strip()

    if url.endswith('.mkv') or url.endswith('.mp4'):
        file_path = await download_file(url, 'downloaded_video.mkv')
    else:
        file_path = await download_video(url)

    if file_path:
        await message.reply_document(InputFile(file_path))
        os.remove(file_path)
    else:
        await message.reply("Failed to download the video. Please check the URL and try again.")


if __name__ == '__main__':
    logger.info("Starting bot...")
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(dp.start_polling())
        loop.run_forever()
    except Exception as e:
        logger.exception("An error occurred in the main loop:")