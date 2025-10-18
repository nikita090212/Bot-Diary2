import json
import threading
import time
from datetime import datetime

DATA_FILE = "reminders.json"
CHECK_INTERVAL = 60  # секунд между проверками


def load_tasks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def add_task(user_id, text, remind_time_str):
    tasks = load_tasks()
    user_tasks = tasks.get(str(user_id), [])
    user_tasks.append({"text": text, "time": remind_time_str})
    tasks[str(user_id)] = user_tasks
    save_tasks(tasks)


def get_user_tasks(user_id):
    tasks = load_tasks()
    return tasks.get(str(user_id), [])


def remove_due_tasks():
    """Удаляет задачи, время которых прошло"""
    tasks = load_tasks()
    now = datetime.now()
    changed = False

    for user_id in list(tasks.keys()):
        user_tasks = tasks[user_id]
        new_tasks = []
        for task in user_tasks:
            task_time = datetime.fromisoformat(task["time"])
            if task_time > now:
                new_tasks.append(task)
            else:
                changed = True
        tasks[user_id] = new_tasks

    if changed:
        save_tasks(tasks)


def start_reminder_loop(bot):
    def loop():
        while True:
            tasks = load_tasks()
            now = datetime.now()

            for user_id, user_tasks in tasks.items():
                for task in user_tasks:
                    task_time = datetime.fromisoformat(task["time"])
                    if 0 <= (task_time - now).total_seconds() < CHECK_INTERVAL:
                        try:
                            bot.send_message(user_id, f"🔔 Напоминание: {task['text']}")
                        except Exception as e:
                            print(f"Ошибка при отправке: {e}")
            remove_due_tasks()
            time.sleep(CHECK_INTERVAL)

    threading.Thread(target=loop, daemon=True).start()
