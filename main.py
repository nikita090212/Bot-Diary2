import telebot
from datetime import datetime
from logic import add_task, get_user_tasks, start_reminder_loop
from config import*


bot = telebot.TeleBot(config.py)
start_reminder_loop(bot)  # Запускаем фоновую проверку напоминаний


@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой бот-ежедневник.\n\n"
        "Чтобы добавить задачу, отправь сообщение в формате:\n"
        "`Текст задачи ; ДД.ММ.ГГГГ ЧЧ:ММ`\n\n"
        "Пример:\n"
        "`Позвонить другу ; 20.10.2025 18:00`\n\n"
        "Команда /list — посмотреть задачи.",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["list"])
def list_handler(message):
    tasks = get_user_tasks(message.from_user.id)
    if not tasks:
        bot.send_message(message.chat.id, "У тебя пока нет задач 📭")
        return

    text = "🗓 Твои задачи:\n"
    for task in tasks:
        dt = datetime.fromisoformat(task["time"]).strftime("%d.%m.%Y %H:%M")
        text += f"• {task['text']} — {dt}\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: ";" in message.text)
def add_task_handler(message):
    try:
        task_text, time_str = map(str.strip, message.text.split(";", 1))
        remind_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
        add_task(message.from_user.id, task_text, remind_time.isoformat())
        bot.send_message(message.chat.id, f"✅ Задача добавлена: {task_text} на {remind_time.strftime('%d.%m.%Y %H:%M')}")
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Неверный формат. Пример:\nСходить в аптеку ; 20.10.2025 15:00")


bot.polling(none_stop=True)
