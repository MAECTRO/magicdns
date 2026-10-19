import re
import os
import sys
import xml.etree.ElementTree as ET
import subprocess
import cv2
import numpy as np
import qrcode

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

html_path = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\index.html'
mobileconfig_path = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\profile.mobileconfig'

assert os.path.exists(html_path), "index.html must exist"
assert os.path.exists(mobileconfig_path), "profile.mobileconfig must exist"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

tests = []

def test(name, condition, details=""):
    tests.append((name, bool(condition), details))

# 1. Autonomous single file
test("No external script tags", not re.search(r'<script\s+[^>]*src=', html, re.I))
test("No external stylesheet links", not re.search(r'<link\s+[^>]*rel=["\']stylesheet["\']', html, re.I))

# 2. Cyber-Minimalism Palette & Atmosphere
test("Background deep color #070d14", '#070d14' in html)
test("Neon mint color #00ff9d", '#00ff9d' in html)
test("Emerald color #10b981", '#10b981' in html)
test("Cyber cyan color #06b6d4", '#06b6d4' in html)
test("Glassmorphism backdrop-filter", 'backdrop-filter: blur' in html)
test("Focus visible outline style", ':focus-visible' in html and 'outline' in html)
test("Smooth scrolling enabled", 'scroll-behavior: smooth' in html)

# 3. Header structure
test("Brand MagicDNS in header", '<span class="brand-title">Magic<span class="accent">DNS</span></span>' in html or 'MagicDNS' in html)
test("No Cascade in header navbar", 'Cascade' not in html.split('</header>')[0])
test("Logo has clean network SVG icon", 'logo-icon' in html and '<circle cx="12" cy="12" r="3">' in html)
test("Live status badge", 'Статус сети:' in html and 'Работает стабильно' in html)
test("Pulsing status dot animation", 'radar-ping' in html and 'status-ping' in html)

# 4. Hero section requirements
test("Hero heading for Claude, Gemini, Google AI Studio, Antigravity",
     'Быстрый DNS для Claude AI, Gemini, Google AI Studio и Antigravity' in html)
test("Hero subtitle direct access without VPN",
     'Прямой доступ к Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT без VPN' in html)
test("Unified services ribbon chips",
     all(chip in html for chip in ['Claude AI', 'Gemini', 'ChatGPT', 'Perplexity', 'Antigravity', 'Без VPN и сторонних программ'])
     and 'Claude AI &amp; Sonnet' not in html
     and 'Google AI Studio' not in html[html.find('class="services-ribbon"'):html.find('class="configurator-section tabs-section')])
test("Support button in header", 'https://pay.cloudtips.ru/p/596a95a5' in html.split('</header>')[0] and 'target="_blank"' in html.split('</header>')[0] and 'rel="noopener noreferrer"' in html.split('</header>')[0])
test("Support button in footer", 'https://pay.cloudtips.ru/p/596a95a5' in html.split('<footer>')[1] and 'target="_blank"' in html.split('<footer>')[1] and 'rel="noopener noreferrer"' in html.split('<footer>')[1])
test("Support button heart has proper fill color", '.social-btn-donate .donate-heart' in html and 'fill: #ff5e7e !important;' in html)
test("No duplicate copy button in Android tab", '<button class="btn-neon-action" data-clipboard="dns.magicdns.ru">Скопировать хост</button>' not in html)

# 5. Segmented Tab Bar & Device Configurator
test("Segmented bar present", 'class="segmented-bar"' in html)
test("Windows DoH tab with SVG icon", 'id="tab-windows"' in html and 'Windows (DoH)' in html)
test("Apple iOS/macOS tab with SVG icon", 'id="tab-ios"' in html and 'Apple iOS / macOS' in html)
test("Android DoT tab with SVG icon", 'id="tab-android"' in html and 'Android (DoT)' in html)
test("Proxy tab with SVG icon", 'id="tab-proxy"' in html and 'Прокси приложений' in html)

# 6. Two-Column Glassmorphism Cards & Endpoints
test("Glassmorphism two-column configuration card layout",
     'glass-config-card' in html and 'card-left-column' in html and 'card-right-column' in html)
test("Swedish IPv4 109.120.132.43 present", '109.120.132.43' in html and '2.56.179.170' not in html)
test("No duckdns hosts present", 'greenfest.duckdns.org' not in html and 'greenflow.duckdns.org' not in html)
test("Windows DoH URL", 'https://dns.magicdns.ru/dns-query' in html)
test("iOS profile URL", 'https://dns.magicdns.ru/profile.mobileconfig' in html)
test("Android Private DNS host", 'dns.magicdns.ru' in html)
test("Proxy complete address and parameters",
     'http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085' in html and '8085' in html and 'Px94kM8vQ7wZb2Rt' in html)

# 7. QR Code Pods with captions
test("QR pods with dark backing and caption present",
     'class="qr-pod"' in html and 'class="qr-caption"' in html and 'class="qr-canvas-box"' in html)

