# Devman Review Telegram Bot

**Описание**  
Этот проект — Telegram-бот для уведомления о проверках работ на платформе [Devman](https://dvmn.org) через Long Polling API.  
Бот отправляет уведомления в Telegram о проверке работ.

---

## **Функционал**
- Слушает новые проверки работ через Devman Long Polling API.
- Отправляет уведомления в Telegram о результатах проверки:
  - Работа принята.
  - Работа не принята (с указанием ошибок).
- Обрабатывает таймауты и потерю соединения.
- Работает в вечном цикле, автоматически продолжает работу после ошибок.

---

## **Установка**
## Установка
1. Клонируй репозиторий: `git clone git@github.com:Evst404/send_mail_check_work.git`
2. Создай venv: `python3 -m venv venv`
3. Активируй: `source venv/bin/activate`
4. Установи зависимости: `pip install -r requirements.txt`
5. Настрой .env с DVMN_TOKEN, TELEGRAM_TOKEN, CHAT_ID
6. Запусти: `python bot.py`

## Systemd
1. Создай /etc/systemd/system/send-mail-bot.service (см. код выше)
2. `systemctl daemon-reload`
3. `systemctl enable send-mail-bot.service`
4. `systemctl start send-mail-bot.service`

После запуска бот будет слушать новые проверки и отправлять уведомления в Telegram.
