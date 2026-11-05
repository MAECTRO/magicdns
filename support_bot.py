"""

MagicDNS 24/7 Cloud Support, Relay & 1-Tap Review Moderation Bot

Runs as systemd service on Management Host.



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

import requests

from concurrent.futures import ThreadPoolExecutor

import subprocess

import ssl

import uuid

import socket

from http.server import HTTPServer, BaseHTTPRequestHandler

from datetime import datetime



BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

ADMIN_CHAT_ID = 8010010144

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

GITHUB_REPO = "MAECTRO/magicdns"

import urllib.parse

SHARE_TEXT = "Держи рабочий DNS без VPN. Gemini, ChatGPT и Claude работают напрямую на полной скорости. Настраивается за 1 минуту:"
SHARE_URL = f"https://t.me/share/url?url=https%3A%2F%2Ft.me%2Fmagicdns_alert_bot&text={urllib.parse.quote(SHARE_TEXT)}"
COMMUNITY_CHAT_URL = os.environ.get("COMMUNITY_CHAT_URL", "")

def get_community_btn():
    if COMMUNITY_CHAT_URL:
        return {"text": "💬 Чат сообщества", "url": COMMUNITY_CHAT_URL}
    return {"text": "💬 Чат сообщества", "callback_data": "community_chat"}



DONATE_URL = "https://pay.cloudtips.ru/p/596a95a5"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# High-performance HTTP Keep-Alive session for Telegram API
tg_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=25, pool_maxsize=35, max_retries=1)
tg_session.mount("https://", adapter)
tg_session.mount("http://", adapter)

# Thread pool for asynchronous callback/message processing so getUpdates is never blocked
executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="tg_worker")



MONTHS_RU = {

    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',

    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',

    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'

}



def sanitize_reply_markup(chat_id, reply_markup):
    """Telegram Bot API forbids web_app buttons in inline keyboards sent to groups/supergroups/channels.
    This helper converts any web_app button into a standard url button if chat_id < 0."""
    if not reply_markup:
        return reply_markup
    
    # Handle string encoded JSON
    is_json_str = False
    if isinstance(reply_markup, str):
        try:
            reply_markup = json.loads(reply_markup)
            is_json_str = True
        except Exception:
            return reply_markup

    try:
        cid = int(chat_id)
        is_group = (cid < 0)
    except Exception:
        is_group = False

    if not is_group or not isinstance(reply_markup, dict):
        return json.dumps(reply_markup) if is_json_str else reply_markup

    ikb = reply_markup.get("inline_keyboard")
    if not ikb or not isinstance(ikb, list):
        return json.dumps(reply_markup) if is_json_str else reply_markup

    new_ikb = []
    for row in ikb:
        new_row = []
        for btn in row:
            if isinstance(btn, dict):
                b = dict(btn)
                if "web_app" in b:
                    wa = b.pop("web_app")
                    if isinstance(wa, dict) and "url" in wa:
                        b["url"] = wa["url"]
                new_row.append(b)
            else:
                new_row.append(btn)
        new_ikb.append(new_row)

    res = dict(reply_markup)
    res["inline_keyboard"] = new_ikb
    return json.dumps(res) if is_json_str else res


def tg_request(method, data=None, timeout=10):
    if isinstance(data, dict):
        cid = data.get("chat_id")
        rm = data.get("reply_markup")
        if cid is not None and rm is not None:
            data["reply_markup"] = sanitize_reply_markup(cid, rm)
    url = f"{BASE_URL}/{method}"
    try:
        if data is not None:
            resp = tg_session.post(url, json=data, timeout=timeout)
        else:
            resp = tg_session.get(url, timeout=timeout)
        
        try:
            res_json = resp.json()
        except Exception:
            res_json = {"ok": False, "status_code": resp.status_code, "text": resp.text}

        if not resp.ok:
            body = resp.text
            print(f"[TG HTTP ERROR] {method} ({resp.status_code}): {body}")
            if resp.status_code == 409:
                print("[TG 409] Backing off 12s...")
                time.sleep(12)
            if resp.status_code == 400 and "can't parse entities" in body and isinstance(data, dict) and data.get("parse_mode"):
                print(f"[TG HTML FALLBACK] Retrying {method} as plain text...")
                retry_data = dict(data)
                retry_data.pop("parse_mode", None)
                return tg_request(method, retry_data, timeout=timeout)
        return res_json
    except requests.exceptions.Timeout as e:
        if method != "getUpdates":
            print(f"[TG TIMEOUT] {method}: {e}")
        return {'ok': False, 'error': f"timeout: {e}"}
    except Exception as e:
        print(f"[TG ERROR] {method}: {e}")
        return {'ok': False, 'error': str(e)}


def answer_callback(cq_id, text="", alert=False):
    payload = {"callback_query_id": cq_id, "show_alert": alert}
    if text:
        payload["text"] = text
    return tg_request("answerCallbackQuery", payload, timeout=5)


def delete_message(chat_id, message_id):
    return tg_request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})


def edit_message(chat_id, message_id, text, parse_mode="HTML", reply_markup=None):

    payload = {

        "chat_id": chat_id,

        "message_id": message_id,

        "text": text,

        "parse_mode": parse_mode

    }

    if reply_markup is not None:

        payload["reply_markup"] = reply_markup

    return tg_request("editMessageText", payload)



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



def send_document(chat_id, filename, file_bytes, caption="", parse_mode="HTML", reply_markup=None):
    url = f"{BASE_URL}/sendDocument"
    files = {"document": (filename, file_bytes, "application/x-apple-aspen-config")}
    data = {"chat_id": str(chat_id), "caption": caption, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = tg_session.post(url, data=data, files=files, timeout=25)
        return resp.json()
    except Exception as e:
        print(f"[TG SEND_DOC ERROR] {e}")
        return {'ok': False, 'error': str(e)}


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



def send_sticker(chat_id, sticker_file_id, reply_to_message_id=None):

    data = {

        "chat_id": chat_id,

        "sticker": sticker_file_id

    }

    if reply_to_message_id:

        data["reply_to_message_id"] = reply_to_message_id

    return tg_request("sendSticker", data)



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
PENDING_SITE_ALERTS = {}

PENDING_REVIEWS_REPLIES = {}  # admin_chat_id -> review_id

PENDING_USER_MESSAGES = {}  # user_id -> dict with pending message
ACTIVE_ADMIN_REPLY = {}     # admin_id -> {"target_user_id": int, "name": str, "username": str, "question": str, "time": float}
USER_SUPPORT_CONTEXT = {}   # user_id -> {"name": str, "username": str, "last_text": str, "time": float}




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


def show_alert_preview(alert_text, media_msg=None, reply_to_msg_id=None):
    with subscribers_lock:
        active_recipients = [u for u in subscribers.values() if u.get('is_active', True) and u.get('user_id') != ADMIN_CHAT_ID]
        recipient_count = len(active_recipients)

    PENDING_ALERTS[ADMIN_CHAT_ID] = {
        "text": alert_text,
        "media_msg": media_msg,
        "created_at": time.time()
    }

    formatted_preview = format_alert_message(alert_text)
    preview_card = (
        f"🚨 <b>ПОДТВЕРЖДЕНИЕ ЭКСТРЕННОГО ОПОВЕЩЕНИЯ (БОТ):</b>\n\n"
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
    return send_message(ADMIN_CHAT_ID, preview_card, reply_to_message_id=reply_to_msg_id, reply_markup=alert_kb)


def show_sitealert_picker(site_text, reply_to_msg_id=None):
    draft_id = str(int(time.time() * 1000))
    PENDING_SITE_ALERTS[draft_id] = site_text.strip()

    draft_msg = (
        f"🌐 <b>Черновик баннера для сайта magicdns.ru:</b>\n\n"
        f"<i>«{html.escape(site_text.strip())}»</i>\n\n"
        f"<b>Выберите тип и цвет баннера:</b>"
    )
    kb = {
        "inline_keyboard": [
            [{"text": "🟢 Восстановление (зелёный)", "callback_data": f"pub_alert:{draft_id}:success"}],
            [{"text": "⚠️ Авария / Техработы (жёлтый)", "callback_data": f"pub_alert:{draft_id}:warning"}],
            [{"text": "ℹ️ Инфо / Анонс (синий)", "callback_data": f"pub_alert:{draft_id}:info"}],
            [{"text": "❌ Отмена", "callback_data": f"pub_alert:{draft_id}:cancel"}]
        ]
    }
    return send_message(ADMIN_CHAT_ID, draft_msg, reply_to_message_id=reply_to_msg_id, reply_markup=kb)




def set_bot_commands():

    cmds = [

        {"command": "dns", "description": "⚡ Параметры и ссылки MagicDNS"},

        {"command": "check", "description": "🔍 Проверка подключения и нейросетей"},

        {"command": "routers", "description": "📡 Настройка роутера (Wi-Fi)"},

        {"command": "android", "description": "🤖 Настройка для Android (DoT)"},

        {"command": "ios", "description": "🍏 Профиль для iPhone и iPad"},

        {"command": "faq", "description": "❓ Решение частых проблем (FAQ)"},

        {"command": "status", "description": "🟢 Статус серверов сети"},

        {"command": "donate", "description": "☕ Поддержать серверы"},

        {"command": "help", "description": "💬 Помощь и связь с поддержкой"},

        {"command": "friends", "description": "🤝 Друзья проекта (Dagami DNS)"}

    ]

    try:

        res = tg_request("setMyCommands", {"commands": cmds})

        print(f"[BOT COMMANDS] Registered public menu: {res.get('ok')}")

    except Exception as e:

        print(f"[BOT COMMANDS ERROR] {e}")



    admin_cmds = [

        {"command": "admin", "description": "🛠 Панель управления"},

        {"command": "testai", "description": "🧪 Экспресс-тест доступности ИИ"},

        {"command": "dig", "description": "🔍 DNS-диагностика любого домена"},

        {"command": "faq", "description": "❓ Решение частых проблем (FAQ)"},

        {"command": "ios", "description": "🍏 Профиль для iPhone и iPad"},

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

SERVERS_STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servers_status.json")



DEFAULT_SERVERS_STATUS = {

    "se": {

        "name": "🇩🇪 Франкфурт (Основа / Core Node)",

        "short_name": "🇩🇪 Франкфурт",

        "ip": "109.120.177.170",

        "status": "ok"

    },

    "de": {

        "name": "🇩🇪 Второй узел (Backup)",

        "short_name": "🇩🇪 Второй узел",

        "ip": "45.88.163.92",

        "status": "ok"

    }

}



def load_servers_status():

    try:

        if os.path.exists(SERVERS_STATUS_FILE):

            with open(SERVERS_STATUS_FILE, "r", encoding="utf-8") as f:

                loaded = json.load(f)

                res = {k: v.copy() for k, v in DEFAULT_SERVERS_STATUS.items()}

                for k, v in loaded.items():

                    if k in res:

                        res[k].update(v)

                return res

    except Exception as e:

        print(f"[STATUS LOAD ERR] {e}")

    return {k: v.copy() for k, v in DEFAULT_SERVERS_STATUS.items()}



def save_servers_status(data):

    try:

        with open(SERVERS_STATUS_FILE, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:

        print(f"[STATUS SAVE ERR] {e}")



STATUS_CONFIG = {

    "ok": {

        "badge": "🟢",

        "label": "Штатно",

        "title": "Работает стабильно"

    },

    "degraded": {

        "badge": "🟡",

        "label": "С перебоями",

        "title": "Высокая нагрузка / техработы"

    },

    "down": {

        "badge": "🔴",

        "label": "Авария",

        "title": "Временно недоступен"

    }

}



def get_dns_card():

    return (

        "⚡ <b>Параметры подключения MagicDNS:</b>\n\n"

        "• <b>Роутеры (Wi-Fi) и ПК:</b>\n"

        "  1️⃣ Основной (🇩🇪 Франкфурт): <code>109.120.177.170</code>\n"

        "  2️⃣ Второй (🇩🇪 Второй узел): <code>45.88.163.92</code>\n\n"

        "• <b>Android (Частный DNS-сервер):</b>\n"

        "  Имя хоста: <code>api.magicdns.ru</code>\n\n"

        "• <b>iPhone / iPad / Mac:</b>\n"

        "  Прямая ссылка на профиль: <a href='https://magicdns.ru/profile.mobileconfig'>https://magicdns.ru/profile.mobileconfig</a>\n"

        "  <i>(нажмите кнопку внизу или ссылку, чтобы скачать и установить профиль в Настройках)</i>\n\n"

        "• <b>Windows 10/11 и браузеры (DoH):</b>\n"

        "  Шаблон DoH: <code>https://api.magicdns.ru/sync</code>\n\n"

        "• <b>Linux (Ubuntu / Mint / Debian):</b>\n"

        "  DoT (порт 853): <code>109.120.177.170#api.magicdns.ru</code>\n"

        "  DoH (порт 443): <code>https://api.magicdns.ru/sync</code>\n\n"

        "🤝 <b>Дружественные проекты:</b>\n"

        "• <b>Dagami DNS:</b> <a href='https://dns.dagami.ru'>https://dns.dagami.ru</a> (чат @dagamvi)\n\n"

        "🌐 <b>Подробные инструкции с картинками:</b>\n"

        "<a href='https://magicdns.ru/#setup'>https://magicdns.ru/#setup</a>"

    )


def get_dns_kb():

    return {

        "inline_keyboard": [

            [{"text": "🤖 Настройка на Android", "callback_data": "cmd_android"}, {"text": "🍏 Профиль iOS / Mac", "callback_data": "cmd_ios"}],

            [{"text": "📡 Настройка роутера (Wi-Fi)", "callback_data": "cmd_routers"}, {"text": "🔍 Проверить подключение", "web_app": {"url": "https://magicdns.ru/check.html"}}],

            [get_community_btn(), {"text": "✈️ Поделиться с другом", "url": SHARE_URL}],

            [{"text": "❓ Частые вопросы (FAQ)", "callback_data": "faq_menu"}, {"text": "☕ Сказать спасибо", "url": DONATE_URL}],

            [{"text": "🤝 Дружественные проекты (Dagami DNS)", "callback_data": "faq_friends"}],

            [{"text": "🌐 Инструкция на сайте", "url": "https://magicdns.ru/#setup"}, {"text": "☕ Сказать спасибо", "url": DONATE_URL}]

        ]

    }




# -------------------------------------------------------------
# Global AI Status & Outage Detector (Cached 60s)
# -------------------------------------------------------------
AI_STATUS_CACHE = {
    "gemini": {"status": "ok", "name": "Google Gemini", "latency": 45},
    "openai": {"status": "ok", "name": "OpenAI (ChatGPT)", "latency": 60},
    "claude": {"status": "ok", "name": "Anthropic Claude", "latency": 75},
    "last_check": 0
}

def update_global_ai_status():
    global AI_STATUS_CACHE
    now = time.time()
    if now - AI_STATUS_CACHE.get("last_check", 0) < 60:
        return AI_STATUS_CACHE

    # Check Google Gemini
    try:
        t0 = time.time()
        r = requests.get("https://generativelanguage.googleapis.com", timeout=3, headers={"User-Agent": "MagicDNS/1.0"})
        lat = int((time.time() - t0) * 1000)
        st = "ok" if r.status_code in (200, 400, 403, 404) else "error"
        AI_STATUS_CACHE["gemini"] = {"status": st, "name": "Google Gemini", "latency": lat}
    except Exception:
        AI_STATUS_CACHE["gemini"] = {"status": "error", "name": "Google Gemini", "latency": 0}

    # Check OpenAI
    try:
        t0 = time.time()
        r = requests.get("https://status.openai.com/api/v2/status.json", timeout=3)
        lat = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            ind = r.json().get("status", {}).get("indicator", "none")
            st = "ok" if ind in ("none", "minor") else "error"
        else:
            st = "ok"
        AI_STATUS_CACHE["openai"] = {"status": st, "name": "OpenAI (ChatGPT)", "latency": lat}
    except Exception:
        AI_STATUS_CACHE["openai"] = {"status": "error", "name": "OpenAI (ChatGPT)", "latency": 0}

    # Check Claude
    try:
        t0 = time.time()
        r = requests.get("https://api.anthropic.com", timeout=3, headers={"User-Agent": "MagicDNS/1.0"})
        lat = int((time.time() - t0) * 1000)
        st = "ok" if r.status_code in (200, 400, 403, 404) else "error"
        AI_STATUS_CACHE["claude"] = {"status": st, "name": "Anthropic Claude", "latency": lat}
    except Exception:
        AI_STATUS_CACHE["claude"] = {"status": "error", "name": "Anthropic Claude", "latency": 0}

    AI_STATUS_CACHE["last_check"] = now
    return AI_STATUS_CACHE


# -------------------------------------------------------------
# Group Shield & Moderation Helpers
# -------------------------------------------------------------
PENDING_GROUP_CAPTCHAS = {}  # f"{chat_id}_{uid}" -> {"msg_id": id, "time": t}
GROUP_TRIGGER_COOLDOWNS = {} # f"{chat_id}_{topic}" -> t
GROUP_ADMINS_CACHE = {}      # chat_id -> {"admins": set(), "time": t}

def restrict_chat_member(chat_id, user_id, can_send_messages=True, until_date=0):
    permissions = {
        "can_send_messages": can_send_messages,
        "can_send_audios": can_send_messages,
        "can_send_documents": can_send_messages,
        "can_send_photos": can_send_messages,
        "can_send_videos": can_send_messages,
        "can_send_voice_notes": can_send_messages,
        "can_send_polls": can_send_messages,
        "can_send_other_messages": can_send_messages,
        "can_add_web_page_previews": can_send_messages
    }
    data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "permissions": permissions
    }
    if until_date:
        data["until_date"] = int(until_date)
    return tg_request("restrictChatMember", data)

def ban_chat_member(chat_id, user_id, until_date=0):
    data = {"chat_id": chat_id, "user_id": user_id}
    if until_date:
        data["until_date"] = int(until_date)
    return tg_request("banChatMember", data)

def unban_chat_member(chat_id, user_id, only_if_banned=True):
    return tg_request("unbanChatMember", {"chat_id": chat_id, "user_id": user_id, "only_if_banned": only_if_banned})

def delete_message(chat_id, message_id):
    return tg_request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def is_user_chat_admin(chat_id, user_id, sender_chat_id=None):
    # Telegram Anonymous Admin Bot ID (1087968824) is always an admin
    if user_id in (ADMIN_CHAT_ID, 1087968824):
        return True
    if sender_chat_id is not None and sender_chat_id == chat_id:
        return True
    now = time.time()
    cached = GROUP_ADMINS_CACHE.get(chat_id)
    if cached and (now - cached.get("time", 0) < 300):
        return (user_id in cached.get("admins", set())) or (sender_chat_id == chat_id)

    res = tg_request("getChatAdministrators", {"chat_id": chat_id})
    if res.get("ok"):
        admins = {adm["user"]["id"] for adm in res.get("result", []) if "user" in adm}
        admins.add(ADMIN_CHAT_ID)
        admins.add(1087968824)
        GROUP_ADMINS_CACHE[chat_id] = {"admins": admins, "time": now}
        return (user_id in admins) or (sender_chat_id == chat_id)
    return False

def get_status_card(is_admin=False):
    ai_status = update_global_ai_status()

    # Nodes info
    lines = [
        "🌐 <b>Шлюзы MagicDNS (Европа):</b>",
        "• 🇩🇪 Франкфурт (Основной): 🟢 <code>109.120.177.170</code> (Штатно)",
        "• 🇫🇮 Финляндия (Второй узел): 🟢 <code>45.88.163.92</code> (Штатно)",
        "",
        "🧠 <b>Глобальный статус нейросетей:</b>"
    ]

    ai_all_ok = True
    ai_alerts = []
    for k in ["gemini", "openai", "claude"]:
        item = ai_status.get(k, {})
        name = item.get("name", k)
        st = item.get("status", "ok")
        lat = item.get("latency", 50)
        if st == "ok":
            badge = "🟢"
            txt = f"Штатно ({lat} мс)"
        else:
            badge = "⚠️"
            txt = "Сбой на стороне сервиса"
            ai_all_ok = False
            ai_alerts.append(name)
        lines.append(f"• {name}: {badge} {txt}")

    if ai_all_ok:
        footer = "\n\n🛡️ <i>Все шлюзы и внешние API доступны. Трафик маршрутизируется без задержек.</i>"
    else:
        names_str = ", ".join(ai_alerts)
        footer = (
            f"\n\n⚠️ <i>Внимание: зафиксированы неполадки на стороне <b>{names_str}</b>. "
            "Шлюзы MagicDNS работают в штатном режиме, ожидаем восстановления внешнего API.</i>"
        )

    return f"🟢 <b>Статус сети и нейросетей MagicDNS:</b>\n\n" + "\n".join(lines) + footer


def get_status_kb(is_admin=False):

    buttons = [

        [{"text": "⚡ Параметры подключения", "callback_data": "cmd_dns"}],

        [{"text": "☕ Поддержать серверы", "url": DONATE_URL}],

        [{"text": "🌐 Сайт magicdns.ru", "url": "https://magicdns.ru"}]

    ]

    if is_admin:

        buttons.insert(0, [{"text": "🚦 Изменить статус серверов", "callback_data": "admin_srv_status"}])

    return {"inline_keyboard": buttons}



def get_admin_servers_card():

    statuses = load_servers_status()

    se = statuses.get("se", {})

    de = statuses.get("de", {})

    se_meta = STATUS_CONFIG.get(se.get("status", "ok"), STATUS_CONFIG["ok"])

    de_meta = STATUS_CONFIG.get(de.get("status", "ok"), STATUS_CONFIG["ok"])



    return (

        "🚦 <b>Управление состоянием серверов MagicDNS:</b>\n\n"

        f"🇩🇪 <b>Франкфурт (109.120.177.170):</b> {se_meta['badge']} {se_meta['label']}\n"

        f"🇩🇪 <b>Второй узел (45.88.163.92):</b> {de_meta['badge']} {de_meta['label']}\n\n"

        "<i>Нажмите на сервер ниже, чтобы переключить его статус (Штатно / С перебоями / Авария). "

        "Новый статус моментально отобразится всем пользователям в /status!</i>"

    )



def get_admin_servers_kb():

    statuses = load_servers_status()

    se_b = STATUS_CONFIG.get(statuses.get("se", {}).get("status", "ok"), STATUS_CONFIG["ok"])["badge"]

    de_b = STATUS_CONFIG.get(statuses.get("de", {}).get("status", "ok"), STATUS_CONFIG["ok"])["badge"]



    return {

        "inline_keyboard": [

            [{"text": f"🇸🇪 Швеция: {se_b}", "callback_data": "srv_pick_se"}],

            [{"text": f"🇩🇪 Германия: {de_b}", "callback_data": "srv_pick_de"}],

            [{"text": "🧪 Экспресс-тест доступности ИИ", "callback_data": "admin_test_ai"}],

            [{"text": "🛠 В панель администратора", "callback_data": "admin_panel"}]

        ]

    }



def get_server_picker_card(srv_key):

    statuses = load_servers_status()

    srv = statuses.get(srv_key, {})

    curr = STATUS_CONFIG.get(srv.get("status", "ok"), STATUS_CONFIG["ok"])

    name = srv.get("name", srv_key.upper())



    return (

        f"⚙️ <b>Настройка статуса для {name}:</b>\n\n"

        f"Текущее состояние: {curr['badge']} <b>{curr['label']}</b> ({curr['title']})\n\n"

        f"<i>Выберите новое состояние:</i>"

    )



def get_server_picker_kb(srv_key):

    return {

        "inline_keyboard": [

            [{"text": "🟢 Штатно (Стабильно)", "callback_data": f"srv_set_{srv_key}_ok"}],

            [{"text": "🟡 С перебоями (Нагрузка / Лаги)", "callback_data": f"srv_set_{srv_key}_degraded"}],

            [{"text": "🔴 Авария (Недоступен)", "callback_data": f"srv_set_{srv_key}_down"}],

            [{"text": "🔙 Назад к списку серверов", "callback_data": "admin_srv_status"}]

        ]

    }



def get_donate_card():

    return (

        "☕ <b>Поддержка серверов MagicDNS</b>\n\n"

        "MagicDNS — бесплатный независимый проект без рекламы и платных подписок.\n\n"

        "Все европейские узлы (Стокгольм, Франкфурт) мы оплачиваем самостоятельно. Если сервис помогает вам в работе с нейросетями, коде или учебе — любая чашка кофе поможет проекту жить дальше и развиваться. Спасибо каждому! ❤️"

    )



def get_donate_kb():

    return {

        "inline_keyboard": [

            [{"text": "☕ Поддержать серверы (CloudTips)", "url": DONATE_URL}],

            [{"text": "🌐 Официальный сайт", "url": "https://magicdns.ru"}]

        ]

    }



def get_group_rules_card():
    return (
        "📋 <b>Правила официального сообщества MagicDNS:</b>\n\n"
        "1️⃣ <b>Тематика чата:</b>\n"
        "Обсуждаем настройку Smart DNS, доступ к нейросетям (ChatGPT, Claude, Gemini), игровым сервисам и решение технических сетевых вопросов.\n\n"
        "2️⃣ <b>Спам и реклама:</b>\n"
        "Любая реклама каналов, услуг, реферальные ссылки и спам — немедленный бан навсегда без предупреждения.\n\n"
        "3️⃣ <b>Уважение и порядок:</b>\n"
        "Запрещены оскорбления, токсичность, мат и переход на личности. Мы здесь, чтобы помогать друг другу.\n\n"
        "4️⃣ <b>Безопасность:</b>\n"
        "Никогда не публикуйте в общем чате свои пароли, секретные ключи или токены доступа.\n\n"
        "🛡 <i>Нарушителей модераторы наказывают командами <code>!бан</code> и <code>!мут</code></i>"
    )

def get_group_rules_kb():
    return {
        "inline_keyboard": [
            [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}],
            [{"text": "🔍 Проверить подключение", "url": "https://magicdns.ru/check.html"}]
        ]
    }

def get_group_mod_card():
    return (
        "🛡 <b>Панель модерации группы MagicDNS:</b>\n\n"
        "Все модераторы группы могут управлять порядком прямо в чате через команды в ответ (Reply) на сообщение нарушителя:\n\n"
        "• <code>!бан</code> или <code>/ban</code> (ответом) — удаляет спам и навсегда банит спамера\n"
        "• <code>!мут 30</code> или <code>/mute 30</code> (ответом) — запрещает писать на 30 минут (можно указать любое число минут)\n"
        "• <code>!кик</code> или <code>/kick</code> (ответом) — исключает пользователя из чата\n\n"
        "🤖 <b>Автоматическая защита группы:</b>\n"
        "• <b>Антиспам-капча:</b> новые участники при входе автоматически глушатся, пока не нажмут кнопку подтверждения\n"
        "• <b>Умный автоответчик:</b> бот сам подсказывает инструкции по ключевым словам (<i>айфон, андроид, роутер</i>)\n\n"
        "⚙️ <i>Управление серверами, сайтом и рассылкой доступно владельцу в личных сообщениях бота: @magicdns_alert_bot (/admin)</i>"
    )

def get_group_mod_kb():
    return {
        "inline_keyboard": [
            [{"text": "🤖 Открыть меню в ЛС бота", "url": "https://t.me/magicdns_alert_bot?start=admin"}],
            [{"text": "📋 Правила группы", "callback_data": "cmd_rules"}]
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

            [{"text": "❓ Частые вопросы и ошибки (FAQ)", "callback_data": "faq_menu"}],

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

            [{"text": "🤖 Настройка Android", "callback_data": "cmd_android"}, {"text": "🍏 Профиль iOS", "callback_data": "cmd_ios"}],

            [{"text": "📡 Настройка роутера", "callback_data": "cmd_routers"}, {"text": "🔍 Проверить подключение", "web_app": {"url": "https://magicdns.ru/check.html"}}],

            [get_community_btn(), {"text": "✈️ Поделиться с другом", "url": SHARE_URL}],

            [{"text": "❓ Частые вопросы и ошибки (FAQ)", "callback_data": "faq_menu"}],

            [{"text": "🤝 Дружественные проекты (Dagami DNS)", "callback_data": "faq_friends"}],

            [{"text": "🌐 Инструкция на сайте", "url": "https://magicdns.ru/#setup"}, {"text": "☕ Сказать спасибо", "url": DONATE_URL}]

        ]

    }



# ==========================================

# FAQ & TROUBLESHOOTING KNOWLEDGE BASE

# ==========================================



def get_faq_menu_card():

    return (

        "❓ <b>База решений и частые вопросы (FAQ) MagicDNS</b>\n\n"

        "Выберите тему ниже, чтобы мгновенно получить пошаговую инструкцию:"

    )



def get_faq_menu_kb():

    return {

        "inline_keyboard": [

            [{"text": "🔴 Не открывается / Шлюз не обнаружен", "callback_data": "faq_troubleshoot"}],

            [{"text": "💻 Windows: команды сброса сети", "callback_data": "faq_win_reset"}],

            [{"text": "🌐 Яндекс Браузер, Chrome, Edge (DoH)", "callback_data": "faq_browser"}],

            [{"text": "📱 Android: ошибка подключения частного DNS", "callback_data": "faq_android"}],

            [{"text": "📶 Роутеры (Keenetic, TP-Link, MikroTik)", "callback_data": "faq_routers"}],

            [{"text": "🍏 iPhone / iPad / Mac: профиль", "callback_data": "faq_apple"}],

            [{"text": "🛡️ Безопасность: банки и Госуслуги", "callback_data": "faq_security"}],

            [{"text": "🐧 Linux (Ubuntu, Mint, Debian): DoT", "callback_data": "faq_linux"}],

            [{"text": "🤝 Дружественные проекты (Dagami DNS)", "callback_data": "faq_friends"}],

            [{"text": "👨‍💻 Связаться с администратором", "callback_data": "faq_contact_admin"}],

            [{"text": "⚡ Параметры подключения", "callback_data": "cmd_dns"}, {"text": "🟢 Статус серверов", "callback_data": "cmd_status"}]

        ]

    }



def get_faq_troubleshoot_card():

    return (

        "🔴 <b>Что делать, если сайты не открываются или пишет «Шлюз не обнаружен»:</b>\n\n"

        "1️⃣ <b>Выключите сторонние VPN!</b>\n"

        "Любой активный VPN (WireGuard, Outline, v2ray, Planet VPN) перехватывает все сетевые запросы и отправляет их в свой тоннель. MagicDNS при этом перестает действовать. Отключите VPN и обновите страницу.\n\n"

        "2️⃣ <b>Ошибка «Основной шлюз не обнаружен» (Windows / Android):</b>\n"

        "• <b>Windows:</b> Не трогайте верхнюю часть настроек IPv4 («Получать IP-адрес автоматически»)! Если затереть там шлюз роутера — пропадёт вся сеть. Адреса MagicDNS нужно вписывать <b>только в нижнее поле</b> («Использовать следующие адреса DNS-серверов»).\n"

        "• <b>Android:</b> В строке «Имя хоста поставщика частного DNS» должно быть строго <code>api.magicdns.ru</code> (без <code>https://</code> и без пробелов).\n\n"

        "3️⃣ <b>Сбросьте кэш браузера:</b>\n"

        "Браузер может помнить старый заблокированный IP адрес. Нажмите комбинацию клавиш <b>Ctrl + F5</b> (Cmd + Shift + R на Mac) либо откройте сайт в режиме Инкогнито.\n\n"

        "4️⃣ <b>Проверьте статус серверов:</b>\n"

        "Нажмите кнопку «🟢 Статус серверов» ниже, чтобы убедиться, что узлы в Швеции и Германии работают штатно."

    )



def get_faq_troubleshoot_kb():

    return {

        "inline_keyboard": [

            [{"text": "💻 Windows: команды сброса сети", "callback_data": "faq_win_reset"}],

            [{"text": "📱 Проблема на Android", "callback_data": "faq_android"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_win_reset_card():

    return (

        "💻 <b>Настройка и сброс сети Windows</b>\n\n"

        "Если после смены DNS пропал интернет, Windows ругается на «Шлюз не обнаружен» или перестали открываться сайты, выберите удобный формат инструкции:\n\n"

        "• <b>🐣 Инструкция для чайников</b> — подробно, с юмором, куда жать пальцем и как не сломать систему.\n"

        "• <b>⚡ Шпаргалка для профи</b> — сухие команды для терминала и параметры адаптера без лишних слов."

    )



def get_faq_win_reset_kb():

    return {

        "inline_keyboard": [

            [{"text": "🐣 Инструкция для чайников (по шагам)", "callback_data": "faq_win_noob"}],

            [{"text": "⚡ Шпаргалка для профи (без воды)", "callback_data": "faq_win_pro"}],

            [{"text": "🌐 Настройка в браузере (DoH)", "callback_data": "faq_browser"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_win_noob_card():

    return (

        "🐣 <b>Инструкция для чайников: реанимируем сеть на Windows</b>\n\n"

        "Спокойно, без паники! Компьютер ты не сломаешь, сейчас всё вернём к жизни за пару минут.\n\n"

        "<b>Шаг 1. Открываем командную строку от админа:</b>\n"

        "1. Зажми клавишу с флажком Windows и нажми английскую <b>R</b>.\n"

        "2. Вбей туда <code>cmd</code>, зажми <b>Ctrl + Shift</b> и нажми <b>Enter</b>.\n\n"

        "<b>Шаг 2. Магические команды по очереди:</b>\n"

        "Копируй эти 4 строчки строго по одной и вставляй в чёрное окно, нажимая Enter:\n\n"

        "<code>ipconfig /flushdns</code>\n"

        "<i>(стирает старый кэш DNS)</i>\n\n"

        "<code>netsh winsock reset</code>\n"

        "<i>(сбрасывает зависшие сетевые сокеты и старые VPN)</i>\n\n"

        "<code>netsh int ip reset</code>\n"

        "<i>(сбрасывает стек протокола TCP/IP до заводского)</i>\n\n"

        "<code>ipconfig /renew</code>\n"

        "<i>(обновляет аренду IP-адреса у роутера)</i>\n\n"

        "<b>Шаг 3. Перезагрузка:</b>\n"

        "Пуск → Перезагрузка (обязательно для применения изменений).\n\n"

        "<b>Шаг 4. Настройка DNS (Панель сетевых подключений):</b>\n"

        "1. Нажми <b>Win + R</b>, введи <code>ncpa.cpl</code> и нажми Enter.\n"

        "2. Правой кнопкой по сети (Ethernet или Wi-Fi) → <b>Свойства</b>.\n"

        "3. Дважды нажми на <b>«IP версии 4 (TCP/IPv4)»</b>.\n"

        "4. В верхней части оставь <i>«Получать IP-адрес автоматически»</i>.\n"

        "5. В нижней части укажи <i>«Использовать следующие адреса DNS-серверов»</i>:\n"

        "  — Предпочитаемый: <code>109.120.177.170</code>\n"

        "  — Альтернативный: <code>45.88.163.92</code>\n"

        "6. Нажми ОК и проверь доступность ChatGPT и Claude!\n\n"

        "💡 <i>Для Windows 11 (DoH): если настраиваешь через «Параметры», вбивай шаблон <code>https://api.magicdns.ru/sync</code> для обоих IP-адресов.</i>"

    )


def get_faq_win_noob_kb():

    return {

        "inline_keyboard": [

            [{"text": "⚡ Показать кратко для профи (без воды)", "callback_data": "faq_win_pro"}],

            [{"text": "🌐 Настройка в браузере (DoH)", "callback_data": "faq_browser"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_win_pro_card():

    return (

        "⚡ <b>Windows: Сброс сети и параметры DNS (Pro-версия)</b>\n\n"

        "<b>1. Терминал от Администратора (Win+X → Терминал):</b>\n"

        "<code>ipconfig /flushdns</code>\n"

        "<code>netsh winsock reset</code>\n"

        "<code>netsh int ip reset</code>\n"

        "<code>ipconfig /renew</code>\n\n"

        "<b>2. Сетевой адаптер (ncpa.cpl):</b>\n"

        "• <b>IPv4 Assignment:</b> DHCP (Auto)\n"

        "• <b>DNS Servers:</b>\n"

        "  — Primary (🇩🇪 Франкфурт): <code>109.120.177.170</code>\n"

        "  — Secondary (🇩🇪 Второй узел): <code>45.88.163.92</code>\n\n"

        "<b>3. Windows 11 DoH Template:</b>\n"

        "Параметры → Сеть → Wi-Fi / Ethernet → Назначение DNS: Вручную (IPv4):\n"

        "• Primary: <code>109.120.177.170</code> | DoH: <code>https://api.magicdns.ru/sync</code>\n"

        "• Alternate: <code>45.88.163.92</code> | DoH: <code>https://api.magicdns.ru/sync</code>\n\n"

        "<b>4. Экспресс-сброс hosts и выключение системного прокси (PowerShell):</b>\n"

        "<code>Set-Content -Path 'C:\\Windows\\System32\\drivers\\etc\\hosts' -Value '# default hosts' -Encoding Ascii; Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings' -Name ProxyEnable -Value 0</code>"

    )


def get_faq_win_pro_kb():

    return {

        "inline_keyboard": [

            [{"text": "🐣 Разжевать как для чайника", "callback_data": "faq_win_noob"}],

            [{"text": "🌐 Настройка в браузере (DoH)", "callback_data": "faq_browser"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_browser_card():

    return (

        "🌐 <b>Яндекс Браузер, Chrome, Edge, Brave (DNS-over-HTTPS)</b>\n\n"

        "Если в Windows DNS настроен, но браузер использует собственный встроенный безопасный резолвер, укажите шаблон DoH вручную:\n\n"

        "<b>Яндекс Браузер:</b>\n"

        "1. Меню → <b>Настройки</b> → вкладка <b>«Системные»</b> (или «Безопасность»).\n"

        "2. Блок <b>«Использовать DNS-серверы»</b> → «Вручную»:\n"

        "<code>https://api.magicdns.ru/sync</code>\n"

        "<i>Либо выберите «Системный DNS», чтобы браузер доверял сетевой карте.</i>\n\n"

        "<b>Chrome / Edge / Brave / Opera:</b>\n"

        "1. <b>Настройки</b> → <b>«Конфиденциальность и безопасность»</b> → <b>«Безопасность»</b>.\n"

        "2. Пункт <b>«Использовать безопасный DNS-сервер»</b> → «Вручную (Custom)»:\n"

        "<code>https://api.magicdns.ru/sync</code>\n"

        "3. Перезапустите вкладку."

    )


def get_faq_browser_kb():

    return {

        "inline_keyboard": [

            [{"text": "💻 Windows: команды сброса сети", "callback_data": "faq_win_reset"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_android_card():

    return (

        "📱 <b>Android: Решение проблем с «Персональным DNS»</b>\n\n"

        "1️⃣ <b>Ошибка «Не удалось подключиться»:</b>\n"

        "В настройках телефона (Подключения → Другие настройки → Персональный DNS) вводите строго чистое доменное имя:\n"

        "<code>api.magicdns.ru</code>\n"

        

        "<i>Не добавляйте http://, https:// или слеши — Android ждет чистый хост для DoT (порт 853).</i>\n\n"

        "2️⃣ <b>Если подключение всё равно сбрасывается:</b>\n"

        "• Проверьте, не включен ли параллельно старый VPN-профиль.\n"

        "• Переключите телефон в «Авиарежим» на 5 секунд и включите обратно.\n"

        "• Если ваш мобильный провайдер глушит порт 853, используйте приложение Intra или Nebulo с DoH (<code>https://api.magicdns.ru/sync</code>)."

    )


def get_faq_android_kb():

    return {

        "inline_keyboard": [

            [{"text": "🤖 Пошаговый мастер по марке смартфона", "callback_data": "cmd_android"}],

            [{"text": "🌐 Настройка в браузере (DoH)", "callback_data": "faq_browser"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_routers_card():

    return (

        "📶 <b>Настройка роутеров (для всей квартиры / офиса)</b>\n\n"

        "После настройки в роутере нейросети будут открываться на всех домашних устройствах без дополнительной возни.\n\n"

        "<b>Параметры для роутера:</b>\n"

        "• Основной DNS: <code>109.120.177.170</code>\n"

        "• Дополнительный DNS: <code>45.88.163.92</code>\n\n"

        "<b>Инструкции по маркам:</b>\n"

        "• <b>Keenetic:</b> 192.168.1.1 → «Сетевые правила» → «Интернет» → в вашем подключении добавьте оба IP. В компоненте DoH/DoT можно указать: <code>https://api.magicdns.ru/sync</code>\n"

        "• <b>TP-Link:</b> «Дополнительные настройки» → «Сеть» → «Интернет» (или DHCP) → укажите Первичный и Вторичный DNS.\n"

        "• <b>MikroTik:</b> В терминале WinBox выполните:\n"

        "<code>/ip dns set servers=109.120.177.170,45.88.163.92 allow-remote-requests=yes</code>\n"

        "• <b>ASUS:</b> «Интернет» → «Подключение» → «Подключаться к DNS автоматически: НЕТ» → введите IP-адреса."

    )


def get_faq_routers_kb():

    return {

        "inline_keyboard": [

            [{"text": "💻 Windows: команды сброса сети", "callback_data": "faq_win_reset"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_apple_card():

    return (

        "🍏 <b>iPhone, iPad и Mac: Профиль конфигурации</b>\n\n"

        "Для Apple мы собрали готовый зашифрованный профиль <code>.mobileconfig</code> (DNS-over-HTTPS).\n\n"

        "<b>Установка за 1 минуту:</b>\n"

        "1. Нажмите кнопку <b>«🍏 Скачать профиль в чат»</b> внизу.\n"

        "2. Нажмите на прикрепленный файл и подтвердите загрузку.\n"

        "3. Откройте <b>«Настройки»</b> iPhone/iPad.\n"

        "4. Вверху нажмите пункт <b>«Профиль загружен»</b>.\n"

        "5. Нажмите <b>«Установить»</b> (введите код-пароль устройства).\n\n"

        "<b>Как проверить активность:</b>\n"

        "«Настройки» → «Основные» → «VPN и управление устройством» → «DNS» → стоит галочка напротив <b>MagicDNS</b>.\n\n"

        "<i>На Mac профиль устанавливается в Системных настройках → Конфиденциальность и безопасность → Профили.</i>"

    )



def get_faq_apple_kb():

    return {

        "inline_keyboard": [

            [{"text": "🍏 Скачать профиль в чат", "callback_data": "cmd_ios"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_security_card():

    return (

        "🛡️ <b>Безопасность и приватность в MagicDNS</b>\n\n"

        "<b>Видит ли MagicDNS мои пароли, переписки или данные банков?</b>\n"

        "<b>НЕТ, это технически исключено:</b>\n\n"

        "• <b>Обычный интернет не перенаправляется:</b> Мы не являемся классическим VPN, который гонит весь трафик через себя. Сбербанк, Т-Банк, Госуслуги, VK, Яндекс и любые российские ресурсы открываются напрямую с вашего интернет-провайдера на максимальной скорости.\n\n"

        "• <b>Точечная маршрутизация:</b> Только конкретные зарубежные домены нейросетей (ChatGPT, Claude, Gemini, Cursor) направляются на европейский шлюз.\n\n"

        "• <b>Сквозное TLS-шифрование:</b> Весь обмен данными между вашим устройством и сервисами ИИ зашифрован сертификатами Cloudflare / OpenAI / Google. Доступа к содержимому запросов, токенам и паролям нет ни у кого, включая наши серверы."

    )



def get_faq_security_kb():

    return {

        "inline_keyboard": [

            [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "👨‍💻 Задать вопрос админу", "callback_data": "faq_contact_admin"}]

        ]

    }



def get_faq_contact_admin_card():

    return (

        "👨‍💻 <b>Связь с технической поддержкой MagicDNS</b>\n\n"

        "Если решения из FAQ не помогли решить вашу проблему:\n\n"

        "1. Просто напишите ваш вопрос прямо в этот чат.\n"

        "2. Приложите скриншот экрана (с ошибкой или настройками сети).\n\n"

        "Администратор сервиса получит обращение и ответит вам прямо здесь!"

    )



def get_faq_contact_admin_kb():

    return {

        "inline_keyboard": [

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}],

            [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

        ]

    }





def get_faq_linux_card():

    return (

        "🐧 <b>Подключение Linux (Ubuntu, Linux Mint, Debian)</b>\n\n"

        "<b>1️⃣ Быстрая настройка через терминал (DoT с шифрованием):</b>\n"

        "Подходит для систем с <code>systemd-resolved</code>. Шифрует весь DNS через TLS (порт 853):\n\n"

        "<code>sudo mkdir -p /etc/systemd/resolved.conf.d && sudo tee /etc/systemd/resolved.conf.d/magicdns.conf << 'EOF'\n"

        "[Resolve]\n"

        "DNS=109.120.177.170#api.magicdns.ru 45.88.163.92#api.magicdns.ru\n"

        "FallbackDNS=1.1.1.1 8.8.8.8\n"

        "DNSOverTLS=yes\n"

        "EOF\n"

        "sudo systemctl restart systemd-resolved</code>\n\n"

        "• <b>Проверка работы:</b> <code>resolvectl status</code>\n\n"

        "• <b>Как отключить:</b>\n"

        "<code>sudo rm -f /etc/systemd/resolved.conf.d/magicdns.conf && sudo systemctl restart systemd-resolved</code>"

    )


def get_faq_linux_kb():

    return {

        "inline_keyboard": [

            [{"text": "🌐 Открыть инструкцию на сайте", "url": "https://magicdns.ru/#setup"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

        ]

    }



def get_faq_friends_card():

    return (

        "🤝 <b>Дружественные проекты и независимое комьюнити</b>\n\n"

        "Мы за свободный интернет, чистую скорость и взаимовыручку среди независимых разработчиков!\n\n"

        "Если вам нужен надёжный резервный Smart DNS или доступ к дополнительным сервисам (Twitch, Strava, Linguee) — искренне рекомендуем проект наших братишек:\n\n"

        "🌐 <b>Dagami DNS</b>\n"

        "• <b>Сайт:</b> https://dns.dagami.ru\n"

        "• <b>Чат сообщества:</b> @dagamvi\n"

        "• <b>Канал новостей:</b> @dagamivibe\n\n"

        "Ребята тоже развивают бесплатный Smart DNS для людей без навязчивой рекламы и платных тарифов, с собственными подписанными Apple-профилями. Добавьте в закладки про запас!"

    )



def get_faq_friends_kb():

    return {

        "inline_keyboard": [

            [{"text": "🌐 Перейти на dns.dagami.ru", "url": "https://dns.dagami.ru/"}],

            [{"text": "💬 Чат @dagamvi", "url": "https://t.me/dagamvi"}, {"text": "📢 Канал @dagamivibe", "url": "https://t.me/dagamivibe"}],

            [{"text": "⬅️ Назад в меню FAQ", "callback_data": "faq_menu"}, {"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

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

            [{"text": "🚦 Статусы серверов (перебои)", "callback_data": "admin_srv_status"}],

            [{"text": "🧪 Экспресс-тест доступности ИИ", "callback_data": "admin_test_ai"}, {"text": "🔍 DNS-диагностика /dig", "callback_data": "admin_dig_info"}],

            [{"text": "🌐 Баннер на сайте", "callback_data": "admin_sitealert_info"}, {"text": "🚨 Рассылка", "callback_data": "admin_alert_info"}],

            [{"text": "📊 Статистика подписчиков", "callback_data": "cmd_users"}, {"text": "🟢 Проверить /status", "callback_data": "cmd_status"}],

            [{"text": "🤝 Друзья (Dagami DNS)", "callback_data": "faq_friends"}, {"text": "⚡ Параметры DNS", "callback_data": "cmd_dns"}]

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

                [{"text": btn_label, "callback_data": f"reply_rev_{r.get('id')}"}],

                [{"text": "🗑 Удалить этот отзыв с сайта", "callback_data": f"del_ask_{r.get('id')}"}]

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



def delete_review_on_github(review_id):

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



    initial_len = len(reviews)

    reviews = [r for r in reviews if str(r.get('id', '')) != str(review_id)]

    if len(reviews) == initial_len:

        return False, f"Отзыв с ID {review_id} не найден."



    new_content_str = json.dumps(reviews, ensure_ascii=False, indent=2)

    new_content_b64 = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')



    update_payload = {

        "message": f"fix(reviews): delete review {review_id} via admin TG bot",

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

            try:

                local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.json")

                with open(local_p, 'w', encoding='utf-8') as lf:

                    lf.write(new_content_str)

            except Exception:

                pass

            return True, "Отзыв успешно удалён из reviews.json на сайте!"

    except Exception as e:

        return False, f"Ошибка удаления на GitHub: {e}"





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



def set_site_alert(active, message="", alert_type="warning"):

    alert_data = {

        "active": active,

        "type": alert_type if active else "info",

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



def sync_servers_to_site(statuses=None):

    """

    Automatically syncs server health state to magicdns.ru via alert.json.

    - If all servers are OK: clears alert banner on the site.

    - If Sweden or Germany is degraded/down: sets prominent alert advising the healthy node.

    """

    try:

        if statuses is None:

            statuses = load_servers_status()

        se_st = statuses.get('se', {}).get('status', 'ok')

        de_st = statuses.get('de', {}).get('status', 'ok')



        if se_st == 'ok' and de_st == 'ok':

            ok, msg = set_site_alert(False, "")

            print(f"[SYNC SITE] Cleared site alert (all nodes OK): {ok} {msg}")

            return ok, msg



        if se_st in ('degraded', 'down') and de_st == 'ok':

            if se_st == 'down':

                alert_text = "<b>Основной сервер MagicDNS (Франкфурт) временно на техобслуживании.</b> Рекомендуем переключиться на резерв: <code>45.88.163.92</code>"

            else:

                alert_text = "<b>На основном сервере (Франкфурт) возможны задержки.</b> Рекомендуем переключиться на резерв: <code>45.88.163.92</code>"

            ok, msg = set_site_alert(True, alert_text)

            print(f"[SYNC SITE] Set site alert for Sweden ({se_st}): {ok} {msg}")

            return ok, msg



        if de_st in ('degraded', 'down') and se_st == 'ok':

            if de_st == 'down':

                alert_text = "<b>Резервный сервер в Германии временно на техобслуживании.</b> Основной узел <code>109.120.177.170</code> работает штатно."

            else:

                alert_text = "<b>На резервном сервере в Германии возможны задержки.</b> Рекомендуем использовать основной узел (Франкфурт): <code>109.120.177.170</code>"

            ok, msg = set_site_alert(True, alert_text)

            print(f"[SYNC SITE] Set site alert for Germany ({de_st}): {ok} {msg}")

            return ok, msg



        # Both degraded / down

        alert_text = "<b>Ведутся технические работы по обновлению инфраструктуры.</b> Возможны задержки при подключении. Мы уже восстанавливаем штатную работу!"

        ok, msg = set_site_alert(True, alert_text)

        print(f"[SYNC SITE] Set site alert for both nodes down/degraded: {ok} {msg}")

        return ok, msg

    except Exception as e:

        print(f"[SYNC SITE ERR] {e}")

        return False, str(e)





def run_ai_diagnostics():

    """

    Probes key AI platforms (Gemini, AI Studio, OpenAI, Claude, Copilot)

    directly through the Sweden core node (10.10.0.1 via WireGuard) or locally.

    Detects 302 captcha redirects and Cloudflare blocks.

    """

    targets = [

        ("Google Gemini", "https://gemini.google.com/"),

        ("Google AI Studio", "https://aistudio.google.com/welcome"),

        ("OpenAI (ChatGPT)", "https://api.openai.com/v1/models"),

        ("Anthropic Claude", "https://api.anthropic.com/v1/messages"),

        ("Microsoft Copilot", "https://copilot.microsoft.com/"),

    ]



    remote_code = """

