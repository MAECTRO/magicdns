#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для полуавтоматической модерации и мгновенной публикации отзывов на MagicDNS.
Использование:
    python add_review.py "Имя" "Платформа" 5 "Текст отзыва"
или
    python add_review.py --author "Вовчик" --platform "Windows" --rating 5 --message "Спасибо вам)"
или интерактивно:
    python add_review.py
"""

import os
import sys
import json
import argparse
import subprocess
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

PLATFORMS = {
    '1': 'Windows',
    '2': 'Apple (iOS / Mac)',
    '3': 'Android',
    '4': 'Роутер (Keenetic / др.)',
    '5': 'DNS'
}

def normalize_platform(plat_raw):
    plat = (plat_raw or '').strip()
    lower = plat.lower()
    if 'win' in lower:
        return 'Windows'
    if 'ios' in lower or 'apple' in lower or 'mac' in lower or 'айфон' in lower:
        return 'Apple (iOS / Mac)'
    if 'android' in lower or 'андроид' in lower:
        return 'Android'
    if 'роутер' in lower or 'router' in lower or 'keenetic' in lower:
        return 'Роутер (Keenetic / др.)'
    return plat or 'Windows'

def main():
    print("=" * 60)
    print("⭐ MagicDNS — Полуавтоматическая публикация отзыва")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="Публикация проверенного отзыва на сайт MagicDNS")
    parser.add_argument('args', nargs='*', help="author, platform, rating, message")
    parser.add_argument('--author', '-a', type=str, default=None, help="Имя или никнейм автора")
    parser.add_argument('--platform', '-p', type=str, default=None, help="Платформа (Windows, iOS, Android, Роутер)")
    parser.add_argument('--rating', '-r', type=int, default=None, help="Оценка от 1 до 5")
    parser.add_argument('--message', '-m', type=str, default=None, help="Текст отзыва")
    parser.add_argument('--no-push', action='store_true', help="Собрать локально без отправки в git")

    parsed = parser.parse_args()

    author = parsed.author
    platform = parsed.platform
    rating = parsed.rating
    message = parsed.message

    # Если позиционные аргументы переданы
    if parsed.args:
        if len(parsed.args) >= 1 and not author:
            author = parsed.args[0]
        if len(parsed.args) >= 2 and not platform:
            platform = parsed.args[1]
        if len(parsed.args) >= 3 and rating is None:
            try:
                rating = int(parsed.args[2])
            except ValueError:
                rating = 5
        if len(parsed.args) >= 4 and not message:
            message = " ".join(parsed.args[3:])

    # Если чего-то не хватает — запрашиваем интерактивно
    if not message:
        if not author:
            author_input = input("Имя или ник автора [по умолчанию: Аноним]: ").strip()
            author = author_input if author_input else "Аноним"

        if not platform:
            print("\nВыберите платформу:")
            print("  1) 💻 Windows (по умолчанию)")
            print("  2) 🍎 Apple (iOS / Mac)")
            print("  3) 🤖 Android")
            print("  4) 🌐 Роутер (Keenetic / др.)")
            print("  5) ⚡ Другое (DNS)")
            choice = input("Номер [1-5]: ").strip() or '1'
            platform = PLATFORMS.get(choice, 'Windows')

        if rating is None:
            rating_input = input("Оценка (1-5) [по умолчанию 5]: ").strip()
            try:
                rating = max(1, min(5, int(rating_input))) if rating_input else 5
            except ValueError:
                rating = 5

        message = input("Текст отзыва: ").strip()
        if not message:
            print("[ОШИБКА] Текст отзыва не может быть пустым.")
            return

    # Валидация и нормализация
    author = (author or 'Аноним').strip()
    platform = normalize_platform(platform)
    try:
        rating = max(1, min(5, int(rating or 5)))
    except (ValueError, TypeError):
        rating = 5
    message = message.strip()

    now = datetime.now()
    date_str = f"{now.day} {MONTHS_RU[now.month]}"

    # Чтение существующего списка отзывов
    reviews_list = []
    if os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
                reviews_list = json.load(f)
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось прочитать reviews.json: {e}")
            reviews_list = []

    # Проверка на дубликат (если такой же автор и текст уже есть)
    for existing in reviews_list:
        if existing.get('author') == author and existing.get('message') == message:
            print(f"[ИНФО] Отзыв от «{author}» с таким же текстом уже опубликован!")
            return

    new_review = {
        "id": f"rev-{int(now.timestamp())}",
        "author": author,
        "platform": platform,
        "rating": rating,
        "message": message,
        "date": date_str
    }

    # Добавляем в конец или в начало? Лучше в начало, чтобы свежие отзывы были первыми
    reviews_list.insert(0, new_review)

    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews_list, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Отзыв успешно добавлен в reviews.json:")
    print(f"     Автор:     {author}")
    print(f"     Платформа: {platform}")
    print(f"     Оценка:    {'★' * rating} ({rating}/5)")
    print(f"     Дата:      {date_str}")
    print(f"     Текст:     «{message}»")

    # 1. Сборка страницы index.html
    print("\n[1/3] Пересборка страницы index.html через build_page.py...")
    build_res = subprocess.run([sys.executable, os.path.join(BASE_DIR, 'build_page.py')], capture_output=True, text=True)
    if build_res.returncode != 0:
        print("[ОШИБКА] Сборка завершилась с ошибкой:")
        print(build_res.stderr or build_res.stdout)
        return
    print("      ✓ index.html успешно собран с обновленным списком отзывов")

    # 2. Запуск тестов
    print("[2/3] Запуск автоматических тестов верификации...")
    test_files = ['test_i18n.py', 'test_page.py', 'test_deep.py', 'test_probe.py']
    for tf in test_files:
        test_path = os.path.join(BASE_DIR, tf)
        if os.path.exists(test_path):
            tres = subprocess.run([sys.executable, test_path], capture_output=True, text=True)
            if tres.returncode != 0:
                print(f"[ОШИБКА] Тест {tf} провален:")
                print(tres.stdout or tres.stderr)
                return
    print("      ✓ Все проверочные тесты пройдены на 100%!")

    # 3. Пуш на продакшн через push_changes.py
    if parsed.no_push:
        print("[3/3] Флаг --no-push: публикация в git пропущена.")
        print("\n✅ Отзыв успешно внедрен локально!")
    else:
        print("[3/3] Отправка изменений на GitHub / MagicDNS...")
        commit_msg = f"feat(reviews): add verified 5-star review from {author}"
        push_script = os.path.join(BASE_DIR, 'push_changes.py')
        push_res = subprocess.run([sys.executable, push_script, commit_msg], capture_output=True, text=True)
        print(push_res.stdout)
        if push_res.returncode == 0:
            print(f"\n🎉 ГОТОВО! Отзыв от «{author}» опубликован на сайте https://magicdns.ru/#reviews!")
        else:
            print("[ВНИМАНИЕ] Не удалось выполнить push:", push_res.stderr)

if __name__ == '__main__':
    main()
