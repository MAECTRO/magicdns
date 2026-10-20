import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

keywords = [
    # Основные
    "смарт днс для ии", "smart dns для ии", "днс для искусственного интеллекта", 
    "частный днс для ии", "днс для нейросетей", "быстрый днс без vpn", "персональный dns сервер",
    # Продуктовые
    "dns для gemini", "smart dns google ai studio", "доступ к google ai studio без vpn", 
    "как открыть gemini через dns", "dns для chatgpt", "доступ к claude ai без vpn", 
    "dns для midjourney", "copilot dns",
    # Платформенные
    "настройка частного dns на android для gemini", "профиль doh dot для ios iphone", 
    "smart dns на роутер keenetic openwrt"
]

body_text = soup.body.get_text().lower()

print("=== KEYWORD CHECK IN BODY TEXT ===")
for kw in keywords:
    count = body_text.count(kw.lower())
    print(f"'{kw}': {count} occurrences in <body>")
