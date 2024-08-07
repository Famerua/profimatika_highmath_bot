from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from csv import DictReader, DictWriter, writer
import aiogram.exceptions
import datetime
from config import BOT_TOKEN


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

NOTIFICATION_MESSAGE: Message


class FSMwaitnotification(StatesGroup):
    notification_message = State()
    add_ref_question = State()
    take_ans_ref_question = State()
    take_count_ref = State()
    wait_1_ref = State()
    wait_2_ref = State()


def is_admin(message: Message):
    return message.from_user.id in [5552984613, 760337093]


@dp.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    if is_admin(message):
        await message.answer(
            text="Рассылка отменена", reply_markup=ReplyKeyboardRemove()
        )
        # Сбрасываем состояние и очищаем данные, полученные внутри состояний
        await state.clear()
    else:
        await message.answer("Вы кто такой? Я вас не знаю!")


# admin
@dp.message(Command(commands=["notificate"]), StateFilter(default_state))
async def admin_notification(message: Message, state: FSMContext):
    if is_admin(message):
        await message.answer("Привет, админ!\n Что надо разослать?")
        await state.set_state(FSMwaitnotification.add_ref_question)
    else:
        await message.answer("Вы кто такой? Я вас не знаю!")


# admin
@dp.message(StateFilter(FSMwaitnotification.add_ref_question))
async def ask_about_ref(message: Message, state: FSMContext):
    print("Бот в состоянии (Получил сообщение. Задал вопрос о ссылке)")

    global NOTIFICATION_MESSAGE
    NOTIFICATION_MESSAGE = message

    button_add_ref_yes = KeyboardButton(text="Да")
    button_add_ref_no = KeyboardButton(text="Нет")
    keyboard_add_ref = ReplyKeyboardMarkup(
        keyboard=[[button_add_ref_yes, button_add_ref_no]], resize_keyboard=True
    )

    await message.answer("Добавить ссылку?", reply_markup=keyboard_add_ref)
    await state.set_state(FSMwaitnotification.take_ans_ref_question)


async def sending_message(message: Message, keyboard=None):
    print("Бот рассылает")
    try:
        with open("/data/users.csv", encoding="utf-8") as file:
            users = DictReader(file)
            with open(
                "/data/sent_messages.csv", "a", newline="", encoding="utf-8"
            ) as sent_file:
                fieldnames = ["chat_id", "message_id", "timestamp"]
                writer = DictWriter(sent_file, fieldnames=fieldnames)
                for user in users:
                    try:
                        if keyboard is None:
                            sent_message = await message.send_copy(
                                chat_id=user["chat_id"], parse_mode='HTML'
                            )
                        else:
                            sent_message = await message.send_copy(
                                chat_id=user["chat_id"], reply_markup=keyboard, parse_mode='HTML'
                            )

                        # Сохраняем chat_id, message_id и время отправки
                        writer.writerow(
                            {
                                "chat_id": user["chat_id"],
                                "message_id": sent_message.message_id,
                                "timestamp": datetime.datetime.now().isoformat(),
                            }
                        )
                    except aiogram.exceptions.TelegramBadRequest as e:
                        # Логируем ошибку и продолжаем с другим пользователем
                        print(
                            f"Ошибка при отправке сообщения в чат {user['chat_id']}, @{user['username']}: {e}"
                        )
                    except aiogram.exceptions.TelegramForbiddenError as e:
                        # Логируем ошибку и продолжаем с другим пользователем
                        print(f"Нет доступа к чату {user['chat_id']}: {e}")
                    except Exception as e:
                        # Логируем любую другую ошибку и продолжаем с другим пользователем
                        print(
                            f"Неизвестная ошибка при отправке сообщения в чат {user['chat_id']}, @{user['username']}: {e}"
                        )
                print("Бот разослал")
    except TypeError:
        await message.reply(text="Не могу это переотправить")
    except Exception as e:
        await message.reply(text=f"Что-то пошло не так: {e}")


# admin
@dp.message(StateFilter(FSMwaitnotification.take_ans_ref_question))
async def take_ans_ref_question(message: Message, state: FSMContext):
    print('Бот получил ответ насчет количества ссылок')
    if message.text == "Да":
        button_1_ref = KeyboardButton(text="1")
        button_2_ref = KeyboardButton(text="2")
        keyboard_count_ref = ReplyKeyboardMarkup(
            keyboard=[[button_1_ref, button_2_ref]], resize_keyboard=True
        )
        print('Бот спрашивает количество ссылок')
        await message.answer(text='Сколько ссылок добавить?', reply_markup=keyboard_count_ref)
        
        # print("Бот в состоянии (Получаю ссылку)")
        # await message.answer(
        #     "Жду от вас название ссылки и саму ссылку в таком формате",
        #     reply_markup=ReplyKeyboardRemove(),
        # )
        # await message.answer("Название ссылки\n\nСсылка")
        await state.set_state(FSMwaitnotification.take_count_ref)
    elif message.text == "Нет":
        await message.answer(
            "Хорошо. Рассылаю сообщение!", reply_markup=ReplyKeyboardRemove()
        )
        # await state.set_state(FSMwaitnotification.ask_about_button)
        await sending_message(NOTIFICATION_MESSAGE)
        await state.clear()

