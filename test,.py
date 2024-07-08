from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

with open('api.text') as f:
    API_TOKEN = f.read()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def check_update(message: Message):
    await message.answer(f"Your id is {message.from_user.id}")

if __name__=='__main__':
    dp.run_polling(bot)