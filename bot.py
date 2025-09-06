import os
import time
import json
import logging
import requests
from dotenv import load_dotenv
from telegram import Bot


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

LONG_POLL_URL = "https://dvmn.org/api/long_polling/"

def send_review_notification(bot: Bot, chat_id: int, lesson_title: str, lesson_url: str, is_negative: bool):
    """Отправка уведомления о проверке в Telegram"""
    message = (
        f"Работа не принята: {lesson_title}\n{lesson_url}\n\nИсправьте ошибки."
        if is_negative else
        f"Отлично! Работа принята: {lesson_title}\n{lesson_url}"
    )
    bot.send_message(chat_id=chat_id, text=message)
    logging.info("Отправлено уведомление по уроку: %s", lesson_title)

def process_poll_response(bot: Bot, chat_id: int, poll_response: dict):
    """Обработка ответа Long Polling API"""
    if poll_response.get("status") == "found":
        last_timestamp = poll_response["last_attempt_timestamp"]
        for review_attempt in poll_response["new_attempts"]:
            send_review_notification(
                bot,
                chat_id,
                review_attempt.get("lesson_title"),
                review_attempt.get("lesson_url"),
                review_attempt.get("is_negative", False)
            )
        return last_timestamp
    elif poll_response.get("status") == "timeout":
        return poll_response["timestamp_to_request"]
    return None

def listen_for_reviews(bot: Bot, chat_id: int, headers: dict):
    """Слушаем новые проверки через Long Polling API"""
    last_timestamp = None

    while True:
        params = {"timestamp": last_timestamp} if last_timestamp else {}
        try:
            response = requests.get(LONG_POLL_URL, headers=headers, params=params, timeout=20)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            logging.warning("Сервер не ответил вовремя, пробуем ещё раз...")
            continue
        except requests.exceptions.ConnectionError:
            logging.error("Нет интернета или сервер недоступен. Ждём 10 секунд...")
            time.sleep(10)
            continue
        except requests.exceptions.HTTPError as http_err:
            logging.error("Ошибка HTTP: %s", http_err)
            time.sleep(10)
            continue

        try:
            poll_response = response.json()
        except json.JSONDecodeError:
            logging.error("Ошибка разбора JSON от сервера. Пропускаем ответ.")
            continue

        last_timestamp = process_poll_response(bot, chat_id, poll_response) or last_timestamp
        time.sleep(1)

def main():
    load_dotenv()

    dvmn_token = os.getenv("DVMN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id_str = os.getenv("CHAT_ID")
    if not all([dvmn_token, telegram_token, chat_id_str]):
        logging.error("Не заданы переменные окружения: DVMN_TOKEN, TELEGRAM_TOKEN или CHAT_ID")
        return

    chat_id = int(chat_id_str)
    bot = Bot(token=telegram_token)
    headers = {"Authorization": f"Token {dvmn_token}"}

    logging.info("=== Запуск слушателя проверок Devman ===")
    listen_for_reviews(bot, chat_id, headers)

if __name__ == "__main__":
    main()