import urllib.request, time, ssl

ctx = ssl.create_default_context()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}

class NoRedirect(urllib.request.HTTPRedirectHandler):

    def redirect_request(self, req, fp, code, msg, headers, newurl):

        return None

opener = urllib.request.build_opener(NoRedirect)

targets = [

    ('Google Gemini', 'https://gemini.google.com/'),

    ('Google AI Studio', 'https://aistudio.google.com/welcome'),

    ('OpenAI (ChatGPT)', 'https://api.openai.com/v1/models'),

    ('Anthropic Claude', 'https://api.anthropic.com/v1/messages'),

    ('Microsoft Copilot', 'https://copilot.microsoft.com/'),

]

for name, url in targets:

    t0 = time.time()

    code = 0

    note = ''

    try:

        req = urllib.request.Request(url, headers=headers)

        resp = opener.open(req, timeout=5)

        code = resp.status

        note = 'OK'

    except urllib.error.HTTPError as e:

        code = e.code

        loc = e.headers.get('Location', '')

        if 'sorry' in loc or 'recaptcha' in loc:

            note = 'Капча Google'

        elif code in (401, 405):

            note = 'Доступен'

        elif code == 403:

            note = 'Cloudflare 403'

        else:

            note = f'HTTP {code}'

    except Exception as e:

        note = 'Сбой'

    lat = int((time.time() - t0) * 1000)

    print(f'{name}|{code}|{lat}|{note}')

