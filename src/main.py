import os
import asyncio
from pytubefix import YouTube
from pytubefix.cli import on_progress
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.exceptions import TelegramEntityTooLarge
from pytubefix.exceptions import AgeRestrictedError, RegexMatchError

load_dotenv()


bot = Bot(token=os.getenv('BOT_TOKEN'))

dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        'Hello! Send me a link to a youtube video and i will send you an mp4 file. If you only need audio, type "/a" at the end of the link.'
    )


@dp.message()
async def send_video(message: types.Message):
    temp = await message.answer(
        'processing...'
    )
    
    audio = False
    url = message.text
    if url[-2:] == '/a':
        audio = True
        url = url[:-2]
    
    try:
        yt = YouTube(url, on_progress_callback = on_progress)
    except RegexMatchError:
        return await bot.edit_message_text(
            'Wrong URL',
            chat_id=message.chat.id,
            message_id=temp.message_id
        )
        
    try:
        ys = yt.streams.get_highest_resolution()
    except AgeRestrictedError:
        return await bot.edit_message_text(
            'This video is age restricted and cannot be downloaded',
            chat_id=message.chat.id,
            message_id=temp.message_id
        )
        
    try:
        if audio:
            await bot.send_audio(message.chat.id, types.URLInputFile(ys.url), title=yt.title)
        else:
            await bot.send_video(message.chat.id, types.URLInputFile(ys.url))
        await bot.delete_message(message.chat.id, temp.message_id)
    except TelegramEntityTooLarge:
        return await bot.edit_message_text(
            'This video is too big',
            chat_id=message.chat.id,
            message_id=temp.message_id
        )
        

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())