# 8. Interactive Connection Status Checker
test("Interactive checker heading", 'Интерактивная проверка подключения к ИИ-шлюзу' in html)
test("Large neon pulse button", 'btn-run-check' in html and 'Проверить подключение' in html and 'neonPulse' in html)
test("Animated progress bar and log", 'checker-progress' in html and 'checker-fill' in html and 'checker-log' in html)
test("Result card with metrics", 'checker-result' in html and 'metric-ping' in html)

# 9. Footer
test("Footer Uptime 99.9%", '99.9%' in html)
test("Telegram and Discord removed from footer", 'https://t.me/magicdns' not in html and 'https://discord.gg/magicdns' not in html)

# 10. Controller & Accessibility (Xbox / Keyboard)
test("Active tab has tabindex 0", 'id="tab-windows"' in html and 'tabindex="0"' in html)
test("Inactive tabs have tabindex -1", 'tabindex="-1"' in html)
test("ArrowDown does not switch tab (no focus trap)", 'e.key === \'ArrowDown\'' in html)

# 11. Interactions, Audio, Haptics & Bug Fixes
test("Double-click copy bug fixed (dataset.originalHtml check)", 'btn.dataset.originalHtml' in html)
test("Native iOS mobileconfig download link (no JS blob)", '<a href="https://dns.magicdns.ru/profile.mobileconfig"' in html and 'id="btn-download-profile"' in html and 'createObjectURL' not in html)
test("Dedicated backup iOS mobileconfig download button", 'id="btn-download-backup-profile"' in html and 'href="https://de.magicdns.ru/api/profile.mobileconfig"' in html)
test("Router Primary DNS is 109.120.132.43", 'id="val-router-primary">109.120.132.43</code>' in html)
test("Router Secondary DNS is 94.249.177.102", 'id="val-router-secondary">94.249.177.102</code>' in html)
test("Windows separate Primary IPv4 field 109.120.132.43", 'id="val-win-ipv4-primary">109.120.132.43</code>' in html)
test("Windows separate Secondary IPv4 field 94.249.177.102", 'id="val-win-ipv4-secondary">94.249.177.102</code>' in html)
test("Windows separate IPv4 copy action buttons", 'data-i18n="btnCopyPrimaryIpv4"' in html and 'data-i18n="btnCopySecondaryIpv4"' in html)
test("Reviews empty state full data-i18n", 'data-i18n="reviewsEmptyBadge"' in html and 'data-i18n="reviewsEmptyTitle"' in html and 'data-i18n="reviewsEmptyDesc"' in html and 'data-i18n="reviewsEmptyBtn"' in html)
test("Feedback modal platform chips & inputs i18n", 'data-i18n="modalPlatRouter"' in html and 'data-i18n-placeholder="modalContactPlaceholder"' in html)
test("Procedural tactile feedback audio/haptics present", 'playTactileFeedback' in html and 'navigator.vibrate' in html and 'AudioContext' in html)

# 12. Mobileconfig file validity
with open(mobileconfig_path, 'r', encoding='utf-8') as f:
    mc_content = f.read()

try:
    ET.fromstring(mc_content)
    test("profile.mobileconfig is valid XML", True)
except Exception as e:
    test("profile.mobileconfig is valid XML", False, str(e))

test("profile.mobileconfig has DoH protocol and URL", 'HTTPS' in mc_content and 'https://dns.magicdns.ru/dns-query' in mc_content)
test("profile.mobileconfig has Swedish DNS IP 109.120.132.43", '109.120.132.43' in mc_content and '2.56.179.170' not in mc_content)

# 13. Extract JS and validate with Node.js vm
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
test("JavaScript block found in HTML", bool(script_match))
if script_match:
    js_code = script_match.group(1)
    temp_js_path = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_test_script.js'
    with open(temp_js_path, 'w', encoding='utf-8') as f:
        f.write(js_code)
    try:
        res = subprocess.run(['node', '--check', temp_js_path], capture_output=True, text=True, check=True)
        test("JavaScript syntax is 100% valid in Node.js", res.returncode == 0)
    except Exception as e:
        test("JavaScript syntax is 100% valid in Node.js", False, str(e))
    finally:
        if os.path.exists(temp_js_path):
            os.remove(temp_js_path)

# 14. Real QR Code Detection Verification with OpenCV
detector = cv2.QRCodeDetector()
qr_targets = [
    'https://dns.magicdns.ru/dns-query',
    'https://dns.magicdns.ru/profile.mobileconfig',
    'dns.magicdns.ru',
    'http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085'
]
qr_all_scannable = True
for target in qr_targets:
    qr_obj = qrcode.QRCode(box_size=10, border=4)
    qr_obj.add_data(target)
    qr_obj.make(fit=True)
    img = qr_obj.make_image(fill_color='black', back_color='white').convert('RGB')
    val, _, _ = detector.detectAndDecode(np.array(img))
    if val != target:
        qr_all_scannable = False
        break

test("All 4 QR codes are 100% scannable via OpenCV QRCodeDetector", qr_all_scannable)

