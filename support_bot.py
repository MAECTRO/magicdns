#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDNS 24/7 Cloud Support, Relay & 1-Tap Review Moderation Bot
Runs as systemd service on Finland Host (2.56.179.170).

Features:
1. HTTP API on 127.0.0.1:8880 for https://dns.magicdns.ru/api/feedback
   - Client sends feedback/reviews here directly (NO tokens exposed in browser!).
   - Works in Russia without VPN (since dns.magicdns.ru is not blocked!).
2. 1-Tap Review Publishing via Telegram inline keyboard directly to GitHub repo.
3. Two-way live technical support chat with 100% full media support (Photos, Screenshots, Documents, Voice, Video).
4. Community group moderation, anti-spam, /dns, /status, /donate commands.
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

def publish_review_to_github(author, platform, rating, message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/reviews.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "MagicDNS-Finland-VPS-Bot",
        "Accept": "application/vnd.github.v3+json"
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        gh_data = json.loads(resp.read().decode('utf-8'))
        sha = gh_data['sha']
        content_bytes = base64.b64decode(gh_data['content'])
        reviews_list = json.loads(content_bytes.decode('utf-8'))

    now = datetime.now()
    date_str = f"{now.day} {MONTHS_RU[now.month]}"

    # Check for duplicates
    for r in reviews_list:
        if r.get('author') == author and r.get('message') == message:
            return True, "Дубликат: такой отзыв уже есть в списке"

    new_rev = {
        "id": f"rev-{int(now.timestamp())}",
        "author": author,
        "platform": platform,
        "rating": rating,
        "message": message,
        "date": date_str
    }
    reviews_list.insert(0, new_rev)

    updated_json_str = json.dumps(reviews_list, ensure_ascii=False, indent=2)
    b64_content = base64.b64encode(updated_json_str.encode('utf-8')).decode('utf-8')

    put_data = {
        "message": f"feat(reviews): publish verified review from {author} via 1-tap Telegram",
        "content": b64_content,
        "sha": sha
    }
    payload = json.dumps(put_data).encode('utf-8')
    put_req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "MagicDNS-Finland-VPS-Bot",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }, method='PUT')

    with urllib.request.urlopen(put_req, timeout=20) as put_resp:
        return True, "Успешно опубликовано"

def parse_review_message(text):
    author = "Аноним"
    platform = "Windows"
    rating = 5
    body = ""

    lines = text.split('\n')
    is_body = False
    body_lines = []

    for line in lines:
        stripped = line.strip()
        if "Автор:" in stripped:
            author = stripped.split("Автор:", 1)[1].replace('`', '').replace('*', '').strip()
        elif "Платформа:" in stripped:
            platform = stripped.split("Платформа:", 1)[1].replace('`', '').replace('*', '').strip()
        elif "Оценка:" in stripped:
            for star_char in ['★', '⭐']:
                if star_char in stripped:
                    rating = stripped.count(star_char)
                    break
        elif "Текст отзыва:" in stripped or "Текст:" in stripped:
            is_body = True
            continue
        elif "━━━━━━━━━━━━━━━━━━━" in stripped or "👉" in stripped:
            is_body = False
        elif is_body:
            body_lines.append(line)

    body = '\n'.join(body_lines).strip()
    return author, platform, rating, body

