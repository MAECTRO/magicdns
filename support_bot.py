#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Двусторонний Telegram-бот техподдержки MagicDNS.
- Любой пользователь пишет в @magicdns_alert_bot -> сообщение пересылается админу (chat_id: 8010010144).
- Админ делает 'Reply' (Ответить) в Telegram -> бот отправляет ответ пользователю от имени бота.
- Личный контакт админа скрыт.
"""

import os
import sys
import time
import re
import json
import urllib.request
import urllib.parse
import urllib.error

# Поддержка UTF-8 вывода в консоль Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Очищаем системные прокси, которые могут блокировать соединение
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
    os.environ.pop(k, None)

BOT_TOKEN = "8626072258:AAHtcqrf37R0iW3D83Ae7WzLjy2A9alr6Gw"
ADMIN_CHAT_ID = 8010010144
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WELCOME_TEXT = """👋 *Добро пожаловать в службу поддержки MagicDNS!*

Наш официальный сайт: [magicdns.ru](https://magicdns.ru)

Здесь вы можете:
• Задать вопрос по настройке (Windows, iOS, Android, Keenetic / роутеры)
• Сообщить о сбое или ошибке доступа к Gemini, ChatGPT, Claude
• Предложить идею по улучшению сервиса

Напишите ваш вопрос или описание проблемы прямо сюда, и администратор ответит вам в этом чате."""

def tg_request(method, data=None):
    url = f"{BASE_URL}/{method}"
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
        
    try:
        with opener.open(req, timeout=40) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def send_message(chat_id, text, parse_mode="Markdown", reply_to_message_id=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    return tg_request("sendMessage", data)

def main():
    print("=" * 60)
    print("[BOT] MagicDNS Support & Alert Bot запущен!")
    print(f"[BOT] Администратор ID: {ADMIN_CHAT_ID}")
    print("[BOT] Ожидание сообщений от пользователей...")
    print("=" * 60)

    # Проверка бота
    me = tg_request("getMe")
    if not me.get('ok'):
        print("[ERROR] Не удалось подключиться к Telegram API:", me)
        return
    bot_user = me['result']['username']
    print(f"[OK] Подключено к @{bot_user}")

    last_update_id = 0

    while True:
        try:
            updates = tg_request("getUpdates", {
                "offset": last_update_id + 1,
                "timeout": 25
            })

            if not updates.get('ok'):
                time.sleep(3)
                continue

            for update in updates.get('result', []):
                last_update_id = update['update_id']

                message = update.get('message')
                if not message:
                    continue

                from_user = message.get('from', {})
                sender_id = from_user.get('id')
                sender_name = from_user.get('first_name', '')
                if from_user.get('last_name'):
                    sender_name += f" {from_user.get('last_name')}"
                username = f"@{from_user.get('username')}" if from_user.get('username') else "без юзернейма"
                text = message.get('text', '')

                # 1. Если сообщение от обычного пользователя (НЕ админ)
                if sender_id != ADMIN_CHAT_ID:
                    # Приветствие на команду /start
                    if text == '/start':
                        send_message(sender_id, WELCOME_TEXT)
                        notify_admin = (
                            f"👤 *Новый пользователь запустил бота поддержки*\n"
                            f"Имя: {sender_name} ({username})\n"
                            f"ID: `[ID: {sender_id}]`"
                        )
                        send_message(ADMIN_CHAT_ID, notify_admin)
                        continue

                    # Пересылаем сообщение админу
                    admin_msg = (
                        f"📩 *Новый вопрос от пользователя!*\n\n"
                        f"👤 *От:* {sender_name} ({username})\n"
                        f"🆔 `[ID: {sender_id}]`\n\n"
                        f"💬 *Сообщение:*\n{text}\n\n"
                        f"👉 _Чтобы ответить, сделайте Reply (Ответить) на это сообщение._"
                    )
                    send_message(ADMIN_CHAT_ID, admin_msg)
                    send_message(sender_id, "✓ Ваше сообщение передано администратору. Скоро вам ответят прямо здесь!")

                # 2. Если сообщение от АДМИНА
                else:
                    reply_to = message.get('reply_to_message')
                    if reply_to and reply_to.get('text'):
                        reply_text = reply_to.get('text')
                        # Ищем ID пользователя в цитируемом сообщении
                        id_match = re.search(r'\[ID:\s*(\d+)\]', reply_text)
                        if id_match:
                            target_user_id = int(id_match.group(1))
                            user_reply = f"💬 *Ответ от поддержки MagicDNS:*\n\n{text}"
                            res = send_message(target_user_id, user_reply)
                            if res.get('ok'):
                                send_message(ADMIN_CHAT_ID, f"✓ Ответ успешно доставлен пользователю [ID: {target_user_id}]!", reply_to_message_id=message['message_id'])
                            else:
                                send_message(ADMIN_CHAT_ID, f"⚠️ Не удалось доставить ответ: {res.get('error', 'ошибка')}", reply_to_message_id=message['message_id'])

        except Exception as e:
            print(f"[WARN] Ошибка в цикле: {e}")
            time.sleep(3)

if __name__ == '__main__':
    main()
