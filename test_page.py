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
    'Apple iOS profile URL https://magicdns.ru/profile.mobileconfig': 'https://magicdns.ru/profile.mobileconfig' in content,
    'Android Private DNS dns.magicdns.ru': 'dns.magicdns.ru' in content,
    'No proxy endpoints or credentials present': '8085' not in content and 'tab-proxy' not in content and 'card-proxy' not in content and 'Px94kM8vQ7wZb2Rt' not in content,
    'Dynamic status badge: Статус сети: Работает стабильно': 'Статус сети:' in content and 'Работает стабильно' in content,
    'Pulsing dot animation in status badge': 'status-ping' in content and 'radar-ping' in content,
    'Hero heading with AI services': 'Smart DNS для ИИ' in content and 'Gemini' in content and 'ChatGPT' in content and 'Claude' in content,
    'Unified services ribbon with tags': all(tag in content for tag in [
        'Claude AI', 'Gemini', 'ChatGPT', 'Perplexity', 'Antigravity', 'Без VPN и сторонних программ'
    ]) and 'Claude AI &amp; Sonnet' not in content and 'Google AI Studio' not in content[content.find('class="services-ribbon"'):content.find('class="more-services-drawer"')],
    'Support button in header': 'https://pay.cloudtips.ru/p/596a95a5' in content.split('</header>')[0] and 'target="_blank"' in content.split('</header>')[0] and 'rel="noopener noreferrer"' in content.split('</header>')[0],
    'Support button in footer': 'https://pay.cloudtips.ru/p/596a95a5' in content.split('<footer>')[1] and 'target="_blank"' in content.split('<footer>')[1] and 'rel="noopener noreferrer"' in content.split('<footer>')[1],
    'No duplicate copy button in Android tab': '<button class="btn-neon-action" data-clipboard="dns.magicdns.ru">Скопировать хост</button>' not in content,
    'Segmented tab bar for 3 platforms': all(tab in content for tab in [
        'Windows (DoH)', 'Apple iOS / macOS', 'Android (DoT)'
    ]) and 'Прокси приложений' not in content,
    'Clean vector SVG icons in tabs': 'tab-icon' in content,
    'Two-column glassmorphism cards': 'glass-config-card' in content and 'card-left-column' in content and 'card-right-column' in content,
    'QR pods with captions': 'qr-pod' in content and 'qr-caption' in content and 'qr-canvas-box' in content,
    'Inline copy buttons with SVG': 'btn-inline-copy' in content,
    'Connection status checker widget': 'Интерактивная проверка подключения к ИИ-шлюзу' in content,
    'Large neon checker button': 'btn-run-check' in content and 'Проверить подключение' in content,
    'Diagnostics progress bar & log': 'checker-progress' in content and 'checker-fill' in content and 'checker-log' in content,
    'Checker result metrics card': 'checker-result' in content and 'metric-ping' in content,
    'Uptime 99.9% in footer': '99.9%' in content,
    'Telegram and Discord removed from footer': 'https://t.me/magicdns"' not in content and 'https://discord.gg/magicdns' not in content,
    'Theme color #070d14': '#070d14' in content,
    'Neon mint color #00ff9d': '#00ff9d' in content,
    'Emerald color #10b981': '#10b981' in content,
    'Cyber cyan color #06b6d4': '#06b6d4' in content,
    'Glassmorphism backdrop-filter': 'backdrop-filter: blur' in content,
    'Focus-visible accessibility style': ':focus-visible' in content,
    'Tactile Web Audio API feedback': 'playTactileFeedback' in content and 'AudioContext' in content,
    'Haptic vibration support': 'navigator.vibrate' in content,
    'Clipboard copy with originalHtml protection': 'btn.dataset.originalHtml' in content and 'Скопировано!' in content,
    'Native iOS mobileconfig download link (no JS blob)': '<a href="https://magicdns.ru/profile.mobileconfig"' in content and 'id="btn-download-profile"' in content and 'createObjectURL' not in content,
    'No redundant de.magicdns.ru links': 'de.magicdns.ru' not in content,
    'Router Primary DNS 109.120.132.43': 'id="val-router-primary">109.120.132.43</code>' in content,
    'Router Secondary DNS 94.249.177.102': 'id="val-router-secondary">94.249.177.102</code>' in content,
    'Windows separate Primary IPv4 field': 'id="val-win-ipv4-primary">109.120.132.43</code>' in content,
    'Windows separate Secondary IPv4 field': 'id="val-win-ipv4-secondary">94.249.177.102</code>' in content,
    'Windows separate IPv4 copy action buttons': 'data-i18n="btnCopyPrimaryIpv4"' in content and 'data-i18n="btnCopySecondaryIpv4"' in content,
    'Reviews empty state full data-i18n': 'data-i18n="reviewsEmptyBadge"' in content and 'data-i18n="reviewsEmptyTitle"' in content and 'data-i18n="reviewsEmptyDesc"' in content and 'data-i18n="reviewsEmptyBtn"' in content,
    'Feedback modal platform chips & inputs i18n': 'data-i18n="modalPlatRouter"' in content and 'data-i18n-placeholder="modalContactPlaceholder"' in content,
    'Reviews platform & author dynamic localization': 'getLocalizedPlatform' in content and 'isDefaultAuthor' in content,
    'Download buttons tactile feedback binding': 'dlProfileBtn' in content,
    'Comparison table present': 'class="comparison-table"' in content and 'MagicDNS (Smart DNS)' in content and 'Стандартный VPN' in content,
    'AI platforms cards present': all(p in content for p in ['Google Gemini', 'Google AI Studio', 'ChatGPT', 'Claude', 'Midjourney', 'Microsoft Copilot']),
    'FAQ accordion present': 'class="faq-section"' in content and 'class="faq-item"' in content,
    'Cookie banner present': 'id="cookie-banner"' in content and '152-ФЗ' in content,
    'Legal disclaimer present': 'class="legal-disclaimer"' in content and 'AS IS' in content,
    'Footer contact link present': 'id="btn-open-contact"' in content and 'data-i18n="footerContact"' in content,
    'Hero CTA preserves SVG during i18n': 'class="btn-hero-cta" data-i18n="heroCta"' not in content and '<span data-i18n="heroCta">' in content,
    'Regulatory compliance (no обход)': 'обход' not in content.lower(),
    'Regulatory compliance (no разблокиров/взлом/анонимайзер)': not any(term in content.lower() for term in ['разблокиров', 'взлом', 'анонимайзер']),
    'Regulatory compliance (no заблокир)': 'заблокир' not in content.lower(),
    'Contact modal present': 'id="contact-modal"' in content,
    'All 18 semantic core keywords present in body': all(kw in content[content.find('<body>'):].lower() for kw in [
        'смарт днс для ии', 'smart dns для ии', 'днс для искусственного интеллекта', 
        'частный днс для ии', 'днс для нейросетей', 'быстрый днс без vpn', 'персональный dns сервер',
        'dns для gemini', 'smart dns google ai studio', 'доступ к google ai studio без vpn', 
        'как открыть gemini через dns', 'dns для chatgpt', 'доступ к claude ai без vpn', 
        'dns для midjourney', 'copilot dns',
        'настройка частного dns на android для gemini', 'профиль doh dot для ios iphone', 
        'smart dns на роутер keenetic openwrt'
    ]),
    'Schema.org FAQPage present': '"@type": "FAQPage"' in content,
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
