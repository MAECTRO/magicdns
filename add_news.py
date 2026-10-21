#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для быстрой публикации новостей и анонсов на сайте MagicDNS.
Использование:
    python add_news.py
или
    python add_news.py "Заголовок" "Текст анонса" "Обновление"
"""

import os
import sys
import json
import subprocess
from datetime import datetime

MONTHS_RU = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_FILE = os.path.join(BASE_DIR, 'news.json')

TAG_TYPES = {
    '1': ('Обновление', 'update'),
    '2': ('Запуск', 'launch'),
    '3': ('Инфраструктура', 'infra'),
    '4': ('ИИ', 'ai'),
    '5': ('Важно', 'important')
}

def main():
    print("=" * 60)
    print("📢 MagicDNS — Публикация нового анонса")
    print("=" * 60)

    if len(sys.argv) >= 3:
        title = sys.argv[1].strip()
        text = sys.argv[2].strip()
        tag_arg = sys.argv[3].strip() if len(sys.argv) > 3 else 'Обновление'
        tag_name, tag_type = tag_arg, 'update'
    else:
        title = input("Заголовок новости: ").strip()
        if not title:
            print("Ошибка: заголовок не может быть пустым.")
            return

        text = input("Текст новости: ").strip()
        if not text:
            print("Ошибка: текст новости не может быть пустым.")
            return

        print("\nВыберите категорию:")
        print("  1) ⚡ Обновление (по умолчанию)")
        print("  2) 🚀 Запуск")
        print("  3) 🛡️ Инфраструктура")
        print("  4) 🧠 ИИ")
        print("  5) 📌 Важно")
        choice = input("Номер [1-5]: ").strip() or '1'
        tag_name, tag_type = TAG_TYPES.get(choice, ('Обновление', 'update'))

    now = datetime.now()
    date_str = f"{now.day} {MONTHS_RU[now.month]} {now.year}"

    # Чтение существующих новостей
    news_list = []
    if os.path.exists(NEWS_FILE):
        try:
            with open(NEWS_FILE, 'r', encoding='utf-8') as f:
                news_list = json.load(f)
        except Exception:
            news_list = []

    new_item = {
        "id": f"news-{int(now.timestamp())}",
        "date": date_str,
        "tag": tag_name,
        "type": tag_type,
        "title": title,
        "text": text
    }

    # Вставляем наверх
    news_list.insert(0, new_item)

    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Новость сохранена в news.json: «{title}»")

    # Сборка страницы
    print("[1/3] Пересборка страницы index.html...")
    build_res = subprocess.run([sys.executable, os.path.join(BASE_DIR, 'build_page.py')], capture_output=True, text=True)
    if build_res.returncode != 0:
        print("[ERROR] Ошибка при сборке:", build_res.stderr or build_res.stdout)
        return

    # Запуск тестов
    print("[2/3] Запуск верификационных тестов...")
    for test_script in ['test_i18n.py', 'test_page.py', 'test_deep.py']:
        res = subprocess.run([sys.executable, os.path.join(BASE_DIR, test_script)], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[ERROR] Тест {test_script} провалился:\n", res.stdout, res.stderr)
            return

    # Пуш на GitHub
    print("[3/3] Публикация изменений на GitHub...")
    push_script = os.path.join(BASE_DIR, 'push_changes.py')
    commit_msg = f"feat(news): {title}"
    push_res = subprocess.run([sys.executable, push_script, commit_msg], capture_output=True, text=True)
    if push_res.returncode != 0:
        print("[ERROR] Ошибка пуша:", push_res.stderr or push_res.stdout)
        return

    print("\n" + "=" * 60)
    print(f"🎉 Готово! Новость «{title}» опубликована на https://magicdns.ru")
    print("=" * 60)

if __name__ == '__main__':
    main()
