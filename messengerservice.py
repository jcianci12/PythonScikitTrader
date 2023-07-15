import os
from telegram import Bot, InputFile

async def send_telegram_message(message: str):
    bot = Bot(token='6383670824:AAEBM5pxJHkgtPrQn9un74n2D1xqTC4MD6g')
    chat_id = '-1001813786868'
    if os.path.exists('performance.png'):
        photo = InputFile('performance.png')
        # await bot.send_photo(chat_id=chat_id, photo=photo, caption=message)

        await bot.sendPhoto(chat_id, (open('performance.png', "rb")))

    else:
        print('File not found')
