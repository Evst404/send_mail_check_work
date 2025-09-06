import os
import requests
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()
DVMN_TOKEN = os.getenv("DVMN_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

LONG_POLL_URL = "https://dvmn.org/api/long_polling/"
HEADERS = {"Authorization": f"Token {DVMN_TOKEN}"}

last_timestamp = None


def get_status():
    global last_timestamp
    params = {"timestamp": last_timestamp} if last_timestamp else {}
    try:
        response = requests.get(LONG_POLL_URL, headers=HEADERS, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "timeout":
            last_timestamp = data.get("timestamp_to_request")
            return []
        elif data.get("status") == "found":
            last_timestamp = data.get("last_attempt_timestamp")
            return data.get("new_attempts", [])
    except requests.exceptions.ReadTimeout:
        logging.info("Сервер Devman держит соединение. Новых проверок пока нет.")
        return []
    except Exception as e:
        logging.error("Ошибка при получении статуса: %s", e)
        return []


def start(update, context):
    attempts = get_status()
    if not attempts:
        update.message.reply_text("Пока нет новых проверок.")
        return

    messages = []
    for attempt in attempts:
        lesson = attempt.get("lesson_title")
        url = attempt.get("lesson_url")
        is_negative = attempt.get("is_negative", False)

        if is_negative:
            messages.append(f"{lesson}\n{url}\nРабота не принята.\n")
        else:
            messages.append(f"{lesson}\n{url}\nРабота принята!\n")

    update.message.reply_text("\n".join(messages))


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    logging.info("Бот запущен...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