# admin
# @dp.message(StateFilter(FSMwaitnotification.ask_count_of_ref))
# async def ask_count_of_refs(message: Message, state: FSMContext):
#     await state.set_state(FSMwaitnotification.take_count_ref)

#admin
@dp.message(StateFilter(FSMwaitnotification.take_count_ref))
async def take_count_refs(message: Message, state: FSMContext):
    if message.text == '1':
        await message.answer(
            "Жду от вас название ссылки и саму ссылку в таком формате",
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer("Название ссылки\n\nСсылка")
        await state.set_state(FSMwaitnotification.wait_1_ref)

    elif message.text == '2':
        await message.answer(
            "Жду от вас названия ссылок и сами ссылки в таком формате",
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer("Название первой ссылки\n\nПервая сылка\n\nНазвание второй ссылки\n\nВторая ссылка")
        await state.set_state(FSMwaitnotification.wait_2_ref)


@dp.message(StateFilter(FSMwaitnotification.wait_1_ref))
async def take_ref(message: Message, state: FSMContext):
    url = message.text.split("\n\n")
    if len(url) == 2:
        print("Бот в состояннии (Получил ссылку)")
        url_inline_button = InlineKeyboardButton(text=url[0], url=url[1])
        keyboard_ref = InlineKeyboardMarkup(inline_keyboard=[[url_inline_button]])
        await message.answer("Принял! Начинаю рассылку с ссылкой")
        await sending_message(NOTIFICATION_MESSAGE, keyboard_ref)
        await state.clear()
    else:
        await message.answer(
            "Некорректный формат. Введите /cancel, чтобы начать рассылку заново"
        )

@dp.message(StateFilter(FSMwaitnotification.wait_2_ref))
async def take_ref(message: Message, state: FSMContext):
    url = message.text.split("\n\n")
    if len(url) == 4:
        print("Бот в состояннии (Получил ссылки)")
        url_inline_1_button = InlineKeyboardButton(text=url[0], url=url[1])
        url_inline_2_button = InlineKeyboardButton(text=url[2], url=url[3])
        keyboard_refs = InlineKeyboardMarkup(inline_keyboard=[[url_inline_1_button, url_inline_2_button]])
        await message.answer("Принял! Начинаю рассылку с ссылкой")
        await sending_message(NOTIFICATION_MESSAGE, keyboard_refs)
        await state.clear()
    else:
        await message.answer(
            "Некорректный формат. Введите /cancel, чтобы начать рассылку заново"
        )


@dp.message(Command(commands=["stats"]), is_admin, StateFilter(default_state))
async def get_stats(message: Message):
    with open("/data/users.csv") as file:
        Users = DictReader(file)
        readers = [f"@{user['username']}" for user in Users]
    await message.answer(f"Активные читатели {len(readers)}:\n{"\n".join(readers)}")


@dp.message(Command(commands=["start"]), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        f"""<b>Приветствую!</b> 

<em>Данный бот будет уведомлять тебя о выходе новых видео на канале Макса, также ты одним из первых будешь получать актуальную информацию об онлайн трансляциях и вебинарах с курсов по <b>Высшей Математике</b> и узнавать о самых приятных ценах на грядущие курсы)</em>

<b>Если ты согласен, то напиши команду /activate</b>""",
        parse_mode="HTML",
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
    with open("/data/users.csv", newline="") as file:
        Reader = DictReader(file)
        for row in Reader:
            if row["user_id"] == user_id:
                is_subscribed = True
                break

    if is_subscribed:
        await message.answer("Вы уже подписаны!")
    else:
        # Добавляем новую запись в CSV файл
        with open("/data/users.csv", "a", newline="") as csvfile:
            Writer = writer(csvfile)
            Writer.writerow(
                [
                    message.from_user.id,
                    message.chat.id,
                    message.from_user.username,
                ]
            )
        await message.answer("Вы подписались на рассылку!")


@dp.message(Command(commands=["deactivate"]), StateFilter(default_state))
async def process_deactivate_command(message: Message):
    user_id = str(message.from_user.id)  # Преобразуем user_id в строку

    # Проверяем, подписан ли пользователь
    with open("/data/users.csv", newline="") as file:
        if user_id not in {row["user_id"] for row in DictReader(file)}:
            await message.answer("Вы и не подписаны...")
            return

    # Читаем CSV файл и удаляем пользователя
    with open("/data/users.csv", "r", newline="") as csvfile:
        reader = DictReader(csvfile)
        rows = [row for row in reader if row["user_id"] != user_id]

    # Записываем обновленный список пользователей обратно в CSV файл
    with open("/data/users.csv", "w", newline="") as csvfile:
        fieldnames = reader.fieldnames
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    await message.answer("Вы отписались от рассылки(")


if __name__ == "__main__":
    dp.run_polling(bot)
