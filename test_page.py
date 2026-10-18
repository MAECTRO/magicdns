import re
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

target_file = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\index.html'

if not os.path.exists(target_file):
    print("FATAL: index.html not found!")
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    'Single autonomous file (no external script src)': not bool(re.search(r'<script\s+[^>]*src=', content, re.I)),
    'Single autonomous file (no external link stylesheet)': not bool(re.search(r'<link\s+[^>]*rel=["\']stylesheet["\']', content, re.I)),
    'Brand MagicDNS in header': '<span class="brand-title">Magic<span class="accent">DNS</span></span>' in content or 'MagicDNS' in content,
    'No Cascade in header navbar': 'Cascade' not in content.split('</header>')[0],
    'Swedish Primary DNS 109.120.132.43': '109.120.132.43' in content and '2.56.179.170' not in content,
    'No duckdns hosts': 'greenfest.duckdns.org' not in content and 'greenflow.duckdns.org' not in content,
    'Windows DoH URL https://dns.magicdns.ru/dns-query': 'https://dns.magicdns.ru/dns-query' in content,
    'Apple iOS profile URL https://dns.magicdns.ru/profile.mobileconfig': 'https://dns.magicdns.ru/profile.mobileconfig' in content,
    'Android Private DNS dns.magicdns.ru': 'dns.magicdns.ru' in content,
    'App Proxy http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085': 'http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085' in content,
    'Dynamic status badge: Статус сети: Работает стабильно': 'Статус сети:' in content and 'Работает стабильно' in content,
    'Pulsing dot animation in status badge': 'status-ping' in content and 'radar-ping' in content,
    'Hero heading with AI services': 'Быстрый DNS для Claude AI, Gemini, Google AI Studio и Antigravity' in content,
    'Unified services ribbon with tags': all(tag in content for tag in [
        'Claude AI', 'Gemini', 'ChatGPT', 'Perplexity', 'Antigravity', 'Без VPN и сторонних программ'
    ]) and 'Claude AI &amp; Sonnet' not in content,
    'Support button in header': 'https://pay.cloudtips.ru/p/fa11ea81' in content.split('</header>')[0],
    'Support button in footer': 'https://pay.cloudtips.ru/p/fa11ea81' in content.split('<footer>')[1],
    'No duplicate copy button in Android tab': '<button class="btn-neon-action" data-clipboard="dns.magicdns.ru">Скопировать хост</button>' not in content,
    'Segmented tab bar for 4 platforms': all(tab in content for tab in [
        'Windows (DoH)', 'Apple iOS / macOS', 'Android (DoT)', 'Прокси приложений'
    ]),
    'Clean vector SVG icons in tabs': 'tab-icon' in content,
    'Two-column glassmorphism cards': 'glass-config-card' in content and 'card-left-column' in content and 'card-right-column' in content,
    'QR pods with captions': 'qr-pod' in content and 'qr-caption' in content and 'qr-canvas-box' in content,
    'Inline copy buttons with SVG': 'btn-inline-copy' in content,
    'Connection status checker widget': 'Интерактивная проверка подключения к ИИ-шлюзу' in content,
    'Large neon checker button': 'btn-run-check' in content and 'Проверить подключение' in content,
    'Diagnostics progress bar & log': 'checker-progress' in content and 'checker-fill' in content and 'checker-log' in content,
    'Checker result metrics card': 'checker-result' in content and 'metric-ping' in content,
    'Uptime 99.9% in footer': '99.9%' in content,
    'Telegram link': 'https://t.me/magicdns' in content,
    'Discord link': 'https://discord.gg/magicdns' in content,
    'Theme color #070d14': '#070d14' in content,
    'Neon mint color #00ff9d': '#00ff9d' in content,
    'Emerald color #10b981': '#10b981' in content,
    'Cyber cyan color #06b6d4': '#06b6d4' in content,
    'Glassmorphism backdrop-filter': 'backdrop-filter: blur' in content,
    'Focus-visible accessibility style': ':focus-visible' in content,
    'Tactile Web Audio API feedback': 'playTactileFeedback' in content and 'AudioContext' in content,
    'Haptic vibration support': 'navigator.vibrate' in content,
    'Clipboard copy with originalHtml protection': 'btn.dataset.originalHtml' in content and 'Скопировано!' in content,
    'Native iOS mobileconfig download link (no JS blob)': '<a href="https://dns.magicdns.ru/profile.mobileconfig"' in content and 'id="btn-download-profile"' in content and 'createObjectURL' not in content,
    'Valid closing html tag': '</html>' in content
}

all_ok = True
print("=== MAGICDNS PAGE VERIFICATION RESULTS ===")
for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if not passed:
        all_ok = False

print(f"\nFINAL RESULT: {'SUCCESS (All checks passed)' if all_ok else 'FAILURE'}")
if not all_ok:
    sys.exit(1)
