import os
import requests
import logging
import time
from functools import partial
from dotenv import load_dotenv
from telegram import Bot

LONG_POLL_URL = "https://dvmn.org/api/long_polling/"

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_status(headers, last_timestamp=None):
    params = {"timestamp": last_timestamp} if last_timestamp else {}
    try:
        logger.debug(f"Отправка запроса к {LONG_POLL_URL} с параметрами {params}")
        response = requests.get(LONG_POLL_URL, headers=headers, params=params, timeout=90)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Получен ответ от API: {data}")
        if data.get("status") == "timeout":
            return [], data.get("timestamp_to_request")
        elif data.get("status") == "found":
            return data.get("new_attempts", []), data.get("last_attempt_timestamp")
    except requests.exceptions.ReadTimeout:
        logger.warning("Таймаут при запросе к API")
        return [], last_timestamp
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Ошибка соединения с интернетом: {e}")
        time.sleep(10)
        return [], last_timestamp
    except Exception as e:
        logger.critical(f"Критическая ошибка при получении статуса: {e}")
        time.sleep(10)
        return [], last_timestamp

def send_attempts(bot, chat_id, attempts):
    for attempt in attempts:
        lesson = attempt.get("lesson_title")
        url = attempt.get("lesson_url")
        is_negative = attempt.get("is_negative", False)
        if is_negative:
            text = f"Работа не принята\n\n{lesson}\n{url}"
            logger.info(f"Отправлено уведомление: Работа не принята - {lesson}")
        else:
            text = f"Работа принята!\n\n{lesson}\n{url}"
            logger.info(f"Отправлено уведомление: Работа принята - {lesson}")
        bot.send_message(chat_id=chat_id, text=text)

def main():
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    headers = {"Authorization": f"Token {dvmn_token}"}
    bot = Bot(token=telegram_token)
    get_status_with_headers = partial(get_status, headers)
    last_timestamp = None
    logger.info("Бот запущен и ждёт проверки работ...")
    while True:
        try:
            attempts, last_timestamp = get_status_with_headers(last_timestamp)
            if attempts:
                send_attempts(bot, chat_id, attempts)
            1 / 0 
        except Exception as e:
            logger.critical(f"Необработанная ошибка в основном цикле: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
