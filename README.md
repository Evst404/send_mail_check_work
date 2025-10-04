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

## Установка
1. Скачай проект:
```
git clone git@github.com:Evst404/send_mail_check_work.git
cd send_mail_check_work
```
2. Создай окружение:
```
python3 -m venv venv
```
3. Включи окружение:
- На Linux/macOS: `source venv/bin/activate`
- На Windows: `venv\Scripts\activate`
4. Установи нужные программы:
  ```
pip install -r requirements.txt
```
5. Создай файл `.env` и добавь:
```
DVMN_TOKEN=твой_токен_от_Devman
TELEGRAM_TOKEN=твой_токен_от_BotFather
TELEGRAM_CHAT_ID=твой_чат_ID
```
Узнай `TELEGRAM_CHAT_ID` с помощью бота `@userinfobot` после `/start`.
6. Запусти бота для теста:
```
python bot.py
```
## Настройка автозапуска (Systemd)
1. Создай файл:
```
sudo nano /etc/systemd/system/send-mail-bot.service
```
Напиши:
```
[Unit]
Description=Send Mail Check Work Bot
After=network.target
[Service]
User=root
WorkingDirectory=/opt/send_mail_check_work
Environment=PATH=/opt/send_mail_check_work/venv/bin
ExecStart=/opt/send_mail_check_work/venv/bin/python /opt/send_mail_check_work/bot.py
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
```
2. Сохрани и включи:
```
sudo systemctl daemon-reload
```
```
sudo systemctl enable send-mail-bot.service
```
```
sudo systemctl start send-mail-bot.service
```
3. Проверь работу:
`sudo systemctl status send-mail-bot.service`
## Сервер для проверки
```
- **IP**: 178.128.196.169
- **Пользователь**: root
- **Порт SSH**: 22
```

После запуска бот будет слушать новые проверки и отправлять уведомления в Telegram.