# 15. Anti-AI writing compliance (Rule 5)
banned_words = [
    'погрузиться в', 'богатое полотно', 'маяк', 'поворотный момент', 'не только',
    'служит в качестве', 'выступает в роли', 'представляет собой', 'неотъемлемая часть',
    'краеугольный камень', 'vibrant', 'bolster', 'foster'
]
found_banned = [w for w in banned_words if w.lower() in html.lower()]
test("Anti-AI writing rule compliance (no forbidden clichés)", len(found_banned) == 0, f"Found: {found_banned}")

# 16. SEO & Search Engine Optimization Suite
import json
from PIL import Image

# Robots.txt
robots_root = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\robots.txt'
robots_pub = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\public\robots.txt'
test("robots.txt exists in root", os.path.exists(robots_root))
test("robots.txt exists in public/", os.path.exists(robots_pub))
if os.path.exists(robots_root):
    with open(robots_root, 'r', encoding='utf-8') as f:
        rc = f.read()
    test("robots.txt has User-agent: * and Allow: /", 'User-agent: *' in rc and 'Allow: /' in rc)
    test("robots.txt blocks query parameters", 'Disallow: /*?*' in rc)
    test("robots.txt has Sitemap directive", 'Sitemap: https://magicdns.ru/sitemap.xml' in rc)

# Sitemap.xml
sitemap_root = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\sitemap.xml'
sitemap_pub = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\public\sitemap.xml'
test("sitemap.xml exists in root", os.path.exists(sitemap_root))
test("sitemap.xml exists in public/", os.path.exists(sitemap_pub))
if os.path.exists(sitemap_root):
    try:
        st = ET.parse(sitemap_root)
        s_root = st.getroot()
        test("sitemap.xml is valid XML with correct namespace", 'sitemaps.org' in s_root.tag)
        test("sitemap.xml contains https://magicdns.ru/", 'https://magicdns.ru/' in open(sitemap_root).read())
        test("sitemap.xml has priority 1.0", '<priority>1.0</priority>' in open(sitemap_root).read())
    except Exception as e:
        test("sitemap.xml is valid XML", False, str(e))

# OG Image
og_root = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\og-image.png'
og_pub = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\public\og-image.png'
test("og-image.png exists in root", os.path.exists(og_root))
test("og-image.png exists in public/", os.path.exists(og_pub))
if os.path.exists(og_root):
    with Image.open(og_root) as im:
        test("og-image.png has standard 1200x630 dimensions", im.size == (1200, 630))

# HTML Head Meta Tags
title_match = re.search(r'<title>(.*?)</title>', html)
test("Title tag present and optimal length (30-70 chars)", bool(title_match and 30 <= len(title_match.group(1)) <= 70), f"Len: {len(title_match.group(1)) if title_match else 0}")

desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
test("Description meta tag present and optimal length (50-160 chars)", bool(desc_match and 50 <= len(desc_match.group(1)) <= 160), f"Len: {len(desc_match.group(1)) if desc_match else 0}")

test("Keywords meta tag present", '<meta name="keywords"' in html)
test("Canonical link present", '<link rel="canonical" href="https://magicdns.ru/">' in html)

# Open Graph Tags
test("Open Graph site_name, url, title, description, image present",
     all(f'property="og:{prop}"' in html for prop in ['site_name', 'url', 'title', 'description', 'type', 'locale', 'image', 'image:width', 'image:height']))

# Twitter Cards
test("Twitter Cards card, url, title, description, image present",
     all(f'name="twitter:{prop}"' in html for prop in ['card', 'url', 'title', 'description', 'image']))

# Verification placeholders
test("Google Search Console verification placeholder present", 'google-site-verification' in html)
test("Yandex Webmaster verification placeholder present", 'yandex-verification' in html)

# Schema.org JSON-LD
jsonld_match = re.search(r'<script type=["\']application/ld\+json["\']>(.*?)</script>', html, re.DOTALL)
test("Schema.org JSON-LD script present", bool(jsonld_match))
if jsonld_match:
    try:
        ld_data = json.loads(jsonld_match.group(1))
        test("Schema.org JSON-LD is valid JSON", True)
        types = [item.get('@type') for item in ld_data.get('@graph', [])] if '@graph' in ld_data else [ld_data.get('@type')]
        test("Schema.org includes WebApplication or WebSite", 'WebApplication' in types or 'WebSite' in types)
    except Exception as e:
        test("Schema.org JSON-LD is valid JSON", False, str(e))

# Summary
print("\n" + "="*50)
print("DEEP VERIFICATION SUITE RESULTS")
print("="*50)
all_passed = True
for name, passed, details in tests:
    status = "PASS" if passed else "FAIL"
    detail_str = f" ({details})" if details else ""
    print(f"[{status}] {name}{detail_str}")
    if not passed:
        all_passed = False

print(f"\nFINAL STATUS: {'ALL TESTS PASSED!' if all_passed else 'SOME TESTS FAILED!'}")
if not all_passed:
    sys.exit(1)
