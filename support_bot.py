#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDNS 24/7 Cloud Support & 1-Tap Review Moderation Bot
Runs as systemd service on Finland Host (2.56.179.170).
"""

import os
import sys
import time
import json
import html
import base64
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

BOT_TOKEN = "8626072258:AAHtcqrf37R0iW3D83Ae7WzLjy2A9alr6Gw"
ADMIN_CHAT_ID = 8010010144
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "MAECTRO/magicdns"
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
            # Another session or poll in progress; back off
            print("[TG 409] Backing off 12 seconds to clear connection...")
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

def send_message(chat_id, text, parse_mode="HTML", reply_to_message_id=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    return tg_request("sendMessage", data)

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

    lines = text.split('\\n')
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

    body = '\\n'.join(body_lines).strip()
    return author, platform, rating, body

def main():
    print("[BOT] MagicDNS 24/7 Moderator & Support Bot started on Finland Host!")
    me = tg_request("getMe")
    if not me.get('ok'):
        print("[ERROR] Cannot connect to Telegram:", me)
        sys.exit(1)
    print(f"[OK] Connected as @{me['result']['username']}")

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
                        edit_message(ADMIN_CHAT_ID, msg_id, msg_text + "\\n\\n❌ <i>Отзыв отклонён и отправлен в корзину.</i>")
                        continue

                    if data == 'pub_review':
                        answer_callback(cq_id, "⏳ Публикую отзыв на сайт...")
                        author, platform, rating, review_text = parse_review_message(msg_text)
                        print(f"[PUB] Author: {author}, Platform: {platform}, Rating: {rating}, Text: {review_text[:50]}...")

                        try:
                            ok, status_msg = publish_review_to_github(author, platform, rating, review_text)
                            if ok:
                                stars_str = '★' * rating
                                esc_author = html.escape(str(author))
                                esc_platform = html.escape(str(platform))
                                esc_text = html.escape(str(review_text))
                                updated_text = (
                                    f"✅ <b>ОПУБЛИКОВАНО НА САЙТЕ MAGICDNS.RU!</b>\\n\\n"
                                    f"👤 <b>Автор:</b> {esc_author}\\n"
                                    f"💻 <b>Платформа:</b> {esc_platform}\\n"
                                    f"⭐️ <b>Оценка:</b> {stars_str} ({rating}/5)\\n"
                                    f"💬 <b>Текст:</b>\\n{esc_text}\\n\\n"
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

                # 2. Handle Support Messages
                if 'message' in u:
                    m = u['message']
                    sender = m.get('from', {})
                    sender_id = sender.get('id')
                    sender_name = sender.get('first_name', '')
                    username = f"@{sender.get('username')}" if sender.get('username') else "без юзернейма"
                    text = m.get('text', '')

                    if sender_id != ADMIN_CHAT_ID:
                        if text == '/start':
                            welcome = (
                                "👋 <b>Служба поддержки MagicDNS!</b>\\n\\n"
                                "Наш сайт: <a href='https://magicdns.ru'>magicdns.ru</a>\\n\\n"
                                "Задайте вопрос по настройке или сообщите о сбое, и администратор ответит вам здесь."
                            )
                            send_message(sender_id, welcome)
                            notify = f"👤 Новый пользователь в боте поддержки:\\n<b>{sender_name}</b> ({username})\\nID: <code>[ID: {sender_id}]</code>"
                            send_message(ADMIN_CHAT_ID, notify)
                            continue

                        # Forward user message to admin
                        esc_name = html.escape(str(sender_name))
                        esc_uname = html.escape(str(username))
                        esc_msg = html.escape(str(text))
                        admin_forward = (
                            f"📩 <b>Сообщение от пользователя!</b>\\n\\n"
                            f"👤 <b>От:</b> {esc_name} ({esc_uname})\\n"
                            f"🆔 <code>[ID: {sender_id}]</code>\\n\\n"
                            f"💬 <b>Текст:</b>\\n{esc_msg}\\n\\n"
                            f"👉 <i>Сделайте 'Reply' (Ответить), чтобы написать пользователю.</i>"
                        )
                        send_message(ADMIN_CHAT_ID, admin_forward)
                        send_message(sender_id, "✓ Сообщение передано администратору. Скоро ответим прямо здесь!")
                    else:
                        # Admin reply to user
                        reply_to = m.get('reply_to_message')
                        if reply_to and reply_to.get('text'):
                            import re
                            id_match = re.search(r'\\[ID:\\s*(\\d+)\\]', reply_to.get('text'))
                            if id_match:
                                target_id = int(id_match.group(1))
                                esc_rep = html.escape(str(text))
                                resp = send_message(target_id, f"💬 <b>Поддержка MagicDNS:</b>\\n\\n{esc_rep}")
                                if resp.get('ok'):
                                    send_message(ADMIN_CHAT_ID, f"✓ Доставлено пользователю [ID: {target_id}]", reply_to_message_id=m['message_id'])

        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(3)

if __name__ == '__main__':
    main()