# ==============================================================
# HTTP Feedback Receiver on 127.0.0.1:8880 (proxied by Nginx)
# ==============================================================
class FeedbackHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Quiet logs

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if not self.path.startswith('/api/feedback'):
            self.send_response(404)
            self.end_headers()
            return

        try:
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body.decode('utf-8'))

            f_type = data.get('type', 'review')
            platform = data.get('platform', 'Windows')
            rating = int(data.get('rating', 5))
            message = data.get('message', '').strip()
            contact = data.get('contact', '').strip()

            if not message:
                self.send_response(400)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error": "Empty message"}')
                return

            esc_msg = html.escape(message)
            esc_plat = html.escape(platform)
            esc_contact = html.escape(contact) if contact else 'Аноним'
            stars_str = '★' * rating

            reply_markup = None

            if f_type == 'review':
                approve_cmd = f'python add_review.py "{contact.replace("@", "") if contact else "Аноним"}" "{platform}" {rating} "{message}"'
                tg_text = (
                    f"⭐ <b>НОВЫЙ ОТЗЫВ С САЙТА!</b> #ОТЗЫВ\n\n"
                    f"👤 <b>Автор:</b> <code>{esc_contact}</code>\n"
                    f"💻 <b>Платформа:</b> {esc_plat}\n"
                    f"⭐️ <b>Оценка:</b> {stars_str} ({rating}/5)\n\n"
                    f"💬 <b>Текст отзыва:</b>\n{esc_msg}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👉 <b>Опубликовать на сайт (в 1 клик):</b>\n"
                    f"<code>{html.escape(approve_cmd)}</code>"
                )
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {"text": "✅ Опубликовать на сайт", "callback_data": "pub_review"},
                            {"text": "❌ В корзину", "callback_data": "del_review"}
                        ]
                    ]
                }
            elif f_type == 'bug':
                tg_text = (
                    f"🐛 <b>НОВЫЙ БАГ-РЕПОРТ С САЙТА!</b> #БАГ\n\n"
                    f"💻 <b>Платформа:</b> {esc_plat}\n"
                    f"👤 <b>Контакт:</b> <code>{esc_contact}</code>\n\n"
                    f"💬 <b>Описание проблемы:</b>\n{esc_msg}"
                )
            else:
                tg_text = (
                    f"💡 <b>НОВОЕ ПРЕДЛОЖЕНИЕ С САЙТА!</b> #ИДЕЯ\n\n"
                    f"💻 <b>Платформа:</b> {esc_plat}\n"
                    f"👤 <b>Контакт:</b> <code>{esc_contact}</code>\n\n"
                    f"💬 <b>Суть идеи:</b>\n{esc_msg}"
                )

            res = send_message(ADMIN_CHAT_ID, tg_text, reply_markup=reply_markup)

            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            print(f"[HTTP FEEDBACK] Processed {f_type} from {contact or 'anon'}: {res.get('ok')}")

        except Exception as e:
            print(f"[HTTP FEEDBACK ERROR] {e}")
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Server error"}')

def start_http_server():
    server = HTTPServer(('127.0.0.1', 8880), FeedbackHTTPHandler)
    print("[HTTP] Local feedback receiver listening on 127.0.0.1:8880...")
    server.serve_forever()

# ==============================================================
# Main Bot Polling Loop
# ==============================================================
def setup_bot_commands():
    cmds = [
        {"command": "dns", "description": "Параметры и IP-адреса подключения"},
        {"command": "status", "description": "Статус и доступность серверов"},
        {"command": "donate", "description": "Поддержать оплату серверов"},
        {"command": "rules", "description": "Правила сообщества"},
        {"command": "help", "description": "Помощь и список команд"}
    ]
    tg_request("setMyCommands", {"commands": cmds})