"""

    results = []

    node_label = "🇩🇪 Франкфурт (Core Node — 109.120.177.170)"

    tested_remote = False



    try:

        p = subprocess.run(

            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=4", "10.10.0.1", "python3", "-"],

            input=remote_code,

            capture_output=True,

            text=True,

            timeout=10

        )

        output = p.stdout.strip()

        if output and '|' in output:

            for line in output.splitlines():

                parts = line.split('|')

                if len(parts) >= 4:

                    results.append({

                        'name': parts[0],

                        'code': parts[1],

                        'latency': int(parts[2]),

                        'note': parts[3],

                        'is_ok': parts[3] in ('OK', 'Доступен')

                    })

            tested_remote = True

    except Exception:

        pass



    if not tested_remote or not results:

        node_label = "📍 Локальный узел мониторинга"

        results = []

        headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

        }

        class NoRedirect(urllib.request.HTTPRedirectHandler):

            def redirect_request(self, req, fp, code, msg, headers, newurl):

                return None

        opener = urllib.request.build_opener(NoRedirect)



        for name, url in targets:

            t0 = time.time()

            code = 0

            note = ''

            try:

                req = urllib.request.Request(url, headers=headers)

                resp = opener.open(req, timeout=5)

                code = resp.status

                note = 'OK'

            except urllib.error.HTTPError as e:

                code = e.code

                loc = e.headers.get('Location', '')

                if 'sorry' in loc or 'recaptcha' in loc:

                    note = 'Капча Google'

                elif code in (401, 405):

                    note = 'Доступен'

                elif code == 403:

                    note = 'Cloudflare 403'

                else:

                    note = f'HTTP {code}'

            except Exception:

                note = 'Сбой'

            lat = int((time.time() - t0) * 1000)

            results.append({

                'name': name,

                'code': str(code),

                'latency': lat,

                'note': note,

                'is_ok': note in ('OK', 'Доступен')

            })



    lines = [

        "🧪 <b>Результаты экспресс-теста доступности ИИ:</b>",

        f"📍 <i>Узел проверки: {node_label}</i>\n"

    ]



    all_ok = True

    for r in results:

        if r['is_ok']:

            icon = "🟢"

            badge = f"штатно ({r['code']}, {r['latency']} мс)"

        else:

            all_ok = False

            icon = "🔴" if "Капча" in r['note'] or "Сбой" in r['note'] else "🟡"

            badge = f"<b>{r['note']}</b> ({r['code']}, {r['latency']} мс)"

        lines.append(f"{icon} <b>{r['name']}:</b> {badge}")



    now_str = datetime.now().strftime("%d.%m.%Y %H:%M MSK")

    lines.append("")

    if all_ok:

        lines.append("⚡️ <b>Сводка:</b> Все проверенные ИИ-сервисы доступны на полной скорости без блокировок и капчи.")

    else:

        lines.append("⚠️ <b>Сводка:</b> На некоторых сервисах обнаружены задержки или ограничения. Рекомендуется проверить статус серверов.")

    lines.append(f"🕐 <i>Время проверки: {now_str}</i>")



    return "\n".join(lines)





def get_ai_diagnostics_kb():

    return {

        "inline_keyboard": [

            [{"text": "🔄 Повторить проверку", "callback_data": "admin_test_ai"}],

            [{"text": "🖥 Статус серверов", "callback_data": "admin_srv_status"}, {"text": "« В админ-панель", "callback_data": "admin_panel"}]

        ]

    }



def sign_mobileconfig(xml_bytes):

    """Signs Apple .mobileconfig XML using OpenSSL in CMS/PKCS#7 format."""

    cert_path = "/etc/letsencrypt/live/api.magicdns.ru/cert.pem"

    key_path = "/etc/letsencrypt/live/api.magicdns.ru/privkey.pem"

    chain_path = "/etc/letsencrypt/live/api.magicdns.ru/chain.pem"



    if not (os.path.exists(cert_path) and os.path.exists(key_path) and os.path.exists(chain_path)):

        cert_path = "/etc/letsencrypt/live/dns.magicdns.ru/cert.pem"

        key_path = "/etc/letsencrypt/live/dns.magicdns.ru/privkey.pem"

        chain_path = "/etc/letsencrypt/live/dns.magicdns.ru/chain.pem"



    if os.path.exists(cert_path) and os.path.exists(key_path) and os.path.exists(chain_path):

        cmd = [

            "openssl", "cms", "-sign",

            "-signer", cert_path,

            "-inkey", key_path,

            "-certfile", chain_path,

            "-outform", "der",

            "-nodetach"

        ]

        try:

            res = subprocess.run(cmd, input=xml_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

            if res.returncode == 0 and len(res.stdout) > 0:

                print(f"[SIGN PROFILE] Successfully signed mobileconfig via CMS/PKCS#7 ({len(res.stdout)} bytes)")

                return res.stdout

            else:

                err_msg = res.stderr.decode('utf-8', errors='replace')

                print(f"[SIGN PROFILE ERROR] openssl failed (code {res.returncode}): {err_msg}")

        except Exception as e:

            print(f"[SIGN PROFILE EXCEPTION] {e}")

    return None





def generate_mobileconfig(variant="dual"):
    """Generates a valid Apple mobileconfig XML for iOS/macOS DoH with System Scope and RFC 8484 compliance."""
    import uuid
    if variant == "se":
        servers = ["109.120.177.170"]
        name = "MagicDNS (Франкфурт)"
        desc = "Основной немецкий узел MagicDNS DoH"
    elif variant == "de":
        servers = ["45.88.163.92"]
        name = "MagicDNS (Германия)"
        desc = "Резервный немецкий узел MagicDNS DoH"
    else:
        servers = ["109.120.177.170", "45.88.163.92"]
        name = "MagicDNS (Двойной узел)"
        desc = "Двойной узел MagicDNS с автопереключением"

    server_tags = "\n".join([f"                    <string>{s}</string>" for s in servers])
    payload_uuid = str(uuid.uuid4())
    top_uuid = str(uuid.uuid4())

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>DNSSettings</key>
            <dict>
                <key>DNSProtocol</key>
                <string>HTTPS</string>
                <key>ServerAddresses</key>
                <array>
{server_tags}
                </array>
                <key>ServerURL</key>
                <string>https://api.magicdns.ru/dns-query</string>
            </dict>
            <key>PayloadDescription</key>
            <string>{desc}</string>
            <key>PayloadDisplayName</key>
            <string>{name}</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.dnsSettings.managed.{payload_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.dnsSettings.managed</string>
            <key>PayloadUUID</key>
            <string>{payload_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDescription</key>
    <string>Шифрованный DNS MagicDNS (DoH) для доступа к Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT без сторонних приложений.</string>
    <key>PayloadDisplayName</key>
    <string>{name}</string>
    <key>PayloadIdentifier</key>
    <string>ru.magicdns.profile.{variant}</string>
    <key>PayloadOrganization</key>
    <string>MagicDNS</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{top_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>"""
    xml_bytes = xml.encode('utf-8')
    signed = sign_mobileconfig(xml_bytes)
    if signed:
        return signed
    return xml_bytes

def get_ios_picker_card():

    return (

        "🍏 <b>Конфигурационные профили для iPhone и iPad:</b>\n\n"

        "Выберите подходящий вариант профиля:\n\n"

        "• <b>Швеция + Германия (Рекомендуется):</b>\n"

        "Основной шведский узел с автоматическим переключением на Германию при любых перебоях.\n\n"

        "• <b>Только Швеция (Core):</b>\n"

        "Прямой маршрут на Стокгольм без резервирования.\n\n"

        "• <b>Только Германия (Backup):</b>\n"

        "Специальный профиль на Франкфурт (если ваш мобильный оператор сбоит на шведских подсетях)."

    )





def get_ios_picker_kb():

    return {

        "inline_keyboard": [

            [{"text": "🍏 Скачать: Швеция + Германия (Рекомендуется)", "callback_data": "dl_ios_dual"}],

            [{"text": "🇸🇪 Скачать: Только Швеция", "callback_data": "dl_ios_se"}],

            [{"text": "🇩🇪 Скачать: Только Германия", "callback_data": "dl_ios_de"}],

            [{"text": "⚡ Параметры других платформ", "callback_data": "cmd_dns"}]

        ]

    }



def get_check_card():
    return (
        "🔍 <b>Экспресс-проверка подключения MagicDNS</b>\n\n"
        "⚠️ <b>ВАЖНО:</b> Перед проверкой обязательно <b>выключите любой VPN</b> на вашем устройстве.\n\n"
        "MagicDNS работает напрямую без VPN. Если VPN включен, проверка покажет трафик чужого туннеля, а не нашего DNS.\n\n"
        "Нажмите кнопку ниже, чтобы запустить радар доступности нейросетей (Gemini, Claude, ChatGPT) и детектор чистого подключения:"
    )


def get_check_kb():
    return {
        "inline_keyboard": [
            [{"text": "⚡ Запустить проверку подключения", "web_app": {"url": "https://magicdns.ru/check.html"}}],
            [{"text": "🤖 Настройка Android", "callback_data": "cmd_android"}, {"text": "🍏 Профиль iOS", "callback_data": "cmd_ios"}],
            [{"text": "⚡ Все параметры DNS", "callback_data": "cmd_dns"}]
        ]
    }


def get_routers_picker_card():
    return (
        "📡 <b>Настройка MagicDNS на роутере (Wi-Fi для всех устройств)</b>\n\n"
        "При настройке роутера все устройства в домашней сети (компьютеры, ноутбуки, Smart TV, смартфоны, планшеты) "
        "получают доступ к нейросетям автоматически без установки сторонних программ.\n\n"
        "⚠️ <i>Обычный порт 53 (UDP) может перехватываться провайдером. Рекомендуется использовать DoT или DoH.</i>\n\n"
        "<b>Выберите модель вашего роутера:</b>"
    )


def get_routers_picker_kb():
    return {
        "inline_keyboard": [
            [{"text": "📡 Keenetic (DoT / DoH)", "callback_data": "router_keenetic"}, {"text": "📡 MikroTik (RouterOS DoH)", "callback_data": "router_mikrotik"}],
            [{"text": "📡 OpenWrt (DoT / Https-dns)", "callback_data": "router_openwrt"}, {"text": "📡 TP-Link / Asus / Обычные", "callback_data": "router_generic"}],
            [{"text": "🔍 Проверить подключение", "web_app": {"url": "https://magicdns.ru/check.html"}}],
            [{"text": "⚡ Все параметры DNS", "callback_data": "cmd_dns"}, {"text": "❓ Частые вопросы (FAQ)", "callback_data": "faq_menu"}]
        ]
    }


def get_router_brand_kb():
    return {
        "inline_keyboard": [
            [{"text": "🔍 Проверить подключение", "web_app": {"url": "https://magicdns.ru/check.html"}}],
            [{"text": "🔙 К выбору других роутеров", "callback_data": "cmd_routers"}],
            [{"text": "⚡ Все параметры DNS", "callback_data": "cmd_dns"}, {"text": "❓ Частые вопросы (FAQ)", "callback_data": "faq_menu"}]
        ]
    }


def get_router_keenetic_card():
    return (
        "📡 <b>Настройка Keenetic (DNS-over-TLS)</b>\n\n"
        "Keenetic поддерживает защищенный протокол DoT из коробки.\n\n"
        "1️⃣ Откройте панель роутера (<code>192.168.1.1</code> или <code>my.keenetic.net</code>).\n"
        "2️⃣ Перейдите: <b>Сетевые правила</b> ➔ <b>Интернет-фильтр</b> (или <b>DNS</b>).\n"
        "3️⃣ Нажмите <b>«Добавить сервер»</b>.\n"
        "4️⃣ Заполните поля:\n"
        "• <b>IP-адрес DNS-сервера:</b>\n"
        "<code>109.120.177.170</code>\n"
        "• <b>Доменное имя TLS (SNI):</b>\n"
        "<code>api.magicdns.ru</code>\n"
        "• <b>Протокол:</b> DNS-over-TLS (DoT)\n\n"
        "5️⃣ <i>(Опционально резерв):</i> добавьте второй сервер с IP <code>45.88.163.92</code> и тем же именем TLS <code>api.magicdns.ru</code>.\n"
        "6️⃣ Нажмите <b>Сохранить</b>.\n\n"
        "💡 <i>Весь домашний Wi-Fi теперь защищен и открывает нейросети на максимальной скорости.</i>"
    )


def get_router_mikrotik_card():
    return (
        "📡 <b>Настройка MikroTik (RouterOS DoH)</b>\n\n"
        "В RouterOS 6.47+ и 7.x поддерживается шифрованный DoH.\n\n"
        "1️⃣ Откройте <b>WinBox</b> или SSH-терминал роутера.\n"
        "2️⃣ Откройте <b>New Terminal</b> и выполните одну команду:\n\n"
        "<code>/ip dns set use-doh-server=\"https://api.magicdns.ru/dns-query\" verify-doh-cert=yes</code>\n\n"
        "3️⃣ Убедитесь, что в <code>/ip dns</code> прописан хотя бы один обычный временный DNS (например, <code>77.88.8.8</code>), чтобы MikroTik мог впервые разрешить имя DoH-хоста.\n"
        "4️⃣ Очистите кэш DNS:\n"
        "<code>/ip dns cache flush</code>\n\n"
        "💡 <i>Проверить статус: <code>/ip dns print</code> — в строке DoH Server должен отображаться адрес MagicDNS.</i>"
    )


def get_router_openwrt_card():
    return (
        "📡 <b>Настройка OpenWrt</b>\n\n"
        "<b>Вариант 1: Через веб-интерфейс LuCI (Стандартный DNS)</b>\n"
        "1️⃣ Перейдите: <b>Network</b> ➔ <b>Interfaces</b> ➔ <b>WAN</b> ➔ <b>Edit</b>.\n"
        "2️⃣ В <b>Advanced Settings</b> снимите галочку <i>«Use DNS servers advertised by peer»</i>.\n"
        "3️⃣ В поле <b>Custom DNS servers</b> введите:\n"
        "<code>109.120.177.170</code>\n"
        "<code>45.88.163.92</code>\n"
        "4️⃣ Нажмите <b>Save & Apply</b>.\n\n"
        "<b>Вариант 2: Защищенный DoH (через пакет https-dns-proxy)</b>\n"
        "В терминале OpenWrt:\n"
        "<code>opkg update && opkg install https-dns-proxy</code>\n"
        "Укажите bootstrap DNS и URL:\n"
        "<code>uci set https-dns-proxy.main.url='https://api.magicdns.ru/dns-query'</code>\n"
        "<code>uci commit https-dns-proxy && /etc/init.d/https-dns-proxy restart</code>"
    )


def get_router_generic_card():
    return (
        "📡 <b>Настройка TP-Link / Asus / D-Link / Xiaomi Router</b>\n\n"
        "1️⃣ Зайдите в панель роутера (обычно <code>192.168.0.1</code> или <code>192.168.1.1</code>).\n"
        "2️⃣ Перейдите в раздел <b>Сеть</b> (Network / WAN) ➔ <b>Интернет</b> (или <b>DHCP-сервер</b>).\n"
        "3️⃣ Найдите пункт <b>DNS-серверы</b> (Primary / Secondary DNS).\n"
        "4️⃣ Переключите режим с «Автоматически» на «Вручную» и введите:\n"
        "• Основной DNS (Франкфурт): <code>109.120.177.170</code>\n"
        "• Дополнительный DNS (Финляндия): <code>45.88.163.92</code>\n\n"
        "5️⃣ Сохраните настройки и перезагрузите роутер.\n\n"
        "💡 <i>Если после настройки провайдер блокирует порт 53, используйте роутеры с поддержкой DoT (Keenetic) или DoH на самих клиентах.</i>"
    )
def get_android_picker_card():
    return (
        "🤖 <b>Мастер настройки MagicDNS на Android</b>\n\n"
        "Начиная с Android 9 (Pie), в систему встроен современный протокол <b>DNS-over-TLS (DoT)</b>. "
        "Никаких сторонних приложений или сертификатов не требуется — всё настраивается за 1 минуту штатно в настройках смартфона.\n\n"
        "<b>Выберите вашу марку смартфона или оболочку:</b>"
    )


def get_android_picker_kb():
    return {
        "inline_keyboard": [
            [{"text": "📱 Samsung (One UI)", "callback_data": "android_samsung"}, {"text": "📱 Xiaomi / POCO / Redmi", "callback_data": "android_xiaomi"}],
            [{"text": "📱 Realme / OnePlus / OPPO", "callback_data": "android_bbk"}, {"text": "📱 Huawei / Honor", "callback_data": "android_huawei"}],
            [{"text": "📱 Google Pixel / Чистый Android", "callback_data": "android_pixel"}],
            [{"text": "⚡ Параметры всех платформ", "callback_data": "cmd_dns"}, {"text": "❓ Ошибка подключения", "callback_data": "faq_android"}]
        ]
    }


def get_android_brand_kb():
    return {
        "inline_keyboard": [
            [{"text": "🔍 Проверить подключение", "web_app": {"url": "https://magicdns.ru/check.html"}}],
            [{"text": "🔙 К выбору других марок", "callback_data": "cmd_android"}],
            [{"text": "⚡ Все параметры DNS", "callback_data": "cmd_dns"}, {"text": "❓ Ошибка подключения", "callback_data": "faq_android"}]
        ]
    }


def get_android_samsung_card():
    return (
        "📱 <b>Настройка на Samsung (One UI)</b>\n\n"
        "1️⃣ Откройте <b>Настройки</b> смартфона.\n"
        "2️⃣ Перейдите: <b>Подключения</b> ➔ <b>Другие настройки подключения</b>.\n"
        "3️⃣ Нажмите на пункт <b>«Персональный DNS-сервер»</b>.\n"
        "4️⃣ Выберите вариант <b>«Имя хоста поставщика персонального DNS-сервера»</b>.\n"
        "5️⃣ Вставьте имя сервера:\n"
        "<code>api.magicdns.ru</code>\n"
        "<i>(нажмите на адрес выше, чтобы скопировать)</i>\n\n"
        "6️⃣ Нажмите <b>Сохранить</b>.\n\n"
        "💡 <i>Если пишет «Не удается подключиться», убедитесь, что вставили строго адрес без пробелов и без https://.</i>"
    )


def get_android_xiaomi_card():
    return (
        "📱 <b>Настройка на Xiaomi / POCO / Redmi (MIUI & HyperOS)</b>\n\n"
        "1️⃣ Откройте <b>Настройки</b> устройства.\n"
        "2️⃣ Перейдите в раздел <b>Подключение и общий доступ</b>.\n"
        "3️⃣ Нажмите на пункт <b>«Частный DNS-сервер»</b> (в HyperOS — «Персональный DNS»).\n"
        "4️⃣ Выберите <b>«Имя хоста провайдера частного DNS»</b>.\n"
        "5️⃣ Вставьте имя сервера:\n"
        "<code>api.magicdns.ru</code>\n"
        "<i>(нажмите на адрес выше, чтобы скопировать)</i>\n\n"
        "6️⃣ Нажмите <b>Сохранить</b>.\n\n"
        "💡 <i>После сохранения статус под пунктом должен стать «Подключено» или отображать api.magicdns.ru.</i>"
    )


def get_android_bbk_card():
    return (
        "📱 <b>Настройка на Realme / OnePlus / OPPO (ColorOS & Realme UI)</b>\n\n"
        "1️⃣ Откройте <b>Настройки</b> смартфона.\n"
        "2️⃣ Перейдите: <b>Подключение и общий доступ</b> ➔ <b>Частный DNS</b>.\n"
        "3️⃣ Выберите режим <b>«Заданный частный DNS»</b> (или «Имя хоста поставщика частного DNS»).\n"
        "4️⃣ Вставьте адрес:\n"
        "<code>api.magicdns.ru</code>\n"
        "<i>(нажмите на адрес выше, чтобы скопировать)</i>\n\n"
        "5️⃣ Нажмите галочку <b>Сохранить</b> в правом верхнем углу."
    )


def get_android_huawei_card():
    return (
        "📱 <b>Настройка на Huawei / Honor (EMUI & MagicOS)</b>\n\n"
        "1️⃣ Откройте <b>Настройки</b>.\n"
        "2️⃣ Перейдите: <b>Другие соединения</b> ➔ <b>Частный DNS</b> (или «Мобильная сеть» ➔ «Частный DNS»).\n"
        "3️⃣ Выберите пункт <b>«Настроить частный DNS»</b>.\n"
        "4️⃣ Введите имя хоста:\n"
        "<code>api.magicdns.ru</code>\n"
        "<i>(нажмите на адрес выше, чтобы скопировать)</i>\n\n"
        "5️⃣ Нажмите галочку <b>Сохранить</b>."
    )


def get_android_pixel_card():
    return (
        "📱 <b>Настройка на Google Pixel и чистом Android</b>\n\n"
        "<i>(Подходит также для Motorola, Sony Xperia, Nothing OS и других)</i>\n\n"
        "1️⃣ Откройте <b>Настройки</b> телефона.\n"
        "2️⃣ Перейдите в раздел <b>Сеть и интернет</b>.\n"
        "3️⃣ Прокрутите вниз и нажмите <b>«Частный DNS-сервер»</b> (Private DNS).\n"
        "4️⃣ Выберите <b>«Имя хоста поставщика частного DNS-сервера»</b>.\n"
        "5️⃣ Вставьте имя:\n"
        "<code>api.magicdns.ru</code>\n"
        "<i>(нажмите на адрес выше, чтобы скопировать)</i>\n\n"
        "6️⃣ Нажмите <b>Сохранить</b>."
    )






def run_dig_diagnostics(domain):

    """

    Performs live DNS resolution of a target domain across Sweden, Germany, and Cloudflare upstream.

    Determines if domain is proxied through Smart DNS or directly resolved.

    """

    clean_domain = domain.strip().lower()

    clean_domain = re.sub(r'^https?://', '', clean_domain)

    clean_domain = clean_domain.split('/')[0].split(':')[0].strip()



    if not clean_domain or not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$', clean_domain):

        return (

            f"⚠️ <b>Некорректный домен:</b> <code>{html.escape(domain)}</code>\n\n"

            "Пример правильной команды:\n"

            "<code>/dig cursor.com</code>\n"

            "<code>/dig claude.ai</code>"

        ), None



    servers = [

        ("🇩🇪 Франкфурт (Core Node)", "109.120.177.170"),

        ("🇩🇪 Второй узел (Backup)", "45.88.163.92"),

        ("🌐 Cloudflare (Upstream)", "1.1.1.1")

    ]



    report_lines = [

        f"🔍 <b>DNS-диагностика домена:</b> <code>{clean_domain}</code>\n"

    ]



    for s_name, s_ip in servers:

        t0 = time.time()

        res_ips = []

        try:

            p = subprocess.run(

                ["dig", "+short", "+time=2", f"@{s_ip}", clean_domain],

                capture_output=True,

                text=True,

                timeout=4

            )

            raw_out = p.stdout.strip()

            if raw_out:

                lines = [line.strip() for line in raw_out.splitlines() if line.strip() and not line.startswith(';')]

                res_ips = lines

        except Exception:

            try:

                ai = socket.getaddrinfo(clean_domain, None)

                res_ips = list(set([sockaddr[0] for family, type, proto, canonname, sockaddr in ai if family == socket.AF_INET]))

            except Exception:

                res_ips = []



        lat = int((time.time() - t0) * 1000)



        if res_ips:

            is_proxied = any(ip in ("109.120.177.170", "45.88.163.92", "94.249.177.102", "109.120.132.43", "138.124.59.86") for ip in res_ips)

            ips_str = ", ".join(res_ips[:3])

            if is_proxied:

                status_icon = "🟢"

                route_desc = "Маршрутизируется через Smart DNS шлюз"

            else:

                status_icon = "⚪"

                route_desc = "Прямой резолв (проксирование не требуется)"



            report_lines.append(

                f"{s_name}:\n"

                f"• IP: <code>{ips_str}</code> ({lat} мс)\n"

                f"• Статус: {status_icon} <i>{route_desc}</i>\n"

            )

        else:

            report_lines.append(

                f"{s_name}:\n"

                f"• Статус: 🔴 <i>Нет ответа / NXDOMAIN</i> ({lat} мс)\n"

            )



    report_lines.append(f"🕐 <i>Проверено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S MSK')}</i>")

    return "\n".join(report_lines), clean_domain





def get_dig_kb(clean_domain):

    return {

        "inline_keyboard": [

            [{"text": f"🔄 Перепроверить {clean_domain}", "callback_data": f"dig_re_{clean_domain}"}],

            [{"text": "🧪 Экспресс-тест ИИ", "callback_data": "admin_test_ai"}, {"text": "« В админку", "callback_data": "admin_panel"}]

        ]

    }







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



                if review_type in ('vote', 'wishlist_vote'):

                    service_id = data.get('service_id', 'unknown')

                    print(f'[VOTE] Wishlist vote received for {service_id}')

                    self.send_response(200)

                    self.send_header('Content-Type', 'application/json')

                    self.send_header('Access-Control-Allow-Origin', '*')

                    self.end_headers()

                    self.wfile.write(json.dumps({'ok': True, 'message': 'Голос принят'}).encode('utf-8'))

                    return



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



                if review_type == 'wishlist':

                    service_title = data.get('service_title', '').strip() or 'Новый сервис'

                    domain = data.get('domain', '').strip() or 'Не указан'

                    category = data.get('category', 'Игра / Сервис')

                    contact = data.get('contact', '').strip() or esc_author

                    esc_title = html.escape(str(service_title))

                    esc_domain = html.escape(str(domain))

                    esc_category = html.escape(str(category))

                    esc_contact = html.escape(str(contact))

                    tg_msg = (

                        f"💡 <b>НОВАЯ ЗАЯВКА В ВИШЛИСТ С САЙТА! #ВИШЛИСТ</b>\n\n"

                        f"🎮 <b>Сервис / Игра:</b> {esc_title}\n"

                        f"📁 <b>Категория:</b> {esc_category}\n"

                        f"🌐 <b>Домен:</b> <code>{esc_domain}</code>\n"

                        f"👤 <b>Контакт:</b> {esc_contact}\n\n"

                        f"💬 <b>Причина / Ошибка:</b>\n{esc_message}\n\n"

                        f"🛡️ <i>Требуется проверка на РКН (149-ФЗ) и модерация перед публикацией для голосования.</i>"

                    )

                    send_message(ADMIN_CHAT_ID, tg_msg)

                elif review_type in ('idea', 'suggestion'):

                    contact = data.get('contact', '').strip() or esc_author

                    esc_contact = html.escape(str(contact))

                    tg_msg = (

                        f"💡 <b>НОВОЕ ПРЕДЛОЖЕНИЕ / ИДЕЯ ДЛЯ MAGICDNS! #ИДЕЯ</b>\n\n"

                        f"👤 <b>От:</b> {esc_contact}\n"

                        f"💻 <b>Платформа:</b> {esc_platform}\n\n"

                        f"💬 <b>Текст идеи:</b>\n{esc_message}"

                    )

                    send_message(ADMIN_CHAT_ID, tg_msg)

                elif review_type == 'bug':

                    contact = data.get('contact', '').strip() or esc_author

                    esc_contact = html.escape(str(contact))

                    tg_msg = (

                        f"🐛 <b>БАГ-РЕПОРТ С САЙТА! #БАГ</b>\n\n"

                        f"💻 <b>Платформа:</b> {esc_platform}\n"

                        f"👤 <b>Контакт:</b> {esc_contact}\n\n"

                        f"💬 <b>Описание проблемы:</b>\n{esc_message}"

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



    def handle_update(u):

        try:

            for _ in (1,):




                # 1. Handle Inline Button Clicks

                if 'callback_query' in u:

                    cq = u['callback_query']

                    cq_id = cq['id']

                    from_id = cq.get('from', {}).get('id')

                    data = cq.get('data', '')

                    msg = cq.get('message', {})

                    msg_id = msg.get('message_id')

                    msg_text = msg.get('text', '')

                    chat_id = msg.get('chat', {}).get('id', from_id)



                    print(f"[CALLBACK] {data} from user {from_id}")

                    from_user = cq.get('from', {})

                    register_subscriber(from_id, from_user.get('first_name'), from_user.get('username'))



                    # Public callback queries (Available for ALL users)

                    if data == 'cmd_rules':
                        answer_callback(cq_id, "📋 Правила сообщества")
                        res = edit_message(chat_id, msg_id, get_group_rules_card(), reply_markup=get_group_rules_kb())
                        if not res.get("ok"):
                            send_message(chat_id, get_group_rules_card(), reply_markup=get_group_rules_kb())
                        continue

                    if data == 'cmd_dns':

                        answer_callback(cq_id, "⚡ Параметры MagicDNS")

                        res = edit_message(chat_id, msg_id, get_dns_card(), reply_markup=get_dns_kb())

                        if not res.get("ok"):

                            send_message(chat_id, get_dns_card(), reply_markup=get_dns_kb())

                        continue



                    if data == 'cmd_status':

                        answer_callback(cq_id, "🟢 Статус серверов")

                        is_adm = (from_id == ADMIN_CHAT_ID)

                        res = edit_message(chat_id, msg_id, get_status_card(is_admin=is_adm), reply_markup=get_status_kb(is_admin=is_adm))

                        if not res.get("ok"):

                            send_message(chat_id, get_status_card(is_admin=is_adm), reply_markup=get_status_kb(is_admin=is_adm))

                        continue



                    # Group Captcha Callback (Isolated to groups)
                    if data.startswith('captcha_pass:'):
                        try:
                            target_uid = int(data.split(':', 1)[1])
                        except Exception:
                            target_uid = 0

                        if from_id != target_uid:
                            answer_callback(cq_id, "⚠️ Это проверка для другого участника", alert=True)
                            continue

                        # Unrestrict verified member
                        restrict_chat_member(chat_id, from_id, can_send_messages=True)
                        answer_callback(cq_id, "✅ Проверка пройдена! Добро пожаловать.")
                        delete_message(chat_id, msg_id)
                        PENDING_GROUP_CAPTCHAS.pop(f"{chat_id}_{from_id}", None)
                        continue

                    if data == 'community_chat':
                        answer_callback(cq_id)
                        chat_placeholder = (
                            "💬 <b>Официальный чат сообщества MagicDNS</b>\n\n"
                            "Группа взаимопомощи и общения пользователей запускается прямо сейчас!\n\n"
                            "Здесь можно будет:\n"
                            "• Задать вопрос по настройке любой модели телефона или роутера\n"
                            "• Обсуждать работу нейросетей и делиться промптами\n"
                            "• Получать оперативную помощь от модераторов и инженеров\n\n"
                            "🔔 <i>Как только группа откроется, ссылка сразу станет активной прямо в этой кнопке.</i>"
                        )
                        kb = {
                            "inline_keyboard": [
                                [{"text": "✈️ Поделиться с другом", "url": SHARE_URL}],
                                [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]
                            ]
                        }
                        edit_message(chat_id, msg_id, chat_placeholder, reply_markup=kb)
                        continue

                    if data == 'cmd_routers':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_routers_picker_card(), reply_markup=get_routers_picker_kb())
                        continue

                    if data == 'router_keenetic':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_router_keenetic_card(), reply_markup=get_router_brand_kb())
                        continue

                    if data == 'router_mikrotik':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_router_mikrotik_card(), reply_markup=get_router_brand_kb())
                        continue

                    if data == 'router_openwrt':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_router_openwrt_card(), reply_markup=get_router_brand_kb())
                        continue

                    if data == 'router_generic':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_router_generic_card(), reply_markup=get_router_brand_kb())
                        continue

                    if data == 'cmd_android':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_picker_card(), reply_markup=get_android_picker_kb())
                        continue

                    if data == 'android_samsung':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_samsung_card(), reply_markup=get_android_brand_kb())
                        continue

                    if data == 'android_xiaomi':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_xiaomi_card(), reply_markup=get_android_brand_kb())
                        continue

                    if data == 'android_bbk':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_bbk_card(), reply_markup=get_android_brand_kb())
                        continue

                    if data == 'android_huawei':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_huawei_card(), reply_markup=get_android_brand_kb())
                        continue

                    if data == 'android_pixel':
                        answer_callback(cq_id)
                        edit_message(chat_id, msg_id, get_android_pixel_card(), reply_markup=get_android_brand_kb())
                        continue

                    if data == 'cmd_ios':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_ios_picker_card(), reply_markup=get_ios_picker_kb())

                        continue



                    if data in ('dl_ios_dual', 'dl_ios_se', 'dl_ios_de'):

                        var_key = data.replace('dl_ios_', '')

                        labels = {

                            'dual': 'Швеция + Германия',

                            'se': 'Только Швеция',

                            'de': 'Только Германия'

                        }

                        file_names = {

                            'dual': 'MagicDNS-Dual.mobileconfig',

                            'se': 'MagicDNS-Sweden.mobileconfig',

                            'de': 'MagicDNS-Germany.mobileconfig'

                        }

                        lbl = labels.get(var_key, 'MagicDNS')

                        fname = file_names.get(var_key, 'MagicDNS.mobileconfig')

                        answer_callback(cq_id, f"🍏 Отправляю подписанный профиль ({lbl})...")

                        raw_bytes = generate_mobileconfig(var_key)

                        caption = (

                            f"🍏 <b>Профиль MagicDNS ({lbl}) для iPhone и iPad</b>\n\n"

                            "🟢 <b>Криптографически подписан (CMS / PKCS#7):</b>\n"

                            "Сертификат: <code>api.magicdns.ru</code> (Let\'s Encrypt)\n"

                            "Статус в iOS: 🟢 <b>«Проверен»</b> (зелёная галочка)\n\n"

                            "<b>Инструкция по установке:</b>\n"

                            "1. Нажмите на прикрепленный файл выше и подтвердите загрузку.\n"

                            "2. Откройте <b>Настройки</b> устройства.\n"

                            "3. В самом верху нажмите <b>«Профиль загружен»</b>.\n"

                            "4. Нажмите <b>Установить</b> в правом верхнем углу и введите код-пароль.\n\n"

                            "🛡 <i>Трафик к нейросетям идет через защищенный DoH на полной скорости без сторонних приложений.</i>"

                        )

                        send_document(chat_id, fname, raw_bytes, caption=caption, reply_markup=get_dns_kb())

                        continue







                    if data == 'faq_menu':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_menu_card(), reply_markup=get_faq_menu_kb())

                        continue



                    if data == 'faq_troubleshoot':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_troubleshoot_card(), reply_markup=get_faq_troubleshoot_kb())

                        continue



                    if data == 'faq_win_reset':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_win_reset_card(), reply_markup=get_faq_win_reset_kb())

                        continue



                    if data == 'faq_win_noob':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_win_noob_card(), reply_markup=get_faq_win_noob_kb())

                        continue



                    if data == 'faq_win_pro':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_win_pro_card(), reply_markup=get_faq_win_pro_kb())

                        continue



                    if data == 'faq_browser':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_browser_card(), reply_markup=get_faq_browser_kb())

                        continue



                    if data == 'faq_android':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_android_card(), reply_markup=get_faq_android_kb())

                        continue



                    if data == 'faq_routers':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_routers_card(), reply_markup=get_faq_routers_kb())

                        continue



                    if data == 'faq_apple':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_apple_card(), reply_markup=get_faq_apple_kb())

                        continue



                    if data == 'faq_security':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_security_card(), reply_markup=get_faq_security_kb())

                        continue



                    if data == 'faq_linux':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_linux_card(), reply_markup=get_faq_linux_kb())

                        continue



                    if data == 'faq_friends':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_friends_card(), reply_markup=get_faq_friends_kb())

                        continue



                    if data == 'faq_contact_admin':

                        answer_callback(cq_id)

                        edit_message(chat_id, msg_id, get_faq_contact_admin_card(), reply_markup=get_faq_contact_admin_kb())

                        continue



                    if data == 'confirm_user_msg':

                        pending = PENDING_USER_MESSAGES.pop(from_id, None)

                        if not pending:

                            answer_callback(cq_id, "⚠️ Сообщение уже отправлено или устарело", alert=True)

                            continue



                        answer_callback(cq_id, "✈️ Отправлено администратору!")

                        esc_name = html.escape(str(pending.get('sender_name', 'Пользователь')))

                        esc_uname = html.escape(str(pending.get('username', '')))

                        esc_msg = html.escape(str(pending.get('text', '')))

                        media_label = pending.get('media_label', '')



                        USER_SUPPORT_CONTEXT[from_id] = {
                            "name": esc_name,
                            "username": esc_uname,
                            "last_text": esc_msg,
                            "time": time.time()
                        }

                        admin_forward = (

                            f"📩 <b>Сообщение от пользователя{media_label}!</b>\n\n"

                            f"👤 <b>От:</b> {esc_name} ({esc_uname})\n"

                            f"🆔 <code>[ID: {from_id}]</code>\n"

                        )

                        if esc_msg:

                            admin_forward += f"\n💬 <b>Текст:</b>\n{esc_msg}\n"

                        admin_forward += f"\n👉 <i>Нажмите «Ответить» ниже или сделайте Reply на это сообщение.</i>"

                        admin_reply_btn_kb = {
                            "inline_keyboard": [
                                [{"text": f"💬 Ответить {esc_name}", "callback_data": f"reply_to_user:{from_id}"}]
                            ]
                        }

                        info_res = send_message(ADMIN_CHAT_ID, admin_forward, reply_markup=admin_reply_btn_kb)

                        info_msg_id = info_res.get('result', {}).get('message_id') if info_res.get('ok') else None



                        if pending.get('has_media'):

                            copy_res = copy_message(ADMIN_CHAT_ID, from_id, pending['message_id'], reply_to_message_id=info_msg_id)

                            if not copy_res.get('ok'):

                                forward_message(ADMIN_CHAT_ID, from_id, pending['message_id'])



                        sent_card = (

                            "✓ <b>Сообщение успешно передано администратору!</b>\n"

                            "Скоро ответим прямо здесь в чате.\n\n"

                            "💡 Если у вас возникли сложности при подключении, посмотрите частые вопросы — скорее всего решение уже есть:"

                        )

                        sent_kb = {

                            "inline_keyboard": [

                                [{"text": "❓ Частые вопросы и решения (FAQ)", "callback_data": "faq_menu"}],

                                [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

                            ]

                        }

                        edit_message(chat_id, msg_id, sent_card, reply_markup=sent_kb)

                        continue



                    if data.startswith('reply_to_user:'):
                        try:
                            target_uid = int(data.split(':', 1)[1])
                        except Exception:
                            target_uid = None

                        if not target_uid:
                            answer_callback(cq_id, "⚠️ Ошибка: ID пользователя не найден", alert=True)
                            continue

                        u_ctx = USER_SUPPORT_CONTEXT.get(target_uid, {})
                        u_name = u_ctx.get('name') or "Пользователь"
                        u_uname = u_ctx.get('username') or ""
                        u_text = u_ctx.get('last_text') or ""

                        ACTIVE_ADMIN_REPLY[ADMIN_CHAT_ID] = {
                            "target_user_id": target_uid,
                            "name": u_name,
                            "username": u_uname,
                            "question": u_text,
                            "time": time.time()
                        }

                        answer_callback(cq_id, f"Режим ответа: {u_name}")

                        user_info_line = f"{u_name} ({u_uname})" if u_uname else u_name
                        prompt_card = (
                            f"🎯 <b>Режим ответа пользователю:</b>\n\n"
                            f"👤 <b>Кому:</b> {user_info_line}\n"
                            f"🆔 <code>[ID: {target_uid}]</code>\n"
                        )
                        if u_text:
                            prompt_card += f"💬 <b>Вопрос:</b> <i>«{u_text[:300]}»</i>\n"
                        prompt_card += (
                            f"\n✍️ <b>Напишите текст ответа</b> (или отправьте фото/стикер).\n"
                            f"Ваше следующее сообщение уйдёт строго этому человеку."
                        )

                        cancel_reply_kb = {
                            "inline_keyboard": [
                                [{"text": "❌ Отменить ответ", "callback_data": "cancel_admin_reply"}]
                            ]
                        }
                        send_message(ADMIN_CHAT_ID, prompt_card, reply_markup=cancel_reply_kb)
                        continue

                    if data == 'cancel_admin_reply':
                        ACTIVE_ADMIN_REPLY.pop(ADMIN_CHAT_ID, None)
                        answer_callback(cq_id, "Режим ответа отменен")
                        edit_message(ADMIN_CHAT_ID, msg_id, "❌ <i>Режим ответа отменен. Сообщение не отправлено.</i>")
                        continue

                    if data == 'cancel_user_msg':

                        PENDING_USER_MESSAGES.pop(from_id, None)

                        answer_callback(cq_id, "❌ Отправка отменена")

                        cancel_card = (

                            "❌ <b>Отправка отменена.</b>\n\n"

                            "Ваше сообщение <b>не было передано</b> администратору.\n"

                            "Вы можете изучить частые вопросы или написать новое обращение в любой момент."

                        )

                        cancel_kb = {

                            "inline_keyboard": [

                                [{"text": "❓ Частые вопросы (FAQ)", "callback_data": "faq_menu"}],

                                [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

                            ]

                        }

                        edit_message(chat_id, msg_id, cancel_card, reply_markup=cancel_kb)

                        continue



                    # Admin-only callbacks

                    if from_id != ADMIN_CHAT_ID:

                        answer_callback(cq_id, "⛔ Действие только для администратора", alert=True)

                        continue



                    if data == 'admin_srv_status':

                        answer_callback(cq_id, "🚦 Управление серверами")

                        edit_message(ADMIN_CHAT_ID, msg_id, get_admin_servers_card(), reply_markup=get_admin_servers_kb())

                        continue



                    if data.startswith('srv_pick_'):

                        srv_key = data.replace('srv_pick_', '').strip()

                        answer_callback(cq_id)

                        edit_message(ADMIN_CHAT_ID, msg_id, get_server_picker_card(srv_key), reply_markup=get_server_picker_kb(srv_key))

                        continue



                    if data.startswith('srv_set_'):

                        parts = data.split('_')

                        if len(parts) >= 4:

                            srv_key = parts[2]

                            new_status = parts[3]

                            statuses = load_servers_status()

                            if srv_key in statuses and new_status in STATUS_CONFIG:

                                statuses[srv_key]['status'] = new_status

                                save_servers_status(statuses)

                                meta = STATUS_CONFIG[new_status]

                                srv_name = statuses[srv_key].get('short_name', srv_key.upper())

                                answer_callback(cq_id, f"{meta['badge']} {srv_name}: {meta['label']}!")

                                edit_message(ADMIN_CHAT_ID, msg_id, get_admin_servers_card(), reply_markup=get_admin_servers_kb())

                                threading.Thread(target=sync_servers_to_site, args=(statuses,), daemon=True).start()

                        continue



                    if data.startswith('pub_alert:'):
                        parts = data.split(':')
                        if len(parts) >= 3:
                            draft_id = parts[1]
                            action = parts[2]
                            if action == 'cancel':
                                PENDING_SITE_ALERTS.pop(draft_id, None)
                                edit_message(ADMIN_CHAT_ID, msg_id, "❌ <b>Публикация баннера отменена.</b>")
                                answer_callback(cq_id, "Отменено")
                            else:
                                text_to_pub = PENDING_SITE_ALERTS.pop(draft_id, None)
                                if not text_to_pub:
                                    answer_callback(cq_id, "⚠️ Черновик устарел или не найден", alert=True)
                                    continue
                                answer_callback(cq_id, "⏳ Публикую баннер на сайт...")
                                ok, status_msg = set_site_alert(True, text_to_pub, alert_type=action)
                                if ok:
                                    type_names = {
                                        'success': '🟢 Восстановление (зелёный)',
                                        'warning': '⚠️ Авария / Техработы (жёлтый)',
                                        'info': 'ℹ️ Информационный (синий)'
                                    }
                                    type_title = type_names.get(action, action)
                                    alert_msg = (
                                        f"✅ <b>ОПОВЕЩЕНИЕ ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\n\n"
                                        f"🎨 <b>Тип баннера:</b> {type_title}\n"
                                        f"📢 <b>Текст на сайте:</b>\n{html.escape(text_to_pub)}\n\n"
                                        f"🌐 <i>Баннер отображается вверху всех страниц сайта.</i>"
                                    )
                                    kb = {
                                        "inline_keyboard": [
                                            [{"text": "🔕 Снять оповещение с сайта", "callback_data": "clear_site_alert"}],
                                            [{"text": "🌐 Открыть сайт", "url": "https://magicdns.ru"}]
                                        ]
                                    }
                                    edit_message(ADMIN_CHAT_ID, msg_id, alert_msg, reply_markup=kb)
                                else:
                                    edit_message(ADMIN_CHAT_ID, msg_id, f"⚠️ Ошибка при публикации: {html.escape(status_msg)}")
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







                    if data == 'admin_dig_info':

                        answer_callback(cq_id)

                        dig_admin_kb = {

                            "inline_keyboard": [

                                [{"text": "🔍 cursor.com", "callback_data": "dig_re_cursor.com"}, {"text": "🔍 claude.ai", "callback_data": "dig_re_claude.ai"}],

                                [{"text": "🔍 chatgpt.com", "callback_data": "dig_re_chatgpt.com"}, {"text": "🔍 gemini.google.com", "callback_data": "dig_re_gemini.google.com"}],

                                [{"text": "« В админку", "callback_data": "admin_panel"}]

                            ]

                        }

                        send_message(

                            ADMIN_CHAT_ID,

                            "🔍 <b>DNS-диагностика доменов (/dig):</b>\n\n"

                            "Отправьте команду с любым доменом:\n"

                            "• <code>/dig cursor.com</code>\n"

                            "• <code>/dig claude.ai</code>\n"

                            "• <code>/dig chatgpt.com</code>\n\n"

                            "<i>Или нажмите на один из популярных сервисов ниже:</i>",

                            reply_markup=dig_admin_kb

                        )

                        continue



                    if data.startswith('dig_re_'):

                        domain_to_check = data.replace('dig_re_', '').strip()

                        answer_callback(cq_id, f"🔍 Опрашиваю DNS: {domain_to_check}...")

                        def do_dig_refresh(t_chat_id, t_msg_id, dom):

                            rep, c_dom = run_dig_diagnostics(dom)

                            kb = get_dig_kb(c_dom) if c_dom else None

                            edit_message(t_chat_id, t_msg_id, rep, reply_markup=kb)

                        threading.Thread(target=do_dig_refresh, args=(chat_id, msg_id, domain_to_check), daemon=True).start()

                        continue



                    if data == 'admin_test_ai':

                        answer_callback(cq_id, "🧪 Запуск экспресс-теста ИИ...")

                        edit_message(ADMIN_CHAT_ID, msg_id, "⏳ <b>Выполняется экспресс-диагностика доступности ИИ...</b>\n\n<i>Проверяем сетевые шлюзы и опрашиваем нейросети (Gemini, Claude, ChatGPT, Copilot)...</i>")

                        def do_ai_test(target_msg_id):

                            card = run_ai_diagnostics()

                            edit_message(ADMIN_CHAT_ID, target_msg_id, card, reply_markup=get_ai_diagnostics_kb())

                        threading.Thread(target=do_ai_test, args=(msg_id,), daemon=True).start()

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
                            "🌐 <b>Управление баннером на сайте magicdns.ru:</b>\n\n"
                            "1. Напишите текст баннера в чат.\n"
                            "2. <b>Смахните его (Ответить)</b> и отправьте команду <code>/sitealert</code>\n"
                            "<i>(Бот покажет кнопки: 🟢 Зеленый, ⚠️ Желтый, ℹ️ Синий)</i>\n\n"
                            "• Быстро с текстом: <code>/sitealert Текст</code>\n"
                            "• Снять баннер: <code>/clearsitealert</code>"
                        )
                        continue

                    if data == 'admin_alert_info':
                        answer_callback(cq_id)
                        send_message(
                            ADMIN_CHAT_ID,
                            "🚨 <b>Экстренная рассылка подписчикам:</b>\n\n"
                            "1. Напишите текст оповещения в чат.\n"
                            "2. <b>Смахните его (Ответить)</b> и отправьте команду <code>/alert</code>\n"
                            "<i>(Бот покажет превью и кнопки подтверждения перед отправкой)</i>\n\n"
                            "• Быстро с текстом: <code>/alert Текст оповещения</code>"
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



                    if data.startswith('del_ask_'):

                        rev_id = data.replace('del_ask_', '').strip()

                        answer_callback(cq_id)

                        confirm_kb = {

                            "inline_keyboard": [

                                [

                                    {"text": "⚠️ Да, удалить навсегда", "callback_data": f"del_confirm_{rev_id}"},

                                    {"text": "❌ Отмена", "callback_data": "admin_reviews"}

                                ]

                            ]

                        }

                        send_message(

                            ADMIN_CHAT_ID,

                            f"❓ <b>Подтверждение удаления отзыва #{rev_id}:</b>\n\n"

                            f"Вы действительно хотите навсегда удалить этот отзыв с сайта?",

                            reply_markup=confirm_kb

                        )

                        continue



                    if data.startswith('del_confirm_'):

                        rev_id = data.replace('del_confirm_', '').strip()

                        answer_callback(cq_id, "Удаляю отзыв с сайта...")

                        ok, msg = delete_review_on_github(rev_id)

                        if ok:

                            send_message(ADMIN_CHAT_ID, f"🗑 <b>Отзыв #{rev_id} успешно удалён!</b>\nСайт и кэш мобильных устройств синхронизированы.")

                        else:

                            send_message(ADMIN_CHAT_ID, f"❌ <b>Ошибка при удалении:</b> {msg}")

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

                    sender_chat = m.get('sender_chat', {})

                    sender_chat_id = sender_chat.get('id')

                    sender_name = sender.get('first_name', '')

                    username = f"@{sender.get('username')}" if sender.get('username') else "без юзернейма"

                    text = m.get('text', '') or m.get('caption', '') or ''



                    if chat_type == 'private' and sender_id != ADMIN_CHAT_ID:

                        register_subscriber(sender_id, sender_name, username)

                    # -----------------------------------------------------------------
                    # GROUP SHIELD: Strictly isolated to group & supergroup chats only!
                    # In Private Messages (ЛС) this block is completely skipped.
                    # -----------------------------------------------------------------
                    if chat_type in ['group', 'supergroup']:
                        # 1. Captcha Gate on New Chat Members
                        new_members = m.get('new_chat_members', [])
                        if new_members:
                            for nm in new_members:
                                if nm.get('is_bot'):
                                    continue
                                nm_id = nm.get('id')
                                nm_name = html.escape(nm.get('first_name', 'Участник'))

                                # Mute until captcha solved
                                restrict_chat_member(chat_id, nm_id, can_send_messages=False)

                                captcha_kb = {
                                    "inline_keyboard": [
                                        [{"text": "🛡️ Я человек (нажмите здесь)", "callback_data": f"captcha_pass:{nm_id}"}]
                                    ]
                                }
                                c_msg = (
                                    f"👋 Привет, {nm_name}!\n\n"
                                    "Для защиты чата от спам-ботов подтвердите, что вы человек (кнопка ниже):"
                                )
                                c_res = send_message(chat_id, c_msg, reply_markup=captcha_kb)
                                if c_res.get('ok'):
                                    PENDING_GROUP_CAPTCHAS[f"{chat_id}_{nm_id}"] = {
                                        "msg_id": c_res['result']['message_id'],
                                        "time": time.time()
                                    }
                            continue

                        # 2. Moderation commands by admins (Must be a reply to an offender)
                        reply_m = m.get('reply_to_message')
                        clean_text = text.strip().lower()

                        if reply_m and is_user_chat_admin(chat_id, sender_id, sender_chat_id):
                            offender = reply_m.get('from', {})
                            offender_id = offender.get('id')
                            offender_chat_id = reply_m.get('sender_chat', {}).get('id')
                            offender_name = html.escape(offender.get('first_name', 'Пользователь'))

                            if is_user_chat_admin(chat_id, offender_id, offender_chat_id):
                                send_message(chat_id, "⚠️ <i>Нельзя применить команду к администратору группы.</i>", reply_to_message_id=m['message_id'])
                                continue

                            # !бан / /ban
                            if clean_text in ('!бан', '!ban', '/ban', '!kick', '/kick', '!кик'):
                                delete_message(chat_id, reply_m['message_id'])
                                delete_message(chat_id, m['message_id'])
                                ban_chat_member(chat_id, offender_id)
                                send_message(chat_id, f"🔨 <b>{offender_name}</b> заблокирован модератором.")
                                continue

                            # !мут / /mute [mins]
                            if clean_text.startswith(('!мут', '!mute', '/mute')):
                                parts = clean_text.split()
                                duration_mins = 15
                                if len(parts) > 1 and parts[1].isdigit():
                                    duration_mins = max(1, min(1440, int(parts[1])))
                                until_ts = int(time.time() + duration_mins * 60)

                                delete_message(chat_id, reply_m['message_id'])
                                delete_message(chat_id, m['message_id'])
                                restrict_chat_member(chat_id, offender_id, can_send_messages=False, until_date=until_ts)
                                send_message(chat_id, f"🔇 <b>{offender_name}</b> отправлен в мут на {duration_mins} мин.")
                                continue

                        # 3. Smart Keyword Auto-Router (Anti-flood: max 1 response per 120s per topic)
                        if not m.get('entities') and not clean_text.startswith(('/', '!')):
                            now_ts = time.time()

                            # iOS Trigger
                            if any(w in clean_text for w in ['айфон', 'iphone', 'ios', 'профиль', 'mobileconfig', 'сафари']):
                                cd_key = f"{chat_id}_ios"
                                if now_ts - GROUP_TRIGGER_COOLDOWNS.get(cd_key, 0) > 120:
                                    GROUP_TRIGGER_COOLDOWNS[cd_key] = now_ts
                                    kb = {"inline_keyboard": [[{"text": "🍏 Скачать профиль iOS", "url": "https://t.me/magicdns_alert_bot?start=ios"}]]}
                                    send_message(chat_id, "🍏 <b>Настройка MagicDNS для iPhone / iPad:</b>\nСкачайте криптографически подписанный профиль в один клик:", reply_to_message_id=m['message_id'], reply_markup=kb)
                                    continue

                            # Android Trigger
                            if any(w in clean_text for w in ['андроид', 'android', 'сяоми', 'xiaomi', 'самсунг', 'samsung', 'redmi', 'poco', 'hyperos', 'oneui', 'частный dns']):
                                cd_key = f"{chat_id}_android"
                                if now_ts - GROUP_TRIGGER_COOLDOWNS.get(cd_key, 0) > 120:
                                    GROUP_TRIGGER_COOLDOWNS[cd_key] = now_ts
                                    kb = {"inline_keyboard": [[{"text": "🤖 Мастер настройки Android", "url": "https://t.me/magicdns_alert_bot?start=android"}]]}
                                    send_message(chat_id, "🤖 <b>Настройка MagicDNS на Android (DoT):</b>\nВ строке «Персональный DNS» укажите <code>api.magicdns.ru</code>\nПошаговый мастер по маркам телефонов:", reply_to_message_id=m['message_id'], reply_markup=kb)
                                    continue

                            # Routers Trigger
                            if any(w in clean_text for w in ['роутер', 'кинетик', 'keenetic', 'микротик', 'mikrotik', 'openwrt', 'asus']):
                                cd_key = f"{chat_id}_router"
                                if now_ts - GROUP_TRIGGER_COOLDOWNS.get(cd_key, 0) > 120:
                                    GROUP_TRIGGER_COOLDOWNS[cd_key] = now_ts
                                    kb = {"inline_keyboard": [[{"text": "📡 Настройка роутера", "url": "https://t.me/magicdns_alert_bot?start=routers"}]]}
                                    send_message(chat_id, "📡 <b>Настройка MagicDNS на роутере (Wi-Fi):</b>\nГотовые инструкции для Keenetic, MikroTik и OpenWrt:", reply_to_message_id=m['message_id'], reply_markup=kb)
                                    continue

                            # Check / Trouble Trigger
                            if any(w in clean_text for w in ['не работает', 'ошибка', 'не грузит', 'проверить', 'сбоит']):
                                cd_key = f"{chat_id}_check"
                                if now_ts - GROUP_TRIGGER_COOLDOWNS.get(cd_key, 0) > 120:
                                    GROUP_TRIGGER_COOLDOWNS[cd_key] = now_ts
                                    kb = {"inline_keyboard": [[{"text": "🔍 Запустить радар проверки", "url": "https://magicdns.ru/check.html"}]]}
                                    send_message(chat_id, "🔍 <b>Экспресс-проверка подключения MagicDNS:</b>\nПеред проверкой обязательно отключите любой VPN на телефоне!", reply_to_message_id=m['message_id'], reply_markup=kb)
                                    continue




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
                        media_msg = None
                        reply_to = m.get('reply_to_message')
                        tokens = text.strip().split(maxsplit=1)

                        if len(tokens) > 1:
                            alert_text = tokens[1].strip()
                            if reply_to and (reply_to.get('photo') or reply_to.get('document') or reply_to.get('video')):
                                media_msg = reply_to
                        elif reply_to:
                            alert_text = reply_to.get('text') or reply_to.get('caption') or ""
                            if reply_to and (reply_to.get('photo') or reply_to.get('document') or reply_to.get('video')):
                                media_msg = reply_to

                        if not alert_text and not media_msg:
                            send_message(
                                ADMIN_CHAT_ID,
                                "⚠️ <b>Как сделать рассылку в боте:</b>\n\n"
                                "1. Напишите текст оповещения в этот чат.\n"
                                "2. <b>Смахните его (Ответить)</b> и отправьте команду <code>/alert</code>\n\n"
                                "<i>(Или отправьте сразу с текстом: <code>/alert Текст сообщения</code>)</i>"
                            )
                            continue

                        show_alert_preview(alert_text, media_msg=media_msg, reply_to_msg_id=m.get('message_id'))
                        continue

                    elif cmd in ['/sitealert', '/alertsite', 'оповещениесайта', '/banner', '/баннер']:
                        if sender_id != ADMIN_CHAT_ID:
                            send_message(chat_id, "⛔ Команда доступна только администратору сервиса.")
                            continue

                        tokens = text.strip().split(maxsplit=1)
                        reply_to = m.get('reply_to_message')
                        arg = ""

                        if len(tokens) > 1:
                            arg = tokens[1].strip()
                        elif reply_to:
                            arg = reply_to.get('text') or reply_to.get('caption') or ""

                        if not arg:
                            send_message(
                                ADMIN_CHAT_ID,
                                "🌐 <b>Как опубликовать баннер на сайте magicdns.ru:</b>\n\n"
                                "1. Напишите текст баннера в этот чат.\n"
                                "2. <b>Смахните его (Ответить)</b> и отправьте команду <code>/sitealert</code>\n"
                                "<i>(Бот покажет кнопки: 🟢 Зеленый, ⚠️ Желтый, ℹ️ Синий)</i>\n\n"
                                "<i>(Или отправьте сразу: <code>/sitealert Текст</code> / <code>/sitealert green Текст</code>)</i>\n\n"
                                "• Снять баннер: <code>/clearsitealert</code>"
                            )
                            continue

                        if arg.lower() in ['off', 'clear', 'stop', 'удалить', 'выкл', 'снять']:
                            send_message(ADMIN_CHAT_ID, "⏳ Снимаю баннер с сайта...")
                            ok, status_msg = set_site_alert(False, "")
                            if ok:
                                send_message(ADMIN_CHAT_ID, "🔕 <b>Оповещение успешно снято с сайта magicdns.ru!</b>\nБаннер отключен.")
                            else:
                                send_message(ADMIN_CHAT_ID, f"⚠️ Ошибка при снятии: {status_msg}")
                            continue

                        type_map = {
                            'green': 'success', 'зеленый': 'success', 'зелёный': 'success', 'success': 'success', 'ок': 'success', 'ok': 'success', 'восстановление': 'success',
                            'yellow': 'warning', 'желтый': 'warning', 'жёлтый': 'warning', 'warning': 'warning', 'авария': 'warning', 'техработы': 'warning', 'сбой': 'warning', 'red': 'warning', 'красный': 'warning',
                            'blue': 'info', 'синий': 'info', 'info': 'info', 'инфо': 'info', 'анонс': 'info'
                        }

                        parts = arg.split(maxsplit=1)
                        first_word = parts[0].lower().lstrip('/-')

                        if first_word in type_map and len(parts) > 1 and parts[1].strip():
                            chosen_type = type_map[first_word]
                            text_to_pub = parts[1].strip()
                            send_message(ADMIN_CHAT_ID, "⏳ Публикую оповещение на сайт magicdns.ru...")
                            ok, status_msg = set_site_alert(True, text_to_pub, alert_type=chosen_type)
                            if ok:
                                type_names = {
                                    'success': '🟢 Восстановление (зелёный)',
                                    'warning': '⚠️ Авария / Техработы (жёлтый)',
                                    'info': 'ℹ️ Информационный (синий)'
                                }
                                type_title = type_names.get(chosen_type, chosen_type)
                                alert_msg = (
                                    f"✅ <b>ОПОВЕЩЕНИЕ ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\n\n"
                                    f"🎨 <b>Тип баннера:</b> {type_title}\n\n"
                                    f"📢 <b>Текст на сайте:</b>\n{html.escape(text_to_pub)}\n\n"
                                    f"🌐 <i>Баннер отображается вверху всех страниц сайта.</i>"
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

                        show_sitealert_picker(arg, reply_to_msg_id=m.get('message_id'))
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



                    elif cmd in ['/admin', '/menu', '/mod', 'админ', 'панель', 'мод', 'модерация']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        if chat_type in ['group', 'supergroup']:
                            if is_user_chat_admin(chat_id, sender_id, sender_chat_id):
                                send_message(chat_id, get_group_mod_card(), reply_to_message_id=reply_to_id, reply_markup=get_group_mod_kb())
                                if sender_id == ADMIN_CHAT_ID:
                                    send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                            else:
                                send_message(chat_id, "❌ <i>Команды модерации доступны только администраторам группы.</i>", reply_to_message_id=reply_to_id)
                            continue
                        else:
                            if sender_id != ADMIN_CHAT_ID:
                                send_message(chat_id, "❌ <i>Панель управления серверами доступна только владельцу сервиса.</i>")
                                continue
                            send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                            continue



                    elif cmd in ['/share', '/invite', 'поделиться']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        share_card = (
                            "✈️ <b>Поделиться MagicDNS с друзьями и коллегами</b>\n\n"
                            "Помогите друзьям получить быстрый доступ к нейросетям (Gemini, ChatGPT, Claude) без VPN и сторонних программ!\n\n"
                            "Нажмите кнопку ниже, чтобы отправить готовое приглашение в любой чат или контакт:"
                        )
                        share_kb = {
                            "inline_keyboard": [
                                [{"text": "🚀 Отправить приглашение другу", "url": SHARE_URL}],
                                [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]
                            ]
                        }
                        send_message(chat_id, share_card, reply_to_message_id=reply_to_id, reply_markup=share_kb)
                        continue

                    elif cmd in ['/community', '/chat', '/group', 'чат', 'группа']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        if chat_type in ['group', 'supergroup']:
                            c_card = (
                                "💬 <b>Вы уже находитесь в официальном чате сообщества MagicDNS!</b>\n\n"
                                "Задавайте любые вопросы по настройке прямо здесь — участники и администратор подскажут решение.\n\n"
                                "Для пошаговой интерактивной настройки своего устройства откройте бота в личных сообщениях: @magicdns_alert_bot"
                            )
                            c_kb = {
                                "inline_keyboard": [
                                    [{"text": "🤖 Настроить в ЛС бота", "url": "https://t.me/magicdns_alert_bot?start=help"}],
                                    [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]
                                ]
                            }
                        elif COMMUNITY_CHAT_URL:
                            c_card = f"💬 <b>Официальный чат сообщества MagicDNS:</b>\n\nПрисоединяйтесь к обсуждению: <a href='{COMMUNITY_CHAT_URL}'>{COMMUNITY_CHAT_URL}</a>"
                            c_kb = {"inline_keyboard": [[{"text": "💬 Перейти в чат сообщества", "url": COMMUNITY_CHAT_URL}]]}
                        else:
                            c_card = (
                                "💬 <b>Официальный чат сообщества MagicDNS</b>\n\n"
                                "Группа взаимопомощи и общения пользователей запускается прямо сейчас!\n\n"
                                "Здесь можно будет задавать вопросы по настройке, обмениваться промптами и получать помощь модераторов.\n\n"
                                "🔔 <i>Ссылка на вступление появится здесь сразу после открытия чата.</i>"
                            )
                            c_kb = {
                                "inline_keyboard": [
                                    [{"text": "✈️ Поделиться с другом", "url": SHARE_URL}],
                                    [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]
                                ]
                            }
                        send_message(chat_id, c_card, reply_to_message_id=reply_to_id, reply_markup=c_kb)
                        continue

                    elif cmd in ['/router', '/routers', '/wifi', '/keenetic', '/mikrotik']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_routers_picker_card(), reply_to_message_id=reply_to_id, reply_markup=get_routers_picker_kb())
                        continue

                    elif cmd in ['/check', '/test', '/ping', '/status_ai']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_check_card(), reply_to_message_id=reply_to_id, reply_markup=get_check_kb())
                        continue

                    elif cmd in ['/android', '/dot', '/samsung', '/xiaomi']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_android_picker_card(), reply_to_message_id=reply_to_id, reply_markup=get_android_picker_kb())
                        continue

                    elif cmd in ['/ios', '/apple', '/profile', '/mobileconfig']:

                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None

                        send_message(chat_id, get_ios_picker_card(), reply_to_message_id=reply_to_id, reply_markup=get_ios_picker_kb())

                        continue



                    elif cmd in ['/dig', '/resolve', '/nslookup']:

                        tokens = text.strip().split(maxsplit=1)

                        args = tokens[1].strip() if len(tokens) > 1 else ""

                        if not args:

                            dig_quick_kb = {

                                "inline_keyboard": [

                                    [{"text": "🔍 cursor.com", "callback_data": "dig_re_cursor.com"}, {"text": "🔍 claude.ai", "callback_data": "dig_re_claude.ai"}],

                                    [{"text": "🔍 chatgpt.com", "callback_data": "dig_re_chatgpt.com"}, {"text": "🔍 gemini.google.com", "callback_data": "dig_re_gemini.google.com"}]

                                ]

                            }

                            send_message(

                                chat_id,

                                "🔍 <b>DNS-диагностика домена:</b>\n\n"

                                "Использование: <code>/dig домен</code>\n\n"

                                "Примеры:\n"

                                "• <code>/dig cursor.com</code>\n"

                                "• <code>/dig claude.ai</code>\n"

                                "• <code>/dig chatgpt.com</code>\n"

                                "• <code>/dig openai.com</code>\n\n"

                                "<i>Или выберите сервис для мгновенной проверки ниже:</i>",

                                reply_markup=dig_quick_kb

                            )

                            continue

                        wait_msg = send_message(chat_id, f"🔍 <i>Опрашиваю DNS-узлы для домена {html.escape(args)}...</i>")

                        wait_msg_id = wait_msg.get('result', {}).get('message_id') if isinstance(wait_msg, dict) else None

                        def do_dig_cmd(t_chat_id, t_msg_id, dom):

                            rep, c_dom = run_dig_diagnostics(dom)

                            kb = get_dig_kb(c_dom) if c_dom else None

                            if t_msg_id:

                                edit_message(t_chat_id, t_msg_id, rep, reply_markup=kb)

                            else:

                                send_message(t_chat_id, rep, reply_markup=kb)

                        threading.Thread(target=do_dig_cmd, args=(chat_id, wait_msg_id, args), daemon=True).start()

                        continue



                    elif cmd in ['/testai', '/checkai', '/aitest']:

                        if sender_id != ADMIN_CHAT_ID:

                            continue

                        wait_msg = send_message(ADMIN_CHAT_ID, "⏳ <b>Выполняется экспресс-диагностика доступности ИИ...</b>\n\n<i>Проверяем сетевые шлюзы и опрашиваем нейросети (Gemini, Claude, ChatGPT, Copilot)...</i>")

                        wait_msg_id = wait_msg.get('result', {}).get('message_id') if isinstance(wait_msg, dict) else None

                        def do_ai_test_cmd(target_msg_id):

                            card = run_ai_diagnostics()

                            if target_msg_id:

                                edit_message(ADMIN_CHAT_ID, target_msg_id, card, reply_markup=get_ai_diagnostics_kb())

                            else:

                                send_message(ADMIN_CHAT_ID, card, reply_markup=get_ai_diagnostics_kb())

                        threading.Thread(target=do_ai_test_cmd, args=(wait_msg_id,), daemon=True).start()

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

                        is_adm = (sender_id == ADMIN_CHAT_ID)

                        send_message(chat_id, get_status_card(is_admin=is_adm), reply_to_message_id=reply_to_id, reply_markup=get_status_kb(is_admin=is_adm))

                        continue



                    elif cmd in ['/friends', '/dagami', 'друзья', 'партнеры', 'партнёры']:

                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None

                        send_message(chat_id, get_faq_friends_card(), reply_to_message_id=reply_to_id, reply_markup=get_faq_friends_kb())

                        continue



                    elif cmd in ['/donate', '/support', '/tip', 'донат']:

                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None

                        send_message(chat_id, get_donate_card(), reply_to_message_id=reply_to_id, reply_markup=get_donate_kb())

                        continue



                    elif cmd in ['/cancel', 'отмена', 'отменить']:

                        if sender_id in PENDING_USER_MESSAGES:

                            PENDING_USER_MESSAGES.pop(sender_id, None)

                            send_message(chat_id, "❌ <i>Отправка сообщения в поддержку отменена.</i>")

                            continue



                    elif cmd in ['/faq', 'faq', 'чаво', 'вопросы', 'проблемы']:

                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None

                        send_message(chat_id, get_faq_menu_card(), reply_to_message_id=reply_to_id, reply_markup=get_faq_menu_kb())

                        continue



                    elif cmd in ['/rules', 'правила']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_group_rules_card(), reply_to_message_id=reply_to_id, reply_markup=get_group_rules_kb())
                        continue

                    elif cmd in ['/help', 'помощь', 'команды', 'справка']:
                        reply_to_id = m['message_id'] if chat_type in ['group', 'supergroup'] else None
                        send_message(chat_id, get_help_card(), reply_to_message_id=reply_to_id, reply_markup=get_help_kb())
                        if sender_id == ADMIN_CHAT_ID and chat_type == 'private':
                            send_message(ADMIN_CHAT_ID, get_admin_panel_card(), reply_markup=get_admin_panel_kb())
                        continue



                    elif cmd == '/start':
                        # Deep-linking support for group buttons
                        tokens = text.strip().split()
                        if len(tokens) > 1:
                            sub_arg = tokens[1].lower().strip()
                            if sub_arg in ('ios', 'apple', 'mobileconfig'):
                                send_message(chat_id, get_ios_picker_card(), reply_markup=get_ios_picker_kb())
                                continue
                            elif sub_arg in ('android', 'dot', 'samsung', 'xiaomi'):
                                send_message(chat_id, get_android_picker_card(), reply_markup=get_android_picker_kb())
                                continue
                            elif sub_arg in ('routers', 'router', 'wifi', 'keenetic', 'mikrotik'):
                                send_message(chat_id, get_routers_picker_card(), reply_markup=get_routers_picker_kb())
                                continue
                            elif sub_arg in ('check', 'test'):
                                send_message(chat_id, get_check_card(), reply_markup=get_check_kb())
                                continue

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

                        USER_SUPPORT_CONTEXT[sender_id] = {
                            "name": sender_name,
                            "username": username,
                            "last_text": text or "",
                            "time": time.time()
                        }

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



                        # Save pending message with confirmation

                        PENDING_USER_MESSAGES[sender_id] = {

                            "message_id": m['message_id'],

                            "text": text,

                            "sender_name": sender_name,

                            "username": username,

                            "media_label": media_label,

                            "has_media": has_media,

                            "time": time.time()

                        }



                        preview_text = html.escape(text[:300]) if text else ""

                        card = "📨 <b>Подтверждение отправки в поддержку:</b>\n\n"

                        if preview_text:

                            card += f"💬 <b>Текст:</b> <i>«{preview_text}»</i>\n"

                        if has_media:

                            card += f"📎 <b>Вложение:</b>{media_label}\n"

                        card += (

                            "\n<i>Отправить этот запрос администратору сервиса? "

                            "Если вы написали случайно или передумали — нажмите «Отменить».</i>"

                        )

                        kb = {

                            "inline_keyboard": [

                                [

                                    {"text": "✈️ Да, отправить админу", "callback_data": "confirm_user_msg"},

                                    {"text": "❌ Отменить", "callback_data": "cancel_user_msg"}

                                ],

                                [{"text": "❓ Сначала посмотреть FAQ", "callback_data": "faq_menu"}],

                                [{"text": "⚡ Параметры MagicDNS", "callback_data": "cmd_dns"}]

                            ]

                        }

                        send_message(sender_id, card, reply_markup=kb)

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



                        # Admin reply to user: check ACTIVE_ADMIN_REPLY first, then fallback to reply_to
                        target_id = None
                        if text and text.startswith('/'):
                            # Admin is executing a command: clear any active reply mode so command works
                            ACTIVE_ADMIN_REPLY.pop(ADMIN_CHAT_ID, None)
                        else:
                            active_rep = ACTIVE_ADMIN_REPLY.pop(ADMIN_CHAT_ID, None)
                            if active_rep:
                                target_id = active_rep.get('target_user_id')

                        reply_to = m.get('reply_to_message')

                        if not target_id and reply_to:

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

                                # Check if admin sent sticker, video note, media or text

                                is_admin_sticker = bool(m.get('sticker'))

                                is_admin_video_note = bool(m.get('video_note'))

                                has_admin_media = bool(m.get('photo') or m.get('document') or m.get('video') or m.get('voice') or m.get('animation') or m.get('audio'))



                                if is_admin_sticker:

                                    # Stickers cannot have captions in Telegram Bot API

                                    resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'])

                                    if not resp.get('ok') and m.get('sticker', {}).get('file_id'):

                                        resp = send_sticker(target_id, m['sticker']['file_id'])

                                elif is_admin_video_note:

                                    resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'])

                                elif has_admin_media:

                                    caption = "💬 <b>Поддержка MagicDNS:</b>"

                                    if text:

                                        caption += f"\n\n{html.escape(str(text))}"

                                    resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'], caption=caption, parse_mode="HTML")

                                    if not resp.get('ok'):

                                        send_message(target_id, "💬 <b>Поддержка MagicDNS:</b>")

                                        resp = copy_message(target_id, ADMIN_CHAT_ID, m['message_id'])

                                else:

                                    esc_rep = html.escape(str(text or ''))

                                    resp = send_message(target_id, f"💬 <b>Поддержка MagicDNS:</b>\n\n{esc_rep}")



                                if resp.get('ok'):
                                    u_ctx = USER_SUPPORT_CONTEXT.get(target_id, {})
                                    u_name = u_ctx.get('name') or ''
                                    u_uname = u_ctx.get('username') or ''
                                    display_user = f"{u_name} ({u_uname})" if (u_name and u_uname) else (u_name or f"ID {target_id}")

                                    success_msg = f"✓ <b>Доставлено пользователю {display_user}</b> <code>[ID: {target_id}]</code>"
                                    continue_kb = {
                                        "inline_keyboard": [
                                            [{"text": f"💬 Написать еще {u_name or 'пользователю'}", "callback_data": f"reply_to_user:{target_id}"}]
                                        ]
                                    }
                                    send_message(ADMIN_CHAT_ID, success_msg, reply_to_message_id=m['message_id'], reply_markup=continue_kb)

                                else:

                                    raw_err = str(resp.get('error', 'неизвестная ошибка'))

                                    if 'blocked by the user' in raw_err:

                                        err_msg = f"⚠️ Сообщение не доставлено: пользователь [ID: {target_id}] заблокировал бота."

                                    elif 'user is deactivated' in raw_err:

                                        err_msg = f"⚠️ Сообщение не доставлено: аккаунт пользователя [ID: {target_id}] удален или деактивирован."

                                    elif 'chat not found' in raw_err:

                                        err_msg = f"⚠️ Сообщение не доставлено: диалог с пользователем [ID: {target_id}] не найден."

                                    else:

                                        err_msg = f"⚠️ Ошибка отправки: {html.escape(raw_err)}"

                                    send_message(ADMIN_CHAT_ID, err_msg, reply_to_message_id=m['message_id'])
                                continue





        except Exception as e:

            print(f"[HANDLE UPDATE ERROR] {e}")



    while True:

        try:

            params = {"timeout": 2}

            if last_offset > 0:

                params["offset"] = last_offset + 1



            updates = tg_request("getUpdates", params, timeout=8)



            if not updates.get('ok'):

                time.sleep(1)

                continue



            for u in updates.get('result', []):

                last_offset = u['update_id']

                executor.submit(handle_update, u)



        except Exception as e:

            print(f"[LOOP ERROR] {e}")

            time.sleep(1)




if __name__ == '__main__':

    main()
