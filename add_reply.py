#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для добавления официального ответа команды MagicDNS на отзыв.
Использование:
    python add_reply.py <review_id> "Текст ответа"
или интерактивно:
    python add_reply.py
"""

import os
import sys
import json
from datetime import datetime

# Поддержка UTF-8 вывода в консоль Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

MONTHS_RU = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEWS_FILE = os.path.join(BASE_DIR, 'reviews.json')

def load_reviews():
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 60)
    print("💬 MagicDNS — Ответ команды на отзыв пользователя")
    print("=" * 60)

    reviews = load_reviews()
    if not reviews:
        print("❌ Отзывов в reviews.json не найдено.")
        return

    review_id = None
    reply_text = None

    if len(sys.argv) >= 3:
        review_id = sys.argv[1].strip()
        reply_text = sys.argv[2].strip()
    elif len(sys.argv) == 2:
        review_id = sys.argv[1].strip()

    if not review_id:
        print("\nПоследние отзывы:")
        for idx, r in enumerate(reviews[:8], 1):
            has_reply = " [Есть ответ]" if r.get('reply') else ""
            msg_snippet = (r.get('message', '')[:50] + '...') if len(r.get('message', '')) > 50 else r.get('message', '')
            print(f"  [{idx}] ID: {r.get('id')} | {r.get('author', 'Пользователь')} ({r.get('platform', 'DNS')}): \"{msg_snippet}\"{has_reply}")
        
        choice = input("\nВыберите номер отзыва (1-8) или введите ID: ").strip()
        if not choice:
            print("Отменено.")
            return
        
        if choice.isdigit() and 1 <= int(choice) <= min(8, len(reviews)):
            target_review = reviews[int(choice) - 1]
            review_id = str(target_review.get('id'))
        else:
            review_id = choice

    # Search review by ID
    target = None
    for r in reviews:
        if str(r.get('id', '')) == str(review_id):
            target = r
            break

    if not target:
        print(f"❌ Отзыв с ID {review_id} не найден.")
        return

    print(f"\nВыбран отзыв #{target.get('id')}:")
    print(f"  Автор: {target.get('author')}")
    print(f"  Оценка: {target.get('rating')}★ ({target.get('platform')})")
    print(f"  Текст: \"{target.get('message')}\"")
    if target.get('reply'):
        curr = target.get('reply')
        curr_text = curr.get('text') if isinstance(curr, dict) else curr
        print(f"  Текущий ответ: \"{curr_text}\"")

    if not reply_text:
        reply_text = input("\nВведите текст вашего ответа (или оставьте пустым для удаления): ").strip()

    now = datetime.now()
    formatted_date = f"{now.day} {MONTHS_RU.get(now.month, 'января')} {now.year}"

    if reply_text:
        target['reply'] = {
            'text': reply_text,
            'date': formatted_date,
            'author': 'Команда MagicDNS'
        }
        print(f"\n✅ Ответ установлен: \"{reply_text}\"")
    else:
        if 'reply' in target:
            del target['reply']
            print("\n🗑️ Ответ удален.")
        else:
            print("\nОтвет не задан, без изменений.")
            return

    save_reviews(reviews)
    print("💾 Файл reviews.json обновлен.")

    # Rebuild page
    print("🔨 Пересборка index.html...")
    build_script = os.path.join(BASE_DIR, 'build_page.py')
    import subprocess
    res = subprocess.run([sys.executable, build_script], capture_output=True, text=True, encoding='utf-8')
    if res.returncode == 0:
        print("✅ index.html успешно пересобран.")
    else:
        print(f"⚠️ Ошибка сборки index.html: {res.stderr}")

    push = input("\nЗапушить изменения на GitHub? (Y/n): ").strip().lower()
    if push not in ('n', 'no', 'нет'):
        push_script = os.path.join(BASE_DIR, 'push_changes.py')
        if os.path.exists(push_script):
            subprocess.run([sys.executable, push_script])
        else:
            subprocess.run(['git', 'add', 'reviews.json', 'index.html'])
            subprocess.run(['git', 'commit', '-m', f"feat(reviews): reply to review {review_id}"])
            subprocess.run(['git', 'push', 'origin', 'main'])

if __name__ == '__main__':
    main()