def main():
    print("[BOT] MagicDNS 24/7 Moderator & Support Bot started on Finland Host!")
    setup_bot_commands()
    me = tg_request("getMe")
    if not me.get('ok'):
        print("[ERROR] Cannot connect to Telegram:", me)
        sys.exit(1)
    print(f"[OK] Connected as @{me['result']['username']}")

    # Start HTTP receiver in background thread
    t = threading.Thread(target=start_http_server, daemon=True)
    t.start()

    last_offset = 0

    while True:
        try:
            params = {"timeout": 20}
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

                    if from_id != ADMIN_CHAT_ID:
                        answer_callback(cq_id, "⛔ Нет прав администратора", alert=True)
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

                    # --- A. GROUP / SUPERGROUP HANDLING ---
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
                                        "• <code>/rules</code> — правила сообщества\n\n"
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

                        # 3. Group Commands
                        cmd = text.strip().split()[0].lower() if text.strip() else ""
                        cmd = cmd.split('@')[0]  # strip @botname

                        if cmd == '/dns':
                            dns_card = (
                                "⚡ <b>Параметры подключения MagicDNS:</b>\n\n"
                                "• <b>Роутеры (Wi-Fi):</b>\n"
                                "  Основной: <code>109.120.132.43</code>\n"
                                "  Дополнительный: <code>94.249.177.102</code>\n\n"
                                "• <b>Android (Частный DNS):</b>\n"
                                "  Хост: <code>dns.magicdns.ru</code>\n\n"
                                "• <b>iPhone / Mac:</b>\n"
                                "  <a href='https://magicdns.ru/profile.mobileconfig'>Скачать профиль .mobileconfig</a>\n\n"
                                "• <b>Windows:</b>\n"
                                "  DoH: <code>https://dns.magicdns.ru/dns-query</code>\n\n"
                                "🌐 <i>Подробный гайд: <a href='https://magicdns.ru'>magicdns.ru</a></i>"
                            )
                            dns_kb = {
                                "inline_keyboard": [
                                    [{"text": "🌐 Открыть инструкцию на сайте", "url": "https://magicdns.ru/#setup"}],
                                    [{"text": "☕ Сказать спасибо проекту", "url": DONATE_URL}]
                                ]
                            }
                            send_message(chat_id, dns_card, reply_to_message_id=m['message_id'], reply_markup=dns_kb)
                            continue

                        elif cmd == '/status':
                            status_card = (
                                "🟢 <b>Статус инфраструктуры MagicDNS:</b>\n\n"
                                "• 🇸🇪 Швеция (Core Node): 🟢 <code>109.120.132.43</code> (Активен)\n"
                                "• 🇫🇮 Финляндия (Primary / DoH): 🟢 <code>2.56.179.170</code> (Активен)\n"
                                "• 🇩🇪 Германия (Backup Node): 🟢 <code>94.249.177.102</code> (Активен)\n\n"
                                "🛡️ <i>Сеть работает в штатном режиме 24/7. Uptime 99.9%.</i>"
                            )
                            status_kb = {
                                "inline_keyboard": [
                                    [{"text": "☕ Поддержать серверы", "url": DONATE_URL}],
                                    [{"text": "🌐 Сайт magicdns.ru", "url": "https://magicdns.ru"}]
                                ]
                            }
                            send_message(chat_id, status_card, reply_to_message_id=m['message_id'], reply_markup=status_kb)
                            continue

                        elif cmd in ['/donate', '/support', '/tip', 'донат']:
                            donate_card = (
                                "☕ <b>Поддержка серверов MagicDNS</b>\n\n"
                                "MagicDNS — бесплатный независимый проект без рекламы и платных тарифов.\n\n"
                                "Все европейские узлы (Стокгольм, Хельсинки, Франкфурт) и гигабитные каналы мы оплачиваем самостоятельно.\n\n"
                                "Если сервис выручает вас в работе с нейросетями, коде или играх — любая чашка кофе поможет проекту жить дальше и не проседать под наплывом людей. Спасибо каждому! ❤️"
                            )
                            donate_kb = {
                                "inline_keyboard": [
                                    [{"text": "☕ Поддержать серверы (CloudTips)", "url": DONATE_URL}],
                                    [{"text": "🌐 Официальный сайт", "url": "https://magicdns.ru"}]
                                ]
                            }
                            send_message(chat_id, donate_card, reply_to_message_id=m['message_id'], reply_markup=donate_kb)
                            continue

                        elif cmd in ['/rules', '/help']:
                            rules_card = (
                                "📜 <b>Правила MagicDNS Community:</b>\n\n"
                                "1. Взаимоуважение и помощь новичкам.\n"
                                "2. Запрещен спам, реклама, крипта и реферальные ссылки.\n"
                                "3. Запрещены обсуждения политики и оскорбления.\n\n"
                                "⚡ <b>Полезные команды:</b>\n"
                                "• <code>/dns</code> — параметры и IP-адреса\n"
                                "• <code>/status</code> — статус доступности серверов\n"
                                "• <code>/donate</code> — поддержать аренду серверов\n"
                                "• 🌐 Сайт: <a href='https://magicdns.ru'>magicdns.ru</a>"
                            )
                            send_message(chat_id, rules_card, reply_to_message_id=m['message_id'])
                            continue

                        continue

                    # --- B. PRIVATE CHAT HANDLING (Support & Admin Relay) ---
                    if sender_id != ADMIN_CHAT_ID:
                        if text in ['/donate', '/support', '/tip', 'донат']:
                            donate_card = (
                                "☕ <b>Поддержка серверов MagicDNS</b>\n\n"
                                "MagicDNS — бесплатный проект без рекламы.\n"
                                "Если сервис помогает вам в работе — любая поддержка серверов будет очень кстати! ❤️"
                            )
                            donate_kb = {
                                "inline_keyboard": [
                                    [{"text": "☕ Поддержать серверы (CloudTips)", "url": DONATE_URL}],
                                    [{"text": "🌐 Сайт magicdns.ru", "url": "https://magicdns.ru"}]
                                ]
                            }
                            send_message(sender_id, donate_card, reply_markup=donate_kb)
                            continue

                        if text == '/start':
                            welcome = (
                                "👋 <b>Служба поддержки MagicDNS!</b>\n\n"
                                "Наш сайт: <a href='https://magicdns.ru'>magicdns.ru</a>\n\n"
                                "Задайте вопрос по настройке, отправьте скриншот ошибки или сообщите о сбое, и администратор ответит вам здесь."
                            )
                            send_message(sender_id, welcome)
                            notify = f"👤 Новый пользователь в боте поддержки:\n<b>{sender_name}</b> ({username})\nID: <code>[ID: {sender_id}]</code>"
                            send_message(ADMIN_CHAT_ID, notify)
                            continue

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
