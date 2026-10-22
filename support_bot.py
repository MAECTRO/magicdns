"""
MagicDNS 24/7 Cloud Support, Relay & 1-Tap Review Moderation Bot
Runs as systemd service on Finland Host (2.56.179.170).

Features:
1. HTTP API on 127.0.0.1:8880 for https://dns.magicdns.ru/api/feedback
   - Client sends feedback/reviews here directly (NO tokens exposed in browser!).
   - Works in Russia without VPN (since dns.magicdns.ru is not blocked!).
2. 1-Tap Review Publishing via Telegram inline keyboard directly to GitHub repo.
3. Two-way live technical support chat with 100% full media support (Photos, Screenshots, Documents, Voice, Video).
4. Universal /dns, /setup, /status, /donate, /help commands for private chats and groups.
5. Auto-registered Telegram menu commands (setMyCommands).
"""

import os
import re
import sys
import time
import json
import html
import base64
import threading
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = 8010010144
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "MAECTRO/magicdns"
DONATE_URL = "https://pay.cloudtips.ru/p/596a95a5"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

MONTHS_RU = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

def tg_request(method, data=None):
    url = f"{BASE_URL}/{method}"
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"[TG HTTP ERROR] {method} ({e.code}): {body}")
        if e.code == 409:
            print("[TG 409] Backing off 12s...")
            time.sleep(12)
        return {'ok': False, 'error': f"HTTP {e.code}: {body}"}
    except Exception as e:
        print(f"[TG ERROR] {method}: {e}")
        return {'ok': False, 'error': str(e)}

def answer_callback(cq_id, text, alert=False):
    return tg_request("answerCallbackQuery", {
        "callback_query_id": cq_id,
        "text": text,
        "show_alert": alert
    })

def edit_message(chat_id, message_id, text, parse_mode="HTML"):
    return tg_request("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode
    })

