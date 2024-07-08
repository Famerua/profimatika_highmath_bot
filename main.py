from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message
from csv import DictReader, DictWriter, writer

with open("api.text") as f:
    API_TOKEN = f.read()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class FSMwaitnotification(StatesGroup):
    notification_message = State()


def is_admin(message: Message):
    return message.from_user.id in [5552984613, 760337093]


@dp.message(Command(commands=["notificate"]), StateFilter(default_state))
async def admin_notification(message: Message, state: FSMContext):
    if is_admin(message):
        await message.answer("Привет, админ!\n Что надо разослать?")
        await state.set_state(FSMwaitnotification.notification_message)
    else:
        await message.answer("Вы кто такой? Я вас не знаю!")


@dp.message(StateFilter(FSMwaitnotification.notification_message))
async def notificate_message(message: Message, state: FSMContext):
    try:
        with open("users.csv", encoding="utf-8") as file:
            users = DictReader(file)
            for user in users:
                await message.send_copy(chat_id=user["chat_id"])
    except TypeError:
        await message.reply(text="Не могу это переотправить")
    # except: 
    #     await message.reply(text="Что-то не так")
    await state.clear()


@dp.message(Command(commands=["start"]), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        f"Привет!\nХотите получать уведомления о начале вебор Максима? Если да, то напишите комманду /activate"
    )


@dp.message(Command(commands=["help"]), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(
        "Данный бот необходим для автоматического уведомления о начале веба или рассылке файлов\n/activate для подписка\n/deactivate для отмены подписки"
    )


@dp.message(Command(commands=["activate"]), StateFilter(default_state))
async def process_activate_command(message: Message):
    user_id = str(message.from_user.id)  # Преобразуем user_id в строку
    is_subscribed = False
    
    # Читаем CSV файл и проверяем наличие user_id
    with open("users.csv", newline='') as file:
        Reader = DictReader(file)
        for row in Reader:
            if row["user_id"] == user_id:
                is_subscribed = True
                break

    if is_subscribed:
        await message.answer("Вы уже подписаны!")
    else:
        # Добавляем новую запись в CSV файл
        with open("users.csv", 'a', newline='') as csvfile:
            Writer = writer(csvfile)
            Writer.writerow([message.from_user.id, message.chat.id])
        await message.answer("Вы подписались на рассылку!")


@dp.message(Command(commands=["deactivate"]), StateFilter(default_state))
async def process_deactivate_command(message: Message):
    user_id = str(message.from_user.id)  # Преобразуем user_id в строку
    
    # Проверяем, подписан ли пользователь
    with open("users.csv", newline='') as file:
        if user_id not in {row["user_id"] for row in DictReader(file)}:
            await message.answer("Вы и не подписаны...")
            return
    
    # Читаем CSV файл и удаляем пользователя
    with open("users.csv", 'r', newline='') as csvfile:
        reader = DictReader(csvfile)
        rows = [row for row in reader if row['user_id'] != user_id]

    # Записываем обновленный список пользователей обратно в CSV файл
    with open("users.csv", 'w', newline='') as csvfile:
        fieldnames = reader.fieldnames
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    await message.answer("Вы отписались от рассылки(")


if __name__ == "__main__":
    dp.run_polling(bot)
