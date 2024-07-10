import csv
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
import aiogram


with open("api.text") as f:
    API_TOKEN = f.read()

bot = Bot(token=API_TOKEN)

async def delete_messages(start_time: str, end_time: str):
    try:
        start_time_dt = datetime.fromisoformat(start_time)
        end_time_dt = datetime.fromisoformat(end_time)
        
        with open("sent_messages.csv", encoding="utf-8") as sent_file:
            sent_messages = list(csv.DictReader(sent_file))
        
        with open("sent_messages.csv", "w", newline='', encoding="utf-8") as sent_file:
            fieldnames = ["chat_id", "message_id", "timestamp"]
            writer = csv.DictWriter(sent_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in sent_messages:
                message_time_dt = datetime.fromisoformat(record["timestamp"])
                if start_time_dt <= message_time_dt <= end_time_dt:
                    chat_id = record["chat_id"]
                    message_id = record["message_id"]
                    try:
                        await bot.delete_message(chat_id=chat_id, message_id=message_id)
                        print(f"Сообщение {message_id} в чате {chat_id} удалено.")
                    except aiogram.exceptions.TelegramBadRequest as e:
                        print(f"Ошибка при удалении сообщения {message_id} в чате {chat_id}: {e}")
                    except aiogram.exceptions.TelegramForbidden as e:
                        print(f"Нет доступа для удаления сообщения {message_id} в чате {chat_id}: {e}")
                    except Exception as e:
                        print(f"Неизвестная ошибка при удалении сообщения {message_id} в чате {chat_id}: {e}")
                else:
                    writer.writerow(record)
                    
    except Exception as e:
        print(f"Что-то пошло не так: {e}")

if __name__ == "__main__":
    start_time = "2024-07-10T11:46:36.406737"  # Замените на нужное время начала
    end_time = "2024-07-10T11:46:39.406737"    # Замените на нужное время конца

    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_messages(start_time, end_time))
    loop.close()