def send_message(chat_id, text, parse_mode="HTML", reply_to_message_id=None, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request("sendMessage", data)

def copy_message(chat_id, from_chat_id, message_id, caption=None, parse_mode="HTML", reply_to_message_id=None):
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    if caption is not None:
        data["caption"] = caption
        data["parse_mode"] = parse_mode
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    return tg_request("copyMessage", data)

def forward_message(chat_id, from_chat_id, message_id):
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return tg_request("forwardMessage", data)

def set_bot_commands():
    cmds = [
        {"command": "dns", "description": "⚡ Параметры и ссылки MagicDNS"},
        {"command": "status", "description": "🟢 Статус серверов сети"},
        {"command": "donate", "description": "☕ Поддержать серверы"},
        {"command": "help", "description": "💬 Помощь и связь с поддержкой"}
    ]
    try:
        res = tg_request("setMyCommands", {"commands": cmds})
        print(f"[BOT COMMANDS] Registered menu: {res.get('ok')}")
    except Exception as e:
        print(f"[BOT COMMANDS ERROR] {e}")

# Reusable Card and Keyboard Definitions
def get_dns_card():
    return (
        "⚡ <b>Параметры подключения MagicDNS:</b>\n\n"
        "• <b>Роутеры (Wi-Fi) и ПК:</b>\n"
        "  Основной IPv4: <code>109.120.132.43</code>\n"
        "  Запасной IPv4: <code>94.249.177.102</code>\n\n"
        "• <b>Android (Частный DNS-сервер):</b>\n"
        "  Имя хоста: <code>dns.magicdns.ru</code>\n\n"
        "• <b>iPhone / iPad / Mac:</b>\n"
        "  Прямая ссылка на профиль: <a href='https://magicdns.ru/profile.mobileconfig'>https://magicdns.ru/profile.mobileconfig</a>\n"
        "  <i>(нажмите кнопку внизу или ссылку, чтобы скачать и установить профиль в Настройках)</i>\n\n"
        "• <b>Windows 10/11 и браузеры (DoH):</b>\n"
        "  Шаблон DoH: <code>https://dns.magicdns.ru/dns-query</code>\n\n"
        "🌐 <b>Подробные инструкции с картинками:</b>\n"
        "<a href='https://magicdns.ru/#setup'>https://magicdns.ru/#setup</a>"
    )

def get_dns_kb():
    return {
        "inline_keyboard": [
            [{"text": "🍏 Скачать профиль для iOS / Mac", "url": "https://magicdns.ru/profile.mobileconfig"}],
            [{"text": "🌐 Инструкция на сайте", "url": "https://magicdns.ru/#setup"}],
            [{"text": "☕ Сказать спасибо проекту", "url": DONATE_URL}]
        ]
    }

def get_status_card():
    return (
        "🟢 <b>Статус инфраструктуры MagicDNS:</b>\n\n"
        "• 🇸🇪 Швеция (Core Node): 🟢 <code>109.120.132.43</code> (Штатно)\n"
        "• 🇫🇮 Финляндия (Primary / DoH): 🟢 <code>2.56.179.170</code> (Штатно)\n"
        "• 🇩🇪 Германия (Backup Node): 🟢 <code>94.249.177.102</code> (Штатно)\n\n"
        "🛡️ <i>Все узлы активны 24/7. Uptime 99.9%. Трафик маршрутизируется без задержек.</i>"
    )

def get_status_kb():
    return {
        "inline_keyboard": [
            [{"text": "⚡ Параметры подключения", "callback_data": "cmd_dns"}],
            [{"text": "☕ Поддержать серверы", "url": DONATE_URL}],
            [{"text": "🌐 Сайт magicdns.ru", "url": "https://magicdns.ru"}]
        ]
    }

def get_donate_card():
    return (
        "☕ <b>Поддержка серверов MagicDNS</b>\n\n"
        "MagicDNS — бесплатный независимый проект без рекламы и платных подписок.\n\n"
        "Все европейские узлы (Стокгольм, Хельсинки, Франкфурт) мы оплачиваем самостоятельно. Если сервис помогает вам в работе с нейросетями, коде или учебе — любая чашка кофе поможет проекту жить дальше и развиваться. Спасибо каждому! ❤️"
    )

def get_donate_kb():
    return {
        "inline_keyboard": [
            [{"text": "☕ Поддержать серверы (CloudTips)", "url": DONATE_URL}],
            [{"text": "🌐 Официальный сайт", "url": "https://magicdns.ru"}]
        ]
    }

def get_help_card():
    return (
        "👋 <b>Справка и быстрые команды MagicDNS:</b>\n\n"
        "• <code>/dns</code> — быстрые IP и ссылки для настройки всех устройств\n"
        "• <code>/status</code> — проверка работоспособности серверов\n"
        "• <code>/donate</code> — помочь с оплатой хостинга\n"
        "• 🌐 Сайт с подробными гайдами: <a href='https://magicdns.ru/#setup'>https://magicdns.ru/#setup</a>\n\n"
        "💬 <b>Нужна помощь?</b> Просто напишите свой вопрос или пришлите скриншот ошибки в этот чат — администратор ответит вам прямо здесь!"
    )

def get_help_kb():
    return {
        "inline_keyboard": [
            [{"text": "⚡ Настройки DNS", "callback_data": "cmd_dns"}],
            [{"text": "🌐 Инструкции на сайте", "url": "https://magicdns.ru/#setup"}],
            [{"text": "☕ Сказать спасибо", "url": DONATE_URL}]
        ]
    }

def get_welcome_card():
    return (
        "👋 <b>Добро пожаловать в MagicDNS!</b>\n\n"
        "Бесплатный Smart DNS для прямого доступа к нейросетям (ChatGPT, Claude, Gemini, Perplexity) без VPN на полной скорости вашего интернета.\n\n"
        "⚡ <b>Быстрые команды:</b>\n"
        "• <code>/dns</code> — получить адреса и ссылки для настройки\n"
        "• <code>/status</code> — статус работы серверов\n"
        "• <code>/donate</code> — поддержать проект\n\n"
        "💬 Если вам нужна помощь с подключением — просто опишите проблему или пришлите скриншот сюда, мы поможем настроить!"
    )

def get_welcome_kb():
    return {
        "inline_keyboard": [
            [{"text": "⚡ Получить настройки DNS", "callback_data": "cmd_dns"}],
            [{"text": "🌐 Инструкция на сайте", "url": "https://magicdns.ru/#setup"}],
            [{"text": "☕ Сказать спасибо", "url": DONATE_URL}]
        ]
    }

def publish_review_to_github(author, platform, rating, message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/reviews.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "MagicDNS-Finland-VPS-Bot",
        "Accept": "application/vnd.github.v3+json"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            sha = data['sha']
            content_bytes = base64.b64decode(data['content'])
            reviews = json.loads(content_bytes.decode('utf-8'))
    except Exception as e:
        return False, f"Ошибка загрузки reviews.json: {e}"

    now = datetime.now()
    formatted_date = f"{now.day} {MONTHS_RU.get(now.month, 'января')} {now.year}"

    new_review = {
        "id": int(time.time() * 1000),
        "author": author,
        "platform": platform,
        "rating": rating,
        "date": formatted_date,
        "message": message
    }

    reviews.insert(0, new_review)

    new_content_str = json.dumps(reviews, ensure_ascii=False, indent=2)
    new_content_b64 = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')

    update_payload = {
        "message": f"Add review from {author} ({rating}★ via TG 1-Tap)",
        "content": new_content_b64,
        "sha": sha
    }

    req_put = urllib.request.Request(
        url,
        data=json.dumps(update_payload).encode('utf-8'),
        headers=headers,
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req_put, timeout=15) as resp:
            return True, "Отзыв успешно опубликован на GitHub!"
    except Exception as e:
        return False, f"Ошибка сохранения на GitHub: {e}"

def parse_review_message(text):
    author = "Пользователь"
    platform = "Не указана"
    rating = 5
    review_text = ""

    lines = text.split('\n')
    for line in lines:
        if line.startswith("👤 Автор:"):
            author = line.replace("👤 Автор:", "").strip()
        elif line.startswith("💻 Платформа:"):
            platform = line.replace("💻 Платформа:", "").strip()
        elif line.startswith("⭐️ Оценка:"):
            match = re.search(r'\((\d)/5\)', line)
            if match:
                rating = int(match.group(1))

    if "💬 Текст отзыва:" in text:
        parts = text.split("💬 Текст отзыва:")
        if len(parts) > 1:
            raw_text = parts[1]
            if "👉 Нажмите кнопку ниже" in raw_text:
                raw_text = raw_text.split("👉 Нажмите кнопку ниже")[0]
            review_text = raw_text.strip()

    return author, platform, rating, review_text

class FeedbackAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/feedback':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8', errors='ignore')

            try:
                data = json.loads(body)
                author = data.get('name', 'Аноним').strip() or 'Аноним'
                review_type = data.get('type', 'review')
                platform = data.get('platform', 'Не указана')
                rating = int(data.get('rating', 5))
                message = data.get('message', '').strip()

                if not message:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'Пустое сообщение'}).encode('utf-8'))
                    return

                stars_str = '★' * rating
                esc_author = html.escape(str(author))
                esc_platform = html.escape(str(platform))
                esc_message = html.escape(str(message))

                if review_type == 'suggestion':
                    tg_msg = (
                        f"💡 <b>НОВОЕ ПРЕДЛОЖЕНИЕ / ИДЕЯ ДЛЯ MAGICDNS!</b>\n\n"
                        f"👤 <b>От:</b> {esc_author}\n"
                        f"💻 <b>Платформа:</b> {esc_platform}\n\n"
                        f"💬 <b>Текст идеи:</b>\n{esc_message}"
                    )
                    send_message(ADMIN_CHAT_ID, tg_msg)
                else:
                    tg_msg = (
                        f"🌟 <b>НОВЫЙ ОТЗЫВ С САЙТА MAGICDNS!</b>\n\n"
                        f"👤 <b>Автор:</b> {esc_author}\n"
                        f"💻 <b>Платформа:</b> {esc_platform}\n"
                        f"⭐️ <b>Оценка:</b> {stars_str} ({rating}/5)\n\n"
                        f"💬 <b>Текст отзыва:</b>\n{esc_message}\n\n"
                        f"👉 <i>Нажмите кнопку ниже для публикации или отклонения:</i>"
                    )

                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "✅ Опубликовать на сайте", "callback_data": "pub_review"},
                                {"text": "❌ Отклонить", "callback_data": "del_review"}
                            ]
                        ]
                    }
                    send_message(ADMIN_CHAT_ID, tg_msg, reply_markup=keyboard)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'success': True}).encode('utf-8'))
                print(f"[HTTP FEEDBACK] Processed {review_type} from {author}: True")
            except Exception as e:
                print(f"[HTTP ERROR] {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def start_http_server():
    server = HTTPServer(('127.0.0.1', 8880), FeedbackAPIHandler)
    print("[HTTP SERVER] Listening on http://127.0.0.1:8880/api/feedback")
    server.serve_forever()

def main():
    print("="*60)
    print(" MagicDNS 24/7 Support & 1-Tap Moderator Bot Started ")
    print("="*60)

    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    set_bot_commands()

    last_offset = 0

    while True:
        try:
            params = {"timeout": 25}
            if last_offset > 0:
                params["offset"] = last_offset + 1

            updates = tg_request("getUpdates", params)

            if not updates.get('ok'):
                time.sleep(3)
                continue

            for u in updates.get('result', []):
                last_offset = u['update_id']

                # 1. Handle Inline Button Clicks
                if 'callback_query' in u:
                    cq = u['callback_query']
                    cq_id = cq['id']
                    from_id = cq.get('from', {}).get('id')
                    data = cq.get('data', '')
                    msg = cq.get('message', {})
                    msg_id = msg.get('message_id')
                    msg_text = msg.get('text', '')

                    print(f"[CALLBACK] {data} from user {from_id}")

                    # Public callback queries
                    if data == 'cmd_dns':
                        answer_callback(cq_id, "⚡ Параметры MagicDNS")
                        send_message(from_id, get_dns_card(), reply_markup=get_dns_kb())
                        continue

                    if data == 'cmd_status':
                        answer_callback(cq_id, "🟢 Статус серверов")
                        send_message(from_id, get_status_card(), reply_markup=get_status_kb())
                        continue

                    # Admin-only callbacks
                    if from_id != ADMIN_CHAT_ID:
                        answer_callback(cq_id, "⛔ Действие только для администратора", alert=True)
                        continue

                    if data == 'del_review':
                        answer_callback(cq_id, "🗑️ Отзыв отклонён")
                        edit_message(ADMIN_CHAT_ID, msg_id, msg_text + "\n\n❌ <i>Отзыв отклонён и отправлен в корзину.</i>")
                        continue

                    if data == 'pub_review':
                        answer_callback(cq_id, "⏳ Публикую отзыв на сайт...")
                        author, platform, rating, review_text = parse_review_message(msg_text)
                        print(f"[PUB] Author: {author}, Platform: {platform}, Rating: {rating}, Text: {review_text[:40]}...")

                        try:
                            ok, status_msg = publish_review_to_github(author, platform, rating, review_text)
                            if ok:
                                stars_str = '★' * rating
                                esc_author = html.escape(str(author))
                                esc_platform = html.escape(str(platform))
                                esc_text = html.escape(str(review_text))
                                updated_text = (
                                    f"✅ <b>ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\n\n"
                                    f"👤 <b>Автор:</b> {esc_author}\n"
                                    f"💻 <b>Платформа:</b> {esc_platform}\n"
                                    f"⭐️ <b>Оценка:</b> {stars_str} ({rating}/5)\n\n"
                                    f"💬 <b>Текст:</b>\n{esc_text}\n\n"
                                    f"🌐 <i>Отзыв уже залит в reviews.json и доступен на сайте!</i>"
                                )
                                edit_message(ADMIN_CHAT_ID, msg_id, updated_text)
                                answer_callback(cq_id, "🎉 Успешно! Отзыв опубликован на сайте!")
                                print(f"[PUB SUCCESS] Review by {author} published to reviews.json!")
                            else:
                                answer_callback(cq_id, f"⚠️ Ошибка: {status_msg}", alert=True)
                                print(f"[PUB FAIL] {status_msg}")
                        except Exception as e:
                            print(f"[GITHUB ERROR] {e}")
                            answer_callback(cq_id, f"⚠️ Ошибка при публикации: {e}", alert=True)
                        continue

                # 2. Handle Messages (Group & Private)
                if 'message' in u:
                    m = u['message']
                    chat = m.get('chat', {})
                    chat_id = chat.get('id')
                    chat_type = chat.get('type', 'private')
                    sender = m.get('from', {})
                    sender_id = sender.get('id')
                    sender_name = sender.get('first_name', '')
                    username = f"@{sender.get('username')}" if sender.get('username') else "без юзернейма"
                    text = m.get('text', '') or m.get('caption', '') or ''

                    # Detect media attachments
                    is_photo = bool(m.get('photo'))
                    is_doc = bool(m.get('document'))
                    is_video = bool(m.get('video'))
                    is_voice = bool(m.get('voice'))
                    is_video_note = bool(m.get('video_note'))
                    is_audio = bool(m.get('audio'))
                    is_sticker = bool(m.get('sticker'))
                    has_media = is_photo or is_doc or is_video or is_voice or is_video_note or is_audio or is_sticker

                    # Check commands FIRST (Universal for Private & Groups, Users & Admin)
                    cmd = text.strip().split()[0].lower() if text.strip() else ""
                    cmd = cmd.split('@')[0]  # strip @botname

                    if cmd in ['/dns', '/setup', '/config', 'днс', 'настройка']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_dns_card(), reply_to_message_id=reply_to_id, reply_markup=get_dns_kb())
                        continue

                    elif cmd in ['/status', 'статус']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_status_card(), reply_to_message_id=reply_to_id, reply_markup=get_status_kb())
                        continue

                    elif cmd in ['/donate', '/support', '/tip', 'донат']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_donate_card(), reply_to_message_id=reply_to_id, reply_markup=get_donate_kb())
                        continue

                    elif cmd in ['/rules', '/help', 'помощь', 'правила']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_help_card(), reply_to_message_id=reply_to_id, reply_markup=get_help_kb())
                        continue

                    elif cmd == '/start':
                        send_message(chat_id, get_welcome_card(), reply_markup=get_welcome_kb())
                        if chat_type == 'private' and sender_id != ADMIN_CHAT_ID:
                            notify = f"👤 Новый пользователь в боте поддержки:\n<b>{sender_name}</b> ({username})\nID: <code>[ID: {sender_id}]</code>"
                            send_message(ADMIN_CHAT_ID, notify)
                        continue

                    # --- A. GROUP / SUPERGROUP NON-COMMAND HANDLING ---
                    if chat_type in ['group', 'supergroup']:
                        # 1. New members joined
                        new_members = m.get('new_chat_members', [])
                        if new_members:
                            for nm in new_members:
                                if nm.get('username') == 'magicdns_alert_bot':
                                    hello_bot = (
                                        "👋 <b>Всем привет! Я официальный бот MagicDNS.</b>\n\n"
                                        "🛡️ Защищаю чат от спама и помогаю с быстрой настройкой.\n\n"
                                        "⚡ <b>Команды в чате:</b>\n"
                                        "• <code>/dns</code> — быстрые IP и ссылки для настройки\n"
                                        "• <code>/status</code> — статус серверов и узлов сети\n"
                                        "• <code>/help</code> — справка и правила\n\n"
                                        "🌐 <i>Официальный сайт: <a href='https://magicdns.ru'>magicdns.ru</a></i>"
                                    )
                                    send_message(chat_id, hello_bot)
                            continue

                        # 2. Aggressive Anti-spam Filter
                        spam_triggers = [
                            'казино', 'casino', '1win', 'вулкан', 'ставки на спорт',
                            'заработок от', 'пассивный доход от', 'криптосигнал',
                            'подпишись на канал t.me', 'слив 18+', 'интим фото',
                            'договорные матчи', 'лёгкие деньги', 'переходи по ссылке t.me'
                        ]
                        msg_lower = text.lower()
                        if any(trigger in msg_lower for trigger in spam_triggers):
                            tg_request("deleteMessage", {"chat_id": chat_id, "message_id": m['message_id']})
                            notify = f"🛡️ <b>Удален спам в группе:</b>\nОт: {sender_name} ({username})\nТекст: {html.escape(text[:200])}"
                            send_message(ADMIN_CHAT_ID, notify)
                            continue

                        # Other group chatter is ignored
                        continue

                    # --- B. PRIVATE CHAT HANDLING (Support & Admin Relay) ---
                    if sender_id != ADMIN_CHAT_ID:
                        # Forward user message and/or media to admin
                        media_label = ""
                        if is_photo:
                            media_label = " [📷 Скриншот/Фото]"
                        elif is_doc:
                            media_label = " [📁 Файл/Документ]"
                        elif is_video:
                            media_label = " [🎬 Видео]"
                        elif is_voice:
                            media_label = " [🎙️ Голосовое сообщение]"
                        elif is_video_note:
                            media_label = " [📹 Видеосообщение]"
                        elif is_sticker:
                            media_label = " [🎨 Стикер]"

                        esc_name = html.escape(str(sender_name))
                        esc_uname = html.escape(str(username))
                        esc_msg = html.escape(str(text)) if text else ""

                        admin_forward = (
                            f"📩 <b>Сообщение от пользователя{media_label}!</b>\n\n"
                            f"👤 <b>От:</b> {esc_name} ({esc_uname})\n"
                            f"🆔 <code>[ID: {sender_id}]</code>\n"
                        )
                        if esc_msg:
                            admin_forward += f"\n💬 <b>Текст:</b>\n{esc_msg}\n"
                        admin_forward += f"\n👉 <i>Сделайте 'Reply' (Ответить), чтобы написать пользователю.</i>"

                        info_res = send_message(ADMIN_CHAT_ID, admin_forward)
                        info_msg_id = info_res.get('result', {}).get('message_id') if info_res.get('ok') else None

                        # Deliver the media directly to admin
                        if has_media:
                            copy_res = copy_message(ADMIN_CHAT_ID, sender_id, m['message_id'], reply_to_message_id=info_msg_id)
                            if not copy_res.get('ok'):
                                forward_message(ADMIN_CHAT_ID, sender_id, m['message_id'])

                        send_message(sender_id, "✓ Сообщение передано администратору. Скоро ответим прямо здесь!")
                    else:
                        # Admin reply to user
                        reply_to = m.get('reply_to_message')
                        if reply_to:
                            target_id = None
                            
                            # Check text or caption of the replied message
                            rep_text = (reply_to.get('text') or '') + " " + (reply_to.get('caption') or '')
                            id_match = re.search(r'\[ID:\s*(\d+)\]', rep_text)
                            if id_match:
                                target_id = int(id_match.group(1))
                            else:
                                # Check if replied to media that was attached to the info card
                                parent = reply_to.get('reply_to_message')
                                if parent:
                                    parent_text = (parent.get('text') or '') + " " + (parent.get('caption') or '')
                                    id_match_p = re.search(r'\[ID:\s*(\d+)\]', parent_text)
                                    if id_match_p:
                                        target_id = int(id_match_p.group(1))

                            if not target_id and reply_to.get('forward_from'):
                                target_id = reply_to['forward_from'].get('id')

                            if target_id:
                                # Check if admin sent media or text
                                has_admin_media = bool(m.get('photo') or m.get('document') or m.get('video') or m.get('voice'))
                                if has_admin_media:
                                    caption = "💬 <b>Поддержка MagicDNS:</b>"
                                    if text:
                                        caption += f"\n\n{html.escape(str(text))}"
                                    resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'], caption=caption, parse_mode="HTML")
                                    if not resp.get('ok'):
                                        send_message(target_id, "💬 <b>Поддержка MagicDNS:</b>")
                                        resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'])
                                else:
                                    esc_rep = html.escape(str(text))
                                    resp = send_message(target_id, f"💬 <b>Поддержка MagicDNS:</b>\n\n{esc_rep}")

                                if resp.get('ok'):
                                    send_message(ADMIN_CHAT_ID, f"✓ Доставлено пользователю [ID: {target_id}]", reply_to_message_id=m['message_id'])
                                else:
                                    send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка отправки: {resp.get('error', 'неизвестная ошибка')}", reply_to_message_id=m['message_id'])

        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(3)

if __name__ == '__main__':
    main()
