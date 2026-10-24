"""
MagicDNS 24/7 Cloud Support, Relay & 1-Tap Review Moderation Bot
Runs as systemd service on Finland Host (2.56.179.170).

Features:
1. HTTP API on 127.0.0.1:8880 for https://dns.magicdns.ru/api/feedback
   - Client sends feedback/reviews here directly (NO tokens exposed in browser!).
   - Works directly without third-party network clients or tunnels.
2. 1-Tap Review Publishing via Telegram inline keyboard directly to GitHub repo.
3. Two-way live technical support chat with 100% full media support (Photos, Screenshots, Documents, Voice, Video).
4. Universal /dns, /setup, /status, /donate, /help commands for private chats and groups.
5. Auto-registered Telegram menu commands (setMyCommands for users and admin scope).
6. Emergency Alert Broadcast System (/alert, /users) with interactive confirmation and live delivery reporting.
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


SUBSCRIBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")
INITIAL_KNOWN_USERS = [1452460886, 693846199, 268714811, 8970015768, 5786272987]

subscribers_lock = threading.Lock()
subscribers = {}
PENDING_ALERTS = {}
PENDING_REVIEWS_REPLIES = {}  # admin_chat_id -> review_id

def load_subscribers():
    global subscribers
    with subscribers_lock:
        if os.path.exists(SUBSCRIBERS_FILE):
            try:
                with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "users" in data:
                        subscribers = data["users"]
                    elif isinstance(data, dict):
                        subscribers = data
                print(f"[SUBS LOAD] Loaded {len(subscribers)} subscribers from {SUBSCRIBERS_FILE}")
            except Exception as e:
                print(f"[SUBS ERROR] load: {e}")
        else:
            now_str = time.strftime('%Y-%m-%d %H:%M:%S')
            for uid in INITIAL_KNOWN_USERS:
                subscribers[str(uid)] = {
                    "user_id": uid,
                    "first_name": "MagicDNS User",
                    "username": "",
                    "first_seen": now_str,
                    "last_seen": now_str,
                    "is_active": True
                }
            save_subscribers_locked()
            print(f"[SUBS INIT] Seeded {len(subscribers)} initial subscribers")

def save_subscribers_locked():
    try:
        tmp_file = SUBSCRIBERS_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump({"users": subscribers, "updated_at": time.time()}, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file, SUBSCRIBERS_FILE)
    except Exception as e:
        print(f"[SUBS ERROR] save: {e}")

def register_subscriber(user_id, first_name="", username=""):
    if not user_id or user_id == ADMIN_CHAT_ID:
        return
    uid_str = str(user_id)
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    with subscribers_lock:
        if uid_str not in subscribers:
            subscribers[uid_str] = {
                "user_id": int(user_id),
                "first_name": first_name or "",
                "username": username or "",
                "first_seen": now_str,
                "last_seen": now_str,
                "is_active": True
            }
            save_subscribers_locked()
            print(f"[SUBS NEW] Registered user {user_id} ({first_name} {username})")
        else:
            changed = False
            sub = subscribers[uid_str]
            if first_name and sub.get("first_name") != first_name:
                sub["first_name"] = first_name
                changed = True
            if username and sub.get("username") != username:
                sub["username"] = username
                changed = True
            if not sub.get("is_active", True):
                sub["is_active"] = True
                changed = True
            last = sub.get("last_seen", "")
            if last[:13] != now_str[:13]:
                sub["last_seen"] = now_str
                changed = True
            if changed:
                save_subscribers_locked()

def format_alert_message(raw_text):
    return (
        "🚨 <b>ВНИМАНИЕ: ОПОВЕЩЕНИЕ СЕТИ MAGICDNS!</b>\n\n"
        f"{html.escape(raw_text.strip())}\n\n"
        "<i>🟢 Проверить статус узлов: /status\n"
        "⚡ Параметры подключения: /dns\n"
        "💬 Техподдержка: просто напишите в этот чат</i>"
    )

def set_bot_commands():
    cmds = [
        {"command": "dns", "description": "⚡ Параметры и ссылки MagicDNS"},
        {"command": "status", "description": "🟢 Статус серверов сети"},
        {"command": "donate", "description": "☕ Поддержать серверы"},
        {"command": "help", "description": "💬 Помощь и связь с поддержкой"}
    ]
    try:
        res = tg_request("setMyCommands", {"commands": cmds})
        print(f"[BOT COMMANDS] Registered public menu: {res.get('ok')}")
    except Exception as e:
        print(f"[BOT COMMANDS ERROR] {e}")

    admin_cmds = [
        {"command": "admin", "description": "🛠 Панель управления"},
        {"command": "reviews", "description": "💬 Отзывы и ответы команды"},
        {"command": "reply", "description": "✍️ Ответить на отзыв по ID"},
        {"command": "alert", "description": "🚨 Оповещение в Telegram (рассылка)"},
        {"command": "sitealert", "description": "🌐 Оповещение на сайте magicdns.ru"},
        {"command": "clearsitealert", "description": "🔕 Снять оповещение с сайта"},
        {"command": "users", "description": "📊 Статистика аудитории бота"},
        {"command": "status", "description": "🟢 Статус серверов сети"},
        {"command": "dns", "description": "⚡ Параметры MagicDNS"},
        {"command": "help", "description": "💬 Справка и админка"}
    ]
    try:
        res_adm = tg_request("setMyCommands", {
            "commands": admin_cmds,
            "scope": {"type": "chat", "chat_id": ADMIN_CHAT_ID}
        })
        print(f"[BOT COMMANDS] Registered admin menu: {res_adm.get('ok')}")
    except Exception as e:
        print(f"[BOT ADMIN COMMANDS ERROR] {e}")

# Reusable Card and Keyboard Definitions
def get_dns_card():
    return (
        "⚡ <b>Параметры подключения MagicDNS:</b>\n\n"
        "• <b>Роутеры (Wi-Fi) и ПК:</b>\n"
        "  1️⃣ Основной (🇸🇪 Швеция): <code>109.120.132.43</code>\n"
        "  2️⃣ Второй (🇩🇪 Германия): <code>94.249.177.102</code>\n"
        "  3️⃣ Резерв (🇫🇮 Финляндия): <code>2.56.179.170</code>\n\n"
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
        "• 🇸🇪 Швеция (Основа / Core Node): 🟢 <code>109.120.132.43</code> (Штатно)\n"
        "• 🇩🇪 Германия (Второй узел / Backup): 🟢 <code>94.249.177.102</code> (Штатно)\n"
        "• 🇫🇮 Финляндия (Резерв / Relay): 🟢 <code>2.56.179.170</code> (Штатно)\n\n"
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
        "Бесплатный Smart DNS для прямого доступа к нейросетям (ChatGPT, Claude, Gemini, Perplexity) без сторонних приложений и тоннелей на полной скорости вашего интернета.\n\n"
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
            return True, "Отзыв успешно опубликован на GitHub!", new_review.get("id")
    except Exception as e:
        return False, f"Ошибка сохранения на GitHub: {e}", None

def get_admin_panel_card():
    return (
        "🛠 <b>Панель администратора MagicDNS:</b>\n\n"
        "Управляйте отзывами, сайтом и оповещениями через кнопки ниже:\n\n"
        "• 💬 <b>Отзывы и ответы:</b> просмотр отзывов и публикация официальных комментариев команды\n"
        "• 🌐 <b>Баннер на сайте:</b> включить или снять аварию на magicdns.ru\n"
        "• 🚨 <b>Рассылка:</b> экстренное оповещение всем подписчикам бота\n"
        "• 📊 <b>Статистика:</b> аудитория и активные пользователи"
    )

def get_admin_panel_kb():
    return {
        "inline_keyboard": [
            [{"text": "💬 Отзывы на сайте и ответы", "callback_data": "admin_reviews"}],
            [{"text": "🌐 Баннер на сайте", "callback_data": "admin_sitealert_info"}, {"text": "🚨 Рассылка", "callback_data": "admin_alert_info"}],
            [{"text": "📊 Статистика подписчиков", "callback_data": "cmd_users"}, {"text": "🟢 Статус сети", "callback_data": "cmd_status"}]
        ]
    }

def send_reviews_list(chat_id, offset=0, limit=5):
    if offset == 0:
        send_message(chat_id, "⏳ Загружаю отзывы с сайта...")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/reviews.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "MagicDNS-Bot"}
    revs = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            revs = json.loads(base64.b64decode(d['content']).decode('utf-8'))
    except Exception:
        try:
            local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.json")
            with open(local_p, "r", encoding="utf-8") as f:
                revs = json.load(f)
        except Exception:
            revs = []

    if not revs:
        send_message(chat_id, "📭 Список отзывов пуст.")
        return

    total_count = len(revs)
    batch = revs[offset:offset + limit]

    if offset == 0:
        send_message(
            chat_id,
            f"📋 <b>Отзывы на сайте magicdns.ru (Всего: {total_count}):</b>\n"
            f"<i>Показано {min(offset + len(batch), total_count)} из {total_count}. Нажмите кнопку под нужным отзывом для ответа:</i>"
        )

    for r in batch:
        stars = '★' * r.get('rating', 5)
        reply_info = ""
        btn_label = "💬 Ответить на этот отзыв"
        if r.get('reply'):
            rep = r['reply']
            rep_text = rep.get('text') if isinstance(rep, dict) else rep
            reply_info = f"\n\n💬 <b>Ответ команды:</b> <i>{html.escape(str(rep_text))}</i>"
            btn_label = "✏️ Изменить ответ команды"

        card_text = (
            f"⭐️ <b>{stars} ({r.get('rating')}/5)</b> — <b>{html.escape(str(r.get('author')))}</b> [{html.escape(str(r.get('platform')))}]\n"
            f"📅 {r.get('date', '')} | 🆔 <code>{r.get('id')}</code>\n\n"
            f"«{html.escape(str(r.get('message')))}»"
            f"{reply_info}"
        )
        kb = {
            "inline_keyboard": [
                [{"text": btn_label, "callback_data": f"reply_rev_{r.get('id')}"}]
            ]
        }
        send_message(chat_id, card_text, reply_markup=kb)

    shown_so_far = offset + len(batch)
    if shown_so_far < total_count:
        remaining = total_count - shown_so_far
        next_chunk = min(5, remaining)
        more_kb = {
            "inline_keyboard": [
                [
                    {"text": f"📥 Загрузить ещё {next_chunk} (осталось {remaining})", "callback_data": f"rev_page_{shown_so_far}"},
                    {"text": f"📜 Показать вообще все ({remaining})", "callback_data": f"rev_all_{shown_so_far}"}
                ],
                [{"text": "🛠 В панель администратора", "callback_data": "admin_panel"}]
            ]
        }
        send_message(
            chat_id,
            f"👇 <b>Показано {shown_so_far} из {total_count} отзывов.</b>",
            reply_markup=more_kb
        )
    else:
        end_kb = {
            "inline_keyboard": [
                [{"text": "🛠 В панель администратора", "callback_data": "admin_panel"}]
            ]
        }
        send_message(chat_id, f"✅ <b>Выгружены все {total_count} отзывов с сайта!</b>", reply_markup=end_kb)

def reply_to_review_on_github(review_id, reply_text, reply_author="Команда MagicDNS"):
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

    found = False
    for r in reviews:
        if str(r.get('id', '')) == str(review_id):
            if reply_text.strip():
                r['reply'] = {
                    'text': reply_text.strip(),
                    'date': formatted_date,
                    'author': reply_author
                }
            else:
                if 'reply' in r:
                    del r['reply']
            found = True
            break

    if not found:
        return False, f"Отзыв с ID {review_id} не найден."

    new_content_str = json.dumps(reviews, ensure_ascii=False, indent=2)
    new_content_b64 = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')

    update_payload = {
        "message": f"feat(reviews): reply to review {review_id}",
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
            # Also save locally
            try:
                local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.json")
                with open(local_p, 'w', encoding='utf-8') as lf:
                    lf.write(new_content_str)
            except Exception:
                pass
            return True, "Ответ на отзыв успешно опубликован на сайте!"
    except Exception as e:
        return False, f"Ошибка сохранения на GitHub: {e}"


def update_github_file(file_path, content_str, commit_message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "MagicDNS-Finland-VPS-Bot",
        "Accept": "application/vnd.github.v3+json"
    }
    sha = None
    req_get = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req_get, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            sha = data.get('sha')
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)

    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    payload = {
        "message": commit_message,
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha

    req_put = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req_put, timeout=15) as resp:
            return True, "Успешно сохранено на GitHub"
    except Exception as e:
        return False, f"Ошибка PUT: {e}"

def set_site_alert(active, message=""):
    alert_data = {
        "active": active,
        "type": "warning" if active else "info",
        "message": message.strip() if active else "",
        "updated_at": int(time.time())
    }
    json_str = json.dumps(alert_data, ensure_ascii=False, indent=2)

    # 1. Update on GitHub root and public/
    ok1, msg1 = update_github_file("alert.json", json_str, f"chore: {'activate' if active else 'clear'} site alert")
    update_github_file("public/alert.json", json_str, f"chore: {'activate' if active else 'clear'} site alert in public")

    # 2. Also save locally on server
    try:
        local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert.json")
        with open(local_p, 'w', encoding='utf-8') as f:
            f.write(json_str)
    except Exception as e:
        print(f"[LOCAL ALERT SAVE ERR] {e}")

    return ok1, msg1

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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/alert'):
            local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert.json")
            data = {"active": False, "type": "info", "message": "", "updated_at": 0}
            if os.path.exists(local_p):
                try:
                    with open(local_p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"[API ALERT ERR] {e}")

            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/feedback':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8', errors='ignore')

            try:
                data = json.loads(body)
                author = data.get('name', 'Пользователь MagicDNS').strip() or 'Пользователь MagicDNS'
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

    load_subscribers()
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
                    from_user = cq.get('from', {})
                    register_subscriber(from_id, from_user.get('first_name'), from_user.get('username'))

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

                    if data == 'clear_site_alert':
                        answer_callback(cq_id, "⏳ Снимаю оповещение с сайта...")
                        ok, status_msg = set_site_alert(False, "")
                        if ok:
                            answer_callback(cq_id, "✅ Оповещение снято с сайта!")
                            edit_message(ADMIN_CHAT_ID, msg_id, "🔕 <b>Оповещение на сайте magicdns.ru успешно снято!</b>\n\n<i>Баннер скрыт для всех посетителей.</i>")
                        else:
                            answer_callback(cq_id, f"⚠️ Ошибка: {status_msg}", alert=True)
                        continue

                    if data == 'cancel_alert':
                        PENDING_ALERTS.pop(ADMIN_CHAT_ID, None)
                        answer_callback(cq_id, "❌ Рассылка отменена")
                        edit_message(ADMIN_CHAT_ID, msg_id, "❌ <i>Экстренное оповещение отменено администратором.</i>")
                        continue

                    if data == 'test_alert':
                        pending = PENDING_ALERTS.get(ADMIN_CHAT_ID)
                        if not pending:
                            answer_callback(cq_id, "⚠️ Оповещение устарело, создайте заново: /alert", alert=True)
                            continue
                        test_text = format_alert_message(pending["text"])
                        send_message(ADMIN_CHAT_ID, "🧪 <b>[ТЕСТОВОЕ ОПОВЕЩЕНИЕ]</b>\nВот так сообщение выглядит у пользователей:")
                        if pending.get("media_msg"):
                            copy_message(ADMIN_CHAT_ID, ADMIN_CHAT_ID, pending["media_msg"]['message_id'], caption=test_text, parse_mode="HTML")
                        else:
                            send_message(ADMIN_CHAT_ID, test_text)
                        answer_callback(cq_id, "✅ Тестовое оповещение отправлено вам в чат!")
                        continue

                    if data == 'confirm_alert':
                        pending = PENDING_ALERTS.pop(ADMIN_CHAT_ID, None)
                        if not pending:
                            answer_callback(cq_id, "⚠️ Оповещение устарело, создайте заново: /alert", alert=True)
                            continue

                        answer_callback(cq_id, "🚨 Начинаю рассылку оповещения...")
                        edit_message(ADMIN_CHAT_ID, msg_id, "⏳ <b>Выполняется экстренная рассылка оповещения...</b>\n\n<i>Пожалуйста, подождите завершения отправки.</i>")

                        def run_broadcast(alert_info, status_msg_id):
                            alert_body = format_alert_message(alert_info["text"])
                            media_msg = alert_info.get("media_msg")

                            with subscribers_lock:
                                recipients = [u for u in subscribers.values() if u.get('is_active', True) and u.get('user_id') != ADMIN_CHAT_ID]

                            total = len(recipients)
                            sent = 0
                            blocked = 0
                            errors = 0
                            start_time = time.time()

                            for u in recipients:
                                uid = u.get('user_id')
                                try:
                                    if media_msg:
                                        res = copy_message(uid, ADMIN_CHAT_ID, media_msg['message_id'], caption=alert_body, parse_mode="HTML")
                                    else:
                                        res = send_message(uid, alert_body)

                                    if res.get('ok'):
                                        sent += 1
                                    else:
                                        err_str = str(res.get('error', ''))
                                        if '403' in err_str or 'blocked' in err_str.lower() or 'deactivated' in err_str.lower():
                                            blocked += 1
                                            with subscribers_lock:
                                                if str(uid) in subscribers:
                                                    subscribers[str(uid)]['is_active'] = False
                                        else:
                                            errors += 1
                                except Exception as ex:
                                    errors += 1
                                    print(f"[BROADCAST ERR] {uid}: {ex}")

                                time.sleep(0.05)

                            with subscribers_lock:
                                save_subscribers_locked()

                            elapsed = round(time.time() - start_time, 1)
                            report = (
                                f"✅ <b>ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ ЗАВЕРШЕНО!</b>\n\n"
                                f"📊 <b>Отчет о доставке:</b>\n"
                                f"• 👥 Всего получателей: {total}\n"
                                f"• 📬 Успешно доставлено: {sent}\n"
                                f"• 🚫 Заблокировали бота: {blocked}\n"
                                f"• ⚠️ Ошибок отправки: {errors}\n"
                                f"• ⏱ Время отправки: {elapsed} сек.\n\n"
                                f"📢 <b>Разосланный текст:</b>\n"
                                f"<i>{html.escape(alert_info['text'][:250])}</i>"
                            )
                            edit_message(ADMIN_CHAT_ID, status_msg_id, report)
                            print(f"[BROADCAST DONE] Sent: {sent}/{total}, Blocked: {blocked}, Errors: {errors} in {elapsed}s")

                        t = threading.Thread(target=run_broadcast, args=(pending, msg_id), daemon=True)
                        t.start()
                        continue

                    if data == 'admin_panel':
                        answer_callback(cq_id)
                        edit_message(ADMIN_CHAT_ID, msg_id, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                        continue

                    if data == 'admin_reviews':
                        answer_callback(cq_id, "Загружаю отзывы...")
                        send_reviews_list(ADMIN_CHAT_ID)
                        continue

                    if data == 'admin_sitealert_info':
                        answer_callback(cq_id)
                        send_message(
                            ADMIN_CHAT_ID,
                            "🌐 <b>Управление баннером на сайте:</b>\n\n"
                            "• Включить: <code>/sitealert Текст аварии</code>\n"
                            "• Снять: <code>/clearsitealert</code>"
                        )
                        continue

                    if data == 'admin_alert_info':
                        answer_callback(cq_id)
                        send_message(
                            ADMIN_CHAT_ID,
                            "🚨 <b>Экстренная рассылка подписчикам:</b>\n\n"
                            "Отправьте команду:\n<code>/alert Текст оповещения</code>"
                        )
                        continue

                    if data.startswith('rev_all_'):
                        curr_offset = int(data.replace('rev_all_', ''))
                        answer_callback(cq_id, "Выгружаю все отзывы...")
                        send_reviews_list(ADMIN_CHAT_ID, offset=curr_offset, limit=100)
                        continue

                    if data.startswith('rev_page_'):
                        next_offset = int(data.replace('rev_page_', ''))
                        answer_callback(cq_id, "Загружаю ещё отзывы...")
                        send_reviews_list(ADMIN_CHAT_ID, offset=next_offset, limit=5)
                        continue

                    if data.startswith('reply_rev_'):
                        rev_id = data.replace('reply_rev_', '').strip()
                        PENDING_REVIEWS_REPLIES[ADMIN_CHAT_ID] = rev_id
                        answer_callback(cq_id, "✍️ Введите ответ в чат")
                        send_message(
                            ADMIN_CHAT_ID,
                            f"💬 <b>Ответ команды на отзыв #{rev_id}:</b>\n\n"
                            f"Отправьте текст ответа следующим сообщением, и он сразу появится на сайте прямо под этим отзывом.\n"
                            f"<i>(Для отмены отправьте /cancel)</i>"
                        )
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
                            res = publish_review_to_github(author, platform, rating, review_text)
                            ok = res[0]
                            status_msg = res[1]
                            new_rev_id = res[2] if len(res) > 2 else None
                            if ok:
                                stars_str = '★' * rating
                                esc_author = html.escape(str(author))
                                esc_platform = html.escape(str(platform))
                                esc_text = html.escape(str(review_text))
                                updated_text = (
                                    f"✅ <b>ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\n\n"
                                    f"👤 <b>Автор:</b> {esc_author}\n"
                                    f"💻 <b>Платформа:</b> {esc_platform}\n"
                                    f"⭐️ <b>Оценка:</b> {stars_str} ({rating}/5)\n"
                                    f"🆔 <b>ID:</b> <code>{new_rev_id}</code>\n\n"
                                    f"💬 <b>Текст:</b>\n{esc_text}\n\n"
                                    f"🌐 <i>Отзыв уже залит в reviews.json и доступен на сайте!</i>"
                                )
                                pub_kb = {
                                    "inline_keyboard": [
                                        [{"text": "💬 Ответить на этот отзыв", "callback_data": f"reply_rev_{new_rev_id}"}],
                                        [{"text": "🌐 Открыть сайт", "url": "https://magicdns.ru"}]
                                    ]
                                } if new_rev_id else None
                                edit_message(ADMIN_CHAT_ID, msg_id, updated_text, reply_markup=pub_kb)
                                answer_callback(cq_id, "🎉 Успешно! Отзыв опубликован на сайте!")
                                print(f"[PUB SUCCESS] Review by {author} (ID: {new_rev_id}) published to reviews.json!")
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

                    if chat_type == 'private' and sender_id != ADMIN_CHAT_ID:
                        register_subscriber(sender_id, sender_name, username)

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

                    # Admin Emergency Broadcast & Statistics
                    if cmd in ['/alert', '/broadcast', '/notify', 'оповещение', 'рассылка']:
                        if sender_id != ADMIN_CHAT_ID:
                            send_message(chat_id, "⛔ Команда доступна только администратору сервиса.")
                            continue

                        alert_text = ""
                        reply_to = m.get('reply_to_message')
                        tokens = text.strip().split(maxsplit=1)

                        if len(tokens) > 1:
                            alert_text = tokens[1].strip()
                        elif reply_to:
                            alert_text = reply_to.get('text') or reply_to.get('caption') or ""

                        if not alert_text:
                            guide = (
                                "⚠️ <b>Как сделать экстренное оповещение:</b>\n\n"
                                "1. Напишите команду с текстом аварии:\n"
                                "<code>/alert Внимание! На шведском узле технические работы. Пожалуйста, временно переключитесь на немецкий узел: 94.249.177.102</code>\n\n"
                                "2. Или отправьте скриншот/сообщение и ответьте на него командой <code>/alert</code>.\n\n"
                                "<i>Перед отправкой бот покажет превью и попросит подтверждение!</i>"
                            )
                            send_message(ADMIN_CHAT_ID, guide)
                            continue

                        with subscribers_lock:
                            active_recipients = [u for u in subscribers.values() if u.get('is_active', True) and u.get('user_id') != ADMIN_CHAT_ID]
                            recipient_count = len(active_recipients)

                        PENDING_ALERTS[ADMIN_CHAT_ID] = {
                            "text": alert_text,
                            "media_msg": reply_to if (reply_to and (reply_to.get('photo') or reply_to.get('document') or reply_to.get('video'))) else None,
                            "created_at": time.time()
                        }

                        formatted_preview = format_alert_message(alert_text)
                        preview_card = (
                            f"⚠️ <b>ПОДТВЕРЖДЕНИЕ ЭКСТРЕННОГО ОПОВЕЩЕНИЯ:</b>\n\n"
                            f"👥 <b>Получателей:</b> {recipient_count} чел.\n\n"
                            f"📢 <b>Предпросмотр сообщения:</b>\n"
                            f"————————————————————\n"
                            f"{formatted_preview}\n"
                            f"————————————————————\n\n"
                            f"<i>Разослать оповещение всем пользователям бота?</i>"
                        )

                        alert_kb = {
                            "inline_keyboard": [
                                [{"text": f"🚨 Да, разослать всем ({recipient_count})", "callback_data": "confirm_alert"}],
                                [{"text": "🧪 Проверить (отправить мне в ЛС)", "callback_data": "test_alert"}],
                                [{"text": "❌ Отменить", "callback_data": "cancel_alert"}]
                            ]
                        }
                        send_message(ADMIN_CHAT_ID, preview_card, reply_markup=alert_kb)
                        continue

                                        # Site Alert Controls
                    elif cmd in ['/sitealert', '/alertsite', 'оповещениесайта']:
                        if sender_id != ADMIN_CHAT_ID:
                            send_message(chat_id, "⛔ Команда доступна только администратору сервиса.")
                            continue

                        tokens = text.strip().split(maxsplit=1)
                        arg = tokens[1].strip() if len(tokens) > 1 else ""

                        if not arg:
                            site_guide = (
                                "🌐 <b>Управление оповещением на сайте magicdns.ru:</b>\n\n"
                                "• <b>Включить баннер на сайте:</b>\n"
                                "<code>/sitealert Внимание! На шведском узле идут технические работы. Пожалуйста, используйте адрес 94.249.177.102</code>\n\n"
                                "• <b>Снять баннер с сайта:</b>\n"
                                "<code>/clearsitealert</code> (или <code>/sitealert off</code>)"
                            )
                            send_message(ADMIN_CHAT_ID, site_guide)
                            continue

                        if arg.lower() in ['off', 'clear', 'stop', 'удалить', 'выкл', 'снять']:
                            send_message(ADMIN_CHAT_ID, "⏳ Снимаю баннер с сайта...")
                            ok, status_msg = set_site_alert(False, "")
                            if ok:
                                send_message(ADMIN_CHAT_ID, "🔕 <b>Оповещение успешно снято с сайта magicdns.ru!</b>\nБаннер отключен.")
                            else:
                                send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка при снятии: {status_msg}")
                            continue

                        send_message(ADMIN_CHAT_ID, "⏳ Публикую оповещение на сайт magicdns.ru...")
                        ok, status_msg = set_site_alert(True, arg)
                        if ok:
                            alert_msg = (
                                f"🚨 <b>ОПОВЕЩЕНИЕ ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\n\n"
                                f"📢 <b>Текст на сайте:</b>\n{arg}\n\n"
                                f"🌐 <i>Баннер отображается вверху сайта для всех посетителей.</i>"
                            )
                            kb = {
                                "inline_keyboard": [
                                    [{"text": "🔕 Снять оповещение с сайта", "callback_data": "clear_site_alert"}],
                                    [{"text": "🌐 Открыть сайт", "url": "https://magicdns.ru"}]
                                ]
                            }
                            send_message(ADMIN_CHAT_ID, alert_msg, reply_markup=kb)
                        else:
                            send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка при публикации на сайт: {status_msg}")
                        continue

                    elif cmd in ['/clearsitealert', '/sitealertoff', 'снятьоповещение']:
                        if sender_id != ADMIN_CHAT_ID:
                            continue
                        send_message(ADMIN_CHAT_ID, "⏳ Снимаю баннер с сайта...")
                        ok, status_msg = set_site_alert(False, "")
                        if ok:
                            send_message(ADMIN_CHAT_ID, "🔕 <b>Оповещение успешно снято с сайта magicdns.ru!</b>\nБаннер отключен.")
                        else:
                            send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка: {status_msg}")
                        continue

                    elif cmd in ['/reply', '/comment', 'ответить']:
                        if sender_id != ADMIN_CHAT_ID:
                            continue
                        tokens = text.strip().split(maxsplit=2)
                        if len(tokens) < 3:
                            send_message(
                                ADMIN_CHAT_ID,
                                "⚠️ <b>Использование:</b>\n<code>/reply &lt;ID_отзыва&gt; &lt;Текст ответа&gt;</code>\n\n"
                                "<i>Пример:</i>\n<code>/reply 1792840232408 Спасибо за отзыв, приятного пользования!</code>\n\n"
                                "Посмотреть последние отзывы: <code>/reviews</code>"
                            )
                            continue
                        r_id = tokens[1].strip()
                        r_text = tokens[2].strip()
                        send_message(ADMIN_CHAT_ID, f"⏳ Публикую ответ на отзыв #{r_id}...")
                        ok, msg = reply_to_review_on_github(r_id, r_text)
                        if ok:
                            send_message(
                                ADMIN_CHAT_ID,
                                f"✅ <b>Ответ на отзыв #{r_id} опубликован на сайте!</b>\n\n"
                                f"💬 <b>Ваш комментарий:</b>\n<i>{html.escape(r_text)}</i>"
                            )
                        else:
                            send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка: {msg}")
                        continue

                    elif cmd in ['/reviews', '/feedback', 'отзывы']:
                        if sender_id != ADMIN_CHAT_ID:
                            continue
                        send_reviews_list(ADMIN_CHAT_ID)
                        continue

                    elif cmd in ['/admin', '/menu', 'админ', 'панель']:
                        if sender_id != ADMIN_CHAT_ID:
                            continue
                        send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                        continue

                    elif cmd in ['/users', '/subs', '/subscribers', '/stats', 'статистика']:
                        if sender_id != ADMIN_CHAT_ID:
                            continue
                        with subscribers_lock:
                            total = len(subscribers)
                            active = len([u for u in subscribers.values() if u.get('is_active', True)])
                            blocked = total - active
                            sorted_users = sorted(subscribers.values(), key=lambda x: x.get('last_seen', ''), reverse=True)

                        stats_msg = (
                            f"📊 <b>Статистика пользователей бота MagicDNS:</b>\n\n"
                            f"👥 <b>Всего в базе:</b> {total}\n"
                            f"🟢 <b>Активных:</b> {active}\n"
                            f"🚫 <b>Заблокировали бота:</b> {blocked}\n\n"
                            f"<b>Последние активные:</b>\n"
                        )
                        for u in sorted_users[:5]:
                            uname = f"@{u.get('username')}" if u.get('username') else "без юзернейма"
                            stats_msg += f"• <code>{u.get('user_id')}</code> ({html.escape(u.get('first_name', ''))}, {uname}) — {u.get('last_seen')}\n"

                        stats_msg += "\n<i>Для рассылки аварийного оповещения используйте:</i>\n<code>/alert Текст аварии</code>"
                        send_message(ADMIN_CHAT_ID, stats_msg)
                        continue

                    elif cmd in ['/dns', '/setup', '/config', 'днс', 'настройка']:
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
                        if sender_id == ADMIN_CHAT_ID and chat_type == 'private':
                            send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                        continue

                    elif cmd == '/start':
                        if sender_id == ADMIN_CHAT_ID and chat_type == 'private':
                            send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                        else:
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
                        # Check if admin is sending a reply to a review
                        if sender_id == ADMIN_CHAT_ID and ADMIN_CHAT_ID in PENDING_REVIEWS_REPLIES:
                            if text.strip().lower() in ['/cancel', 'отмена', 'cancel']:
                                del PENDING_REVIEWS_REPLIES[ADMIN_CHAT_ID]
                                send_message(ADMIN_CHAT_ID, "❌ Добавление ответа отменено.")
                                continue
                            target_rev_id = PENDING_REVIEWS_REPLIES.pop(ADMIN_CHAT_ID)
                            send_message(ADMIN_CHAT_ID, f"⏳ Публикую ответ на отзыв #{target_rev_id}...")
                            ok, msg = reply_to_review_on_github(target_rev_id, text.strip())
                            if ok:
                                send_message(
                                    ADMIN_CHAT_ID,
                                    f"✅ <b>Ответ на отзыв #{target_rev_id} успешно опубликован на сайте!</b>\n\n"
                                    f"💬 <b>Ваш комментарий:</b>\n<i>{html.escape(text.strip())}</i>"
                                )
                            else:
                                send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка: {msg}")
                            continue

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
