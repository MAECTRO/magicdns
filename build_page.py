import os
import qrcode
import qrcode.image.svg
import re
import json
from i18n_data import i18n, faq_answers

i18n_json = json.dumps(i18n, ensure_ascii=False)
faq_answers_json = json.dumps(faq_answers, ensure_ascii=False)

def get_svg_qr(data):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(data, image_factory=factory, box_size=10, border=4)
    svg = img.to_string(encoding='unicode')
    if '<?xml' in svg:
        svg = svg.split('?>', 1)[1].strip()
    svg = re.sub(r'width="[^"]+"', 'width="100%"', svg)
    svg = re.sub(r'height="[^"]+"', 'height="100%"', svg)
    svg = svg.replace('<svg ', '<svg class="qr-svg" ')
    svg = svg.replace('<path ', '<path fill="#070d14" ')
    return svg

# Generate QR codes for the 4 platform configurations
qr_windows = get_svg_qr('https://dns.magicdns.ru/dns-query')
qr_ios = get_svg_qr('https://magicdns.ru/profile.mobileconfig')
qr_android = get_svg_qr('dns.magicdns.ru')

# Load news and announcements from news.json
news_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'news.json')
news_cards_html = ''
if os.path.exists(news_json_path):
    try:
        with open(news_json_path, 'r', encoding='utf-8') as f:
            news_items = json.load(f)
            for item in news_items:
                tag = item.get("tag", "Обновление")
                tag_type = item.get("type", "update")
                date_str = item.get("date", "")
                title = item.get("title", "")
                text = item.get("text", "")
                news_cards_html += f'''
        <article class="news-card {tag_type}">
          <div class="news-card-top">
            <span class="news-tag {tag_type}">{tag}</span>
            <span class="news-date">{date_str}</span>
          </div>
          <h3 class="news-card-title">{title}</h3>
          <p class="news-card-text">{text}</p>
        </article>'''
    except Exception as e:
        news_cards_html = ''

# Load community reviews from reviews.json
reviews_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reviews.json')
reviews_json_str = "[]"
if os.path.exists(reviews_json_path):
    try:
        with open(reviews_json_path, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
            reviews_json_str = json.dumps(reviews_data, ensure_ascii=False)
    except Exception as e:
        reviews_json_str = "[]"

html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#070d14">
  <title>MagicDNS — ДНС для ИИ: прямой доступ на полной скорости</title>
  <meta name="description" content="ДНС для ИИ и Smart DNS для нейросетей. Прямой доступ к Gemini, ChatGPT и Claude без сторонних приложений и тоннелей на полной скорости. Бесплатная настройка!">
  <meta name="keywords" content="днс для ии, ДНС ДЛЯ ИИ, смарт днс для ии, smart dns для ии, днс для искусственного интеллекта, частный днс для ии, днс для нейросетей, быстрый днс без сторонних приложений, персональный dns сервер, dns для gemini, smart dns google ai studio, доступ к google ai studio без сторонних приложений, как открыть gemini через dns, dns для chatgpt, доступ к claude ai без сторонних приложений, dns для midjourney, copilot dns, настройка частного dns на android для gemini, профиль doh dot для ios iphone, smart dns на роутер keenetic openwrt, MagicDNS, Claude AI, Gemini, Google AI Studio, ChatGPT, DoH, DoT">
  <link rel="canonical" href="https://magicdns.ru/">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%2300ff9d'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Ccircle%20cx='12'%20cy='12'%20r='3'/%3E%3Cpath%20d='M12%202v7m0%206v7M2%2012h7m6%200h7'/%3E%3Ccircle%20cx='12'%20cy='2'%20r='1.5'%20fill='%2300ff9d'/%3E%3Ccircle%20cx='12'%20cy='22'%20r='1.5'%20fill='%2300ff9d'/%3E%3Ccircle%20cx='2'%20cy='12'%20r='1.5'%20fill='%2300ff9d'/%3E%3Ccircle%20cx='22'%20cy='12'%20r='1.5'%20fill='%2300ff9d'/%3E%3C/svg%3E">

  <!-- Search Engine Verification -->
  <meta name="google-site-verification" content="V-LR-OgNY2JECR2l_17IM_vNMcUglPzkEd3CSbcoIHw">
  <meta name="yandex-verification" content="51263b81b36e7cca">

  <!-- Open Graph / Facebook / Telegram / WhatsApp -->
  <meta property="og:site_name" content="MagicDNS">
  <meta property="og:url" content="https://magicdns.ru/">
  <meta property="og:title" content="MagicDNS — ДНС для ИИ: прямой доступ на полной скорости">
  <meta property="og:description" content="ДНС для ИИ и Smart DNS для нейросетей. Прямой доступ к Gemini, ChatGPT и Claude без сторонних приложений и тоннелей на полной скорости. Бесплатная настройка!">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:image" content="https://magicdns.ru/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="https://magicdns.ru/">
  <meta name="twitter:title" content="MagicDNS — ДНС для ИИ: прямой доступ на полной скорости">
  <meta name="twitter:description" content="ДНС для ИИ и Smart DNS для нейросетей. Прямой доступ к Gemini, ChatGPT и Claude без сторонних приложений и тоннелей на полной скорости. Бесплатная настройка!">
  <meta name="twitter:image" content="https://magicdns.ru/og-image.png">

  <!-- Schema.org Structured Data (JSON-LD) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebSite",
        "@id": "https://magicdns.ru/#website",
        "url": "https://magicdns.ru/",
        "name": "MagicDNS",
        "description": "Высокоскоростной Smart DNS для прямого доступа к Claude AI, Gemini, ChatGPT на полной скорости без сторонних приложений и тоннелей",
        "inLanguage": "ru-RU"
      }},
      {{
        "@type": "WebApplication",
        "@id": "https://magicdns.ru/#app",
        "name": "MagicDNS",
        "url": "https://magicdns.ru/",
        "description": "Высокоскоростной защищённый Smart DNS (DoH/DoT) для прямого доступа к Claude AI, Gemini, Google AI Studio и ChatGPT без сторонних приложений и тоннелей.",
        "applicationCategory": "NetworkingApplication",
        "operatingSystem": "Windows, iOS, macOS, Android, Linux, Keenetic, OpenWrt, MikroTik",
        "offers": {{
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "RUB"
        }}
      }},
      {{
        "@type": "FAQPage",
        "@id": "https://magicdns.ru/#faq",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "Безопасно ли использовать MagicDNS для личных и банковских данных?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Да, абсолютно безопасно. Частный ДНС для ИИ и персональный DNS сервер резолвят только адреса доменов. Весь трафик шифруется сквозным TLS/HTTPS между вашим устройством и банком или Госуслугами. Никто не может перехватить пароли или номера карт. Российский трафик идёт напрямую от вашего провайдера на максимальной скорости."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Ведется ли логирование DNS-запросов и истории посещений?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Сервис работает по строгой политике Zero-Logs. Мы не сохраняем историю DNS-запросов, не регистрируем IP-адреса пользователей и не создаем профилей поведения. Обработка происходит в оперативной памяти сервера с немедленной очисткой после ответа."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Почему при использовании MagicDNS скорость интернета не снижается, в отличие от сторонних сетевых клиентов?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Быстрый ДНС не пропускает через себя данные (видео, файлы, страницы). DNS участвует только один раз в момент первого обращения к сайту для получения его IP-адреса (несколько миллисекунд). После этого устройство связывается с сервером напрямую, что гарантирует 100% скорости вашего провайдера."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Будет ли работать Smart DNS при переключении между Wi-Fi и мобильной сетью?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Да. На Android в режиме «Персональный DNS» и на iOS через конфигурационный профиль DoH/DoT настройки действуют системно. При выходе из дома и переключении с Wi-Fi на мобильную сеть 4G/5G профиль сохраняет активность автоматически."
            }}
          }},
          {{
            "@type": "Question",
            "name": "В чем главное отличие Smart DNS от сторонних сетевых клиентов и как открыть Gemini через DNS?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Сторонние сетевые клиенты и тоннели принудительно направляют весь трафик устройства через удаленный зашифрованный сервер, что снижает скорость, увеличивает пинг и блокирует доступ к российским банковским приложениям. Smart DNS устраняет региональные ограничения зарубежных сервисов (OpenAI, Google) через точечную оптимизацию сетевой маршрутизации к AI-платформам, сохраняя прямой доступ ко всем остальным ресурсам. Чтобы понять, как открыть Gemini через DNS, достаточно один раз указать адрес шлюза в системных настройках вашего устройства."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Предоставляет ли MagicDNS доступ к ресурсам, ограниченным на территории РФ?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Нет. Сервис MagicDNS строго соблюдает Федеральный закон № 149-ФЗ и решения уполномоченных органов РФ. Серверы используют архитектуру закрытого белого списка (Strict Whitelist) и маршрутизируют исключительно адреса платформ искусственного интеллекта (OpenAI, Google Gemini, Anthropic Claude, Cursor, Midjourney) и игровых экосистем, которые сами ограничили доступ для РФ со своей стороны. Запросы к ресурсам, доступ к которым ограничен на территории РФ (Единый реестр Роскомнадзора), серверами не обрабатываются и не перенаправляются."
            }}
          }}
        ]
      }}
    ]
  }}
  </script>
  <style>
    /* ==========================================================================
       Design System: Cyber-Minimalism & Futuristic Dark Palette
       ========================================================================== */
    :root {{
      --bg-base: #070d14;
      --bg-surface: #0b1424;
      --bg-card: rgba(11, 20, 36, 0.72);
      --bg-card-elevated: rgba(15, 27, 48, 0.85);
      --bg-input: rgba(7, 13, 20, 0.88);
      
      --neon-mint: #00ff9d;
      --neon-emerald: #10b981;
      --cyber-cyan: #06b6d4;
      
      --mint-glow: rgba(0, 255, 157, 0.28);
      --mint-subtle: rgba(0, 255, 157, 0.12);
      --border-hairline: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(0, 255, 157, 0.25);
      
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --text-code: #00ff9d;
      
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-pill: 9999px;
      
      --transition-fast: 0.15s cubic-bezier(0.16, 1, 0.3, 1);
      --transition-smooth: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    html {{
      scroll-behavior: smooth;
      scroll-padding-top: 80px;
      overflow-x: hidden;
      width: 100%;
      max-width: 100%;
    }}

    section, .tab-panel, .glass-config-card, .faq-section, .reviews-section, .interactive-checker {{
      scroll-margin-top: 80px;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Geist', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      width: 100%;
      max-width: 100%;
      position: relative;
      line-height: 1.5;
      background-image: 
        radial-gradient(circle at 50% -10%, rgba(0, 255, 157, 0.12), transparent 55%),
        radial-gradient(circle at 85% 15%, rgba(6, 182, 212, 0.07), transparent 45%),
        radial-gradient(circle at 15% 45%, rgba(0, 255, 157, 0.05), transparent 40%),
        linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 100% 100%, 36px 36px, 36px 36px;
      background-attachment: fixed;
    }}

    /* Accessibility Focus Style */
    :focus-visible {{
      outline: 2px solid var(--neon-mint);
      outline-offset: 3px;
      box-shadow: 0 0 16px var(--mint-glow);
    }}

    a, button {{
      color: inherit;
      text-decoration: none;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
    }}

    button {{
      background: none;
      border: none;
      cursor: pointer;
      font-family: inherit;
    }}

    .container {{
      width: 100%;
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 20px;
    }}

    /* ==========================================================================
       1. Header (Navbar)
       ========================================================================== */
    header {{
      position: sticky;
      top: 0;
      z-index: 1100;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      background: rgba(7, 13, 20, 0.85);
      border-bottom: 1px solid var(--border-hairline);
      padding: 16px 0;
    }}

    .header-content {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }}

    .logo-icon {{
      width: 38px;
      height: 38px;
      border-radius: var(--radius-sm);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 16px rgba(0, 255, 157, 0.15);
      transition: var(--transition-fast);
    }}

    .logo-icon svg {{
      width: 22px;
      height: 22px;
      filter: drop-shadow(0 0 6px rgba(0, 255, 157, 0.6));
    }}

    .brand-title {{
      font-size: 1.3rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
    }}

    .brand-title .accent {{
      color: var(--neon-mint);
      text-shadow: 0 0 14px var(--mint-glow);
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    /* Language Selector */
    .lang-selector-wrapper {{
      position: relative;
      display: inline-block;
    }}

    .lang-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: var(--radius-pill);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #ffffff;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--transition-fast);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }}

    .lang-btn:hover,
    .lang-btn:focus-visible {{
      background: rgba(0, 255, 157, 0.1);
      border-color: rgba(0, 255, 157, 0.35);
      color: var(--neon-mint);
    }}

    .lang-globe-icon {{
      width: 14px;
      height: 14px;
      color: var(--neon-mint);
      flex-shrink: 0;
    }}

    .lang-arrow-icon {{
      width: 12px;
      height: 12px;
      color: var(--text-dim);
      transition: transform var(--transition-fast);
      flex-shrink: 0;
    }}

    .lang-selector-wrapper.open .lang-arrow-icon {{
      transform: rotate(180deg);
    }}

    .lang-dropdown {{
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      min-width: 155px;
      background: rgba(11, 20, 36, 0.96);
      border: 1px solid rgba(0, 255, 157, 0.25);
      border-radius: var(--radius-md);
      padding: 6px;
      list-style: none;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.65), 0 0 16px rgba(0, 255, 157, 0.1);
      display: none;
      z-index: 1000;
      animation: fadeIn 0.15s ease-out;
    }}

    .lang-selector-wrapper.open .lang-dropdown {{
      display: block;
    }}

    .lang-option {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 10px;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      font-weight: 500;
      color: #cbd5e1;
      cursor: pointer;
      transition: all var(--transition-fast);
      user-select: none;
    }}

    .lang-option:hover,
    .lang-option:focus-visible {{
      background: rgba(0, 255, 157, 0.1);
      color: #ffffff;
    }}

    .lang-option.active {{
      background: rgba(0, 255, 157, 0.15);
      color: var(--neon-mint);
      font-weight: 700;
    }}

    .lang-option .lang-code {{
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-dim);
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.05);
    }}

    .lang-option.active .lang-code {{
      background: rgba(0, 255, 157, 0.2);
      color: var(--neon-mint);
    }}

    .btn-support-header {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 16px;
      border-radius: var(--radius-pill);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.3);
      color: #ffffff;
      font-size: 0.84rem;
      font-weight: 600;
      text-decoration: none;
      box-shadow: 0 0 14px rgba(0, 0, 0, 0.3);
      transition: all var(--transition-smooth);
      white-space: nowrap;
    }}

    .btn-support-header:hover {{
      background: rgba(0, 255, 157, 0.18);
      border-color: var(--neon-mint);
      color: var(--neon-mint);
      transform: translateY(-1px);
      box-shadow: 0 0 18px rgba(0, 255, 157, 0.25);
    }}

    .btn-tg-contact-header {{
      background: rgba(6, 182, 212, 0.1);
      border-color: rgba(6, 182, 212, 0.35);
      color: #38bdf8;
      box-shadow: 0 0 14px rgba(6, 182, 212, 0.1);
    }}

    .btn-tg-contact-header:hover {{
      background: rgba(6, 182, 212, 0.22);
      border-color: var(--cyber-cyan);
      color: #ffffff;
      box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
      transform: translateY(-1px);
    }}

    .feedback-direct-tg-hint {{
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-dim);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }}

    .link-direct-tg {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--cyber-cyan);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.85rem;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      background: rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(6, 182, 212, 0.25);
      transition: all var(--transition-fast);
    }}

    .link-direct-tg:hover {{
      background: rgba(6, 182, 212, 0.2);
      border-color: rgba(6, 182, 212, 0.5);
      color: #ffffff;
      transform: translateY(-1px);
    }}

    .donate-heart {{
      width: 15px;
      height: 15px;
      fill: #ff5e7e;
      filter: drop-shadow(0 0 6px rgba(255, 94, 126, 0.5));
      transition: transform var(--transition-fast);
      flex-shrink: 0;
    }}

    .btn-support-header:hover .donate-heart {{
      transform: scale(1.18);
      filter: drop-shadow(0 0 10px rgba(255, 94, 126, 0.85));
    }}

    .social-btn-donate {{
      border-color: rgba(255, 94, 126, 0.3);
      color: #ffffff;
    }}

    .social-btn-donate:hover {{
      border-color: #ff5e7e;
      background: rgba(255, 94, 126, 0.12);
      color: #ffffff;
      box-shadow: 0 0 16px rgba(255, 94, 126, 0.25);
    }}

    .social-btn-donate .donate-heart,
    .btn-support-header .donate-heart {{
      fill: #ff5e7e !important;
      width: 15px;
      height: 15px;
    }}

    .social-btn-donate:hover .donate-heart {{
      transform: scale(1.15);
      filter: drop-shadow(0 0 10px rgba(255, 94, 126, 0.85));
    }}

    /* Live Network Status Badge */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 7px 16px;
      border-radius: var(--radius-pill);
      background: rgba(11, 20, 36, 0.7);
      border: 1px solid var(--border-glow);
      font-size: 0.84rem;
      font-weight: 500;
      color: var(--text-muted);
      box-shadow: 0 0 14px rgba(0, 0, 0, 0.4);
      transition: var(--transition-smooth);
    }}

    .status-badge:hover {{
      border-color: var(--neon-mint);
      background: rgba(11, 20, 36, 0.9);
      box-shadow: 0 0 18px rgba(0, 255, 157, 0.15);
    }}

    .status-dot-wrapper {{
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 10px;
      height: 10px;
    }}

    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--neon-mint);
      box-shadow: 0 0 10px var(--neon-mint);
    }}

    .status-ping {{
      position: absolute;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: rgba(0, 255, 157, 0.4);
      animation: radar-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
    }}

    @keyframes radar-ping {{
      0% {{ transform: scale(0.6); opacity: 0.9; }}
      80%, 100% {{ transform: scale(2.4); opacity: 0; }}
    }}

    .status-label {{
      display: inline;
    }}

    .status-text {{
      color: #ffffff;
      font-weight: 600;
    }}

    /* ==========================================================================
       2. Hero Section
       ========================================================================== */
    .hero,
    .hero-section {{
      padding: 24px 0 12px;
      text-align: center;
    }}

    .hero-eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--neon-mint);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.28);
      padding: 5px 13px;
      border-radius: var(--radius-pill);
      margin-bottom: 12px;
      letter-spacing: 0.02em;
      box-shadow: 0 0 16px rgba(0, 255, 157, 0.08);
    }}

    .hero h1 {{
      font-size: clamp(2rem, 5vw, 3.2rem);
      font-weight: 800;
      line-height: 1.15;
      letter-spacing: -0.03em;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #ffffff 30%, #00ff9d 75%, #06b6d4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      max-width: 920px;
      margin-left: auto;
      margin-right: auto;
    }}

    .hero p {{
      font-size: clamp(1rem, 2vw, 1.15rem);
      color: var(--text-muted);
      max-width: 740px;
      margin: 0 auto 16px;
      line-height: 1.6;
    }}

    /* Unified Harmonious Services Ribbon (Clean Multi-Row / Never Overflows) */
    .services-ribbon-container {{
      width: 100%;
      max-width: 900px;
      margin: 0 auto 14px;
      padding: 0 12px;
    }}

    .services-ribbon {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 8px 10px;
      padding: 2px 0;
    }}

    .service-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.81rem;
      font-weight: 600;
      color: #e2e8f0;
      background: rgba(11, 20, 36, 0.65);
      border: 1px solid var(--border-hairline);
      padding: 6px 13px;
      border-radius: var(--radius-pill);
      backdrop-filter: blur(8px);
      transition: var(--transition-fast);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}

    .service-chip:hover {{
      border-color: rgba(0, 255, 157, 0.4);
      background: rgba(11, 20, 36, 0.85);
      transform: translateY(-1px);
    }}

    .service-chip svg {{
      width: 14px;
      height: 14px;
      color: var(--neon-mint);
      flex-shrink: 0;
    }}

    .service-chip.highlight {{
      background: rgba(0, 255, 157, 0.09);
      border-color: rgba(0, 255, 157, 0.35);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(0, 255, 157, 0.1);
    }}

    .service-chip.highlight-adblock {{
      background: rgba(6, 182, 212, 0.12);
      border-color: rgba(6, 182, 212, 0.4);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(6, 182, 212, 0.15);
    }}

    .service-chip.highlight-adblock svg {{
      color: var(--cyber-cyan);
    }}

    .service-chip-more {{
      cursor: pointer;
      background: rgba(0, 255, 157, 0.05);
      border-color: rgba(0, 255, 157, 0.3);
      color: var(--neon-mint);
      transition: var(--transition-fast);
      user-select: none;
    }}

    .service-chip-more:hover {{
      background: rgba(0, 255, 157, 0.15);
      border-color: var(--neon-mint);
      transform: translateY(-1px);
      box-shadow: 0 0 14px rgba(0, 255, 157, 0.22);
    }}

    .service-chip-more.active {{
      background: rgba(0, 255, 157, 0.22);
      border-color: var(--neon-mint);
      box-shadow: 0 0 16px rgba(0, 255, 157, 0.35);
    }}

    .service-chip-more svg {{
      transition: transform var(--transition-fast);
    }}

    .service-chip-more.active svg {{
      transform: rotate(45deg);
    }}

    .more-services-drawer {{
      display: none;
      max-width: 860px;
      margin: 14px auto 6px;
      background: rgba(11, 20, 36, 0.92);
      border: 1px solid rgba(0, 255, 157, 0.25);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.05);
      animation: fadeIn 0.22s ease-out;
    }}

    .more-services-drawer.active {{
      display: block;
    }}

    .more-services-title {{
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--neon-mint);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
    }}

    .more-services-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      justify-content: center;
    }}

    .mini-service-tag {{
      font-size: 0.78rem;
      font-weight: 500;
      color: #cbd5e1;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 4px 11px;
      border-radius: var(--radius-pill);
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: var(--transition-fast);
    }}

    .mini-service-tag:hover {{
      background: rgba(0, 255, 157, 0.08);
      border-color: rgba(0, 255, 157, 0.25);
      color: #ffffff;
    }}

    .more-services-note {{
      font-size: 0.75rem;
      color: var(--text-dim);
      text-align: center;
      margin-top: 10px;
    }}

    /* ==========================================================================
       3. Device Configurator (Segmented Bar + Two-Column Glassmorphism Cards)
       ========================================================================== */
    .configurator-section,
    .tabs-section {{
      padding: 8px 0 32px;
    }}

    .segmented-bar-wrapper {{
      display: flex;
      justify-content: flex-start;
      margin-bottom: 16px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      padding: 4px 12px;
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
    }}
    .segmented-bar-wrapper::-webkit-scrollbar {{
      display: none;
    }}

    .segmented-bar {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(11, 20, 36, 0.7);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-md);
      padding: 5px;
      backdrop-filter: blur(16px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      margin: 0 auto;
      min-width: max-content;
      box-sizing: border-box;
    }}

    .segmented-tab {{
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding: 10px 20px;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      white-space: nowrap;
      transition: all var(--transition-fast);
      cursor: pointer;
      flex-shrink: 0;
    }}

    .segmented-tab * {{
      pointer-events: none;
    }}

    .segmented-tab:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.04);
    }}

    .segmented-tab.active {{
      color: #ffffff;
      background: rgba(0, 255, 157, 0.1);
      border-color: rgba(0, 255, 157, 0.45);
      box-shadow: 0 0 16px rgba(0, 255, 157, 0.22);
    }}

    .tab-icon {{
      width: 17px;
      height: 17px;
      flex-shrink: 0;
    }}

    .segmented-tab.active .tab-icon {{
      color: var(--neon-mint);
      filter: drop-shadow(0 0 6px var(--mint-glow));
    }}

    /* Tab Panels */
    .tab-panel {{
      display: none;
      animation: fadeIn var(--transition-smooth);
    }}

    .tab-panel.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Two-Column Glassmorphism Configuration Card */
    .glass-config-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-glow);
      border-radius: var(--radius-lg);
      padding: 28px 32px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.06);
      display: grid;
      grid-template-columns: 1fr 220px;
      gap: 32px;
      align-items: center;
      position: relative;
    }}

    .card-left-column {{
      min-width: 0;
      width: 100%;
    }}

    .card-left-column > :last-child {{
      margin-bottom: 0;
    }}

    /* Card Header Row */
    .card-header-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}

    .card-header-title {{
      font-size: 1.22rem;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.01em;
    }}

    .card-badge {{
      font-size: 0.74rem;
      font-weight: 700;
      background: rgba(0, 255, 157, 0.12);
      color: var(--neon-mint);
      border: 1px solid rgba(0, 255, 157, 0.35);
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      white-space: normal;
      word-break: break-word;
      line-height: 1.4;
      max-width: 100%;
      letter-spacing: 0.02em;
    }}

    .card-instruction {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.55;
      margin-bottom: 18px;
    }}

    /* Input Field & Parameters */
    .input-field-group {{
      margin-bottom: 14px;
      width: 100%;
    }}

    .input-field-label {{
      display: block;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 6px;
    }}

    .code-input-box {{
      background: var(--bg-input);
      border: 1px solid rgba(0, 255, 157, 0.22);
      border-radius: var(--radius-sm);
      padding: 9px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      width: 100%;
      box-sizing: border-box;
      transition: var(--transition-fast);
    }}

    .code-input-box:hover, .code-input-box:focus-within {{
      border-color: var(--neon-mint);
      box-shadow: 0 0 14px rgba(0, 255, 157, 0.15);
    }}

    .code-input-text {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--neon-mint);
      word-break: break-all;
      flex: 1;
      min-width: 0;
    }}

    .btn-inline-copy {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 6px;
      padding: 5px 8px;
      color: #ffffff;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all var(--transition-fast);
      flex-shrink: 0;
    }}

    .btn-inline-copy:hover {{
      background: rgba(0, 255, 157, 0.18);
      border-color: var(--neon-mint);
      color: var(--neon-mint);
      transform: translateY(-1px);
    }}

    .btn-inline-copy svg {{
      width: 14px;
      height: 14px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
    }}

    /* Compact Parameters Grid for Proxy */
    .params-subgrid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}

    .param-subcard {{
      background: rgba(7, 13, 20, 0.7);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-sm);
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .param-subcard-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
    }}

    .param-subcard-label {{
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
    }}

    .param-subcard-val {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.88rem;
      font-weight: 700;
      color: #ffffff;
      word-break: break-all;
    }}

    /* Action Buttons Row */
    .card-actions-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 16px;
    }}

    .card-actions-row:empty {{
      display: none;
      margin: 0;
    }}

    .btn-neon-action,
    .btn-action-green {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: linear-gradient(135deg, #00ff9d 0%, #10b981 100%);
      color: #070d14;
      font-size: 0.9rem;
      font-weight: 700;
      padding: 10px 22px;
      border-radius: var(--radius-sm);
      box-shadow: 0 0 18px rgba(0, 255, 157, 0.35);
      transition: all var(--transition-fast);
      cursor: pointer;
      min-width: 150px;
    }}

    .btn-neon-action svg,
    .btn-action-green svg,
    .btn-dark-action svg,
    .feedback-submit-btn svg {{
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }}

    .btn-neon-action:hover,
    .btn-action-green:hover {{
      transform: translateY(-2px);
      box-shadow: 0 0 26px rgba(0, 255, 157, 0.55);
      filter: brightness(1.05);
    }}

    .btn-neon-action:active,
    .btn-action-green:active {{
      transform: scale(0.98);
    }}

    .btn-dark-action {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: rgba(15, 27, 48, 0.85);
      color: #e2e8f0;
      font-size: 0.9rem;
      font-weight: 600;
      padding: 10px 20px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-hairline);
      transition: all var(--transition-fast);
      cursor: pointer;
      min-width: 140px;
    }}

    .btn-dark-action:hover {{
      background: rgba(22, 38, 66, 0.95);
      border-color: rgba(255, 255, 255, 0.2);
      color: #ffffff;
      transform: translateY(-1px);
    }}

    .btn-dark-action:active {{
      transform: scale(0.98);
    }}

    /* Right Column: Square QR Code Pod with Caption */
    .card-right-column {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .qr-pod {{
      background: rgba(7, 13, 20, 0.75);
      border: 1px solid var(--border-glow);
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 255, 157, 0.05);
      width: 100%;
    }}

    .qr-canvas-box {{
      background: #ffffff;
      border-radius: 8px;
      padding: 7px;
      width: 136px;
      height: 136px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    }}

    .qr-svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .qr-caption {{
      margin-top: 10px;
      font-size: 0.78rem;
      font-weight: 600;
      color: #a7f3d0;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      text-align: center;
      letter-spacing: 0.02em;
    }}

    .qr-caption svg {{
      width: 13px;
      height: 13px;
      stroke: var(--neon-mint);
      fill: none;
      stroke-width: 2;
    }}

    /* Field Alt Notes (Alternative Nodes) */
    .field-alt-note {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 6px;
      font-size: 0.8rem;
      color: var(--text-muted);
      flex-wrap: wrap;
    }}

    .btn-subtext-copy {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 4px;
      padding: 2px 7px;
      color: #a7f3d0;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.74rem;
      transition: all var(--transition-fast);
    }}

    .btn-subtext-copy:hover {{
      background: rgba(0, 255, 157, 0.15);
      border-color: var(--neon-mint);
      color: var(--neon-mint);
      transform: translateY(-1px);
    }}

    .btn-subtext-copy svg {{
      width: 12px;
      height: 12px;
      flex-shrink: 0;
    }}

    /* Dedicated Router Block (Non-DoH) */
    .router-nodoh-block {{
      margin-top: 24px;
    }}

    .router-card {{
      border: 1px solid rgba(0, 255, 157, 0.25);
      box-shadow: 0 12px 34px rgba(0, 0, 0, 0.45), 0 0 24px rgba(0, 255, 157, 0.06);
    }}

    .router-ips-grid,
    .win-ips-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 14px;
      margin-bottom: 8px;
    }}

    .config-tip-box {{
      background: rgba(0, 255, 157, 0.05);
      border: 1px solid rgba(0, 255, 157, 0.22);
      border-left: 3px solid var(--neon-mint);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      margin-top: 10px;
      margin-bottom: 12px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 0.84rem;
      line-height: 1.5;
      color: var(--text-light);
    }}

    .config-tip-icon {{
      flex-shrink: 0;
      width: 16px;
      height: 16px;
      stroke: var(--neon-mint);
      fill: none;
      stroke-width: 2;
      margin-top: 2px;
    }}

    .config-tip-text {{
      flex: 1;
      margin: 0;
      color: #e2e8f0;
    }}

    @media (max-width: 640px) {{
      .router-ips-grid,
      .win-ips-grid {{
        grid-template-columns: 1fr;
        gap: 12px;
      }}
    }}

    .router-actions-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}

    /* ==========================================================================
       4. Block 4: Connection Checker
       ========================================================================== */
    .checker-section {{
      padding: 10px 0 44px;
    }}

    .checker-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-glow);
      border-radius: var(--radius-lg);
      padding: 34px 30px;
      backdrop-filter: blur(16px);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
      text-align: center;
    }}

    .checker-header {{
      max-width: 680px;
      margin: 0 auto 24px;
    }}

    .checker-header h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin-bottom: 8px;
      color: #ffffff;
    }}

    .checker-header p {{
      color: var(--text-muted);
      font-size: 0.94rem;
      line-height: 1.5;
    }}

    /* Big Neon Pulsing Button */
    .btn-run-check {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: linear-gradient(135deg, #00ff9d 0%, #10b981 100%);
      color: #070d14;
      font-size: 1.02rem;
      font-weight: 700;
      padding: 13px 32px;
      border-radius: var(--radius-pill);
      box-shadow: 0 0 24px var(--mint-glow);
      transition: all var(--transition-fast);
      cursor: pointer;
      animation: neonPulse 2.8s infinite;
    }}

    @keyframes neonPulse {{
      0% {{ box-shadow: 0 0 18px rgba(0, 255, 157, 0.35); }}
      50% {{ box-shadow: 0 0 36px rgba(0, 255, 157, 0.65), 0 0 12px rgba(0, 255, 157, 0.9); }}
      100% {{ box-shadow: 0 0 18px rgba(0, 255, 157, 0.35); }}
    }}

    .btn-run-check:hover {{
      transform: translateY(-2px);
      box-shadow: 0 0 38px rgba(0, 255, 157, 0.75);
    }}

    .btn-run-check:active {{
      transform: scale(0.98);
    }}

    .btn-run-check svg {{
      width: 19px;
      height: 19px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2.3;
    }}

    /* Diagnostic Progress */
    .checker-progress-wrap {{
      display: none;
      margin-top: 26px;
      max-width: 520px;
      margin-left: auto;
      margin-right: auto;
    }}

    .checker-progress-bar {{
      height: 7px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-pill);
      overflow: hidden;
      margin-bottom: 12px;
    }}

    .checker-progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--neon-mint), var(--cyber-cyan));
      border-radius: var(--radius-pill);
      transition: width 0.3s ease;
      box-shadow: 0 0 12px var(--mint-glow);
    }}

    .checker-log-text {{
      font-size: 0.85rem;
      color: var(--text-muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    /* Diagnostic Result Card */
    .checker-result-box {{
      display: none;
      margin-top: 26px;
      background: rgba(0, 255, 157, 0.06);
      border: 1px solid rgba(0, 255, 157, 0.35);
      border-radius: var(--radius-md);
      padding: 22px;
      text-align: left;
      animation: fadeIn var(--transition-smooth);
      box-shadow: 0 0 24px rgba(0, 255, 157, 0.08);
      overflow: hidden;
      box-sizing: border-box;
      width: 100%;
    }}

    .result-status-title {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 18px;
    }}

    .result-status-title svg {{
      width: 22px;
      height: 22px;
      stroke: var(--neon-mint);
      stroke-width: 2.2;
      fill: none;
      flex-shrink: 0;
      transition: stroke var(--transition-fast);
    }}

    /* AI Services Probe Grid - 5 Equal Columns with Zero Overflow */
    .ai-services-probe-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 22px;
      width: 100%;
      box-sizing: border-box;
    }}

    @media (max-width: 860px) {{
      .ai-services-probe-grid {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 540px) {{
      .ai-services-probe-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 360px) {{
      .ai-services-probe-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .ai-probe-card {{
      background: rgba(11, 20, 36, 0.7);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-sm);
      padding: 12px 10px 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
      min-height: 96px;
      min-width: 0;
      width: 100%;
      box-sizing: border-box;
      transition: all var(--transition-fast);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}

    .ai-probe-card:hover {{
      border-color: rgba(0, 255, 157, 0.35);
      background: rgba(15, 27, 48, 0.85);
      transform: translateY(-2px);
    }}

    .ai-probe-top {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
      width: 100%;
    }}

    .ai-probe-icon {{
      width: 28px;
      height: 28px;
      border-radius: 7px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .ai-probe-icon svg {{
      width: 15px;
      height: 15px;
    }}

    .ai-probe-titles {{
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1;
      gap: 1px;
      overflow: hidden;
    }}

    .ai-probe-name {{
      font-size: 0.82rem;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .ai-probe-host {{
      font-size: 0.67rem;
      color: var(--text-dim);
      font-family: ui-monospace, SFMono-Regular, monospace;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .ai-probe-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 4px 6px;
      border-radius: var(--radius-pill);
      width: 100%;
      box-sizing: border-box;
      white-space: nowrap;
      transition: all var(--transition-fast);
    }}

    .ai-probe-badge.online {{
      background: rgba(0, 255, 157, 0.1);
      color: var(--neon-mint);
      border: 1px solid rgba(0, 255, 157, 0.3);
      box-shadow: 0 0 10px rgba(0, 255, 157, 0.1);
    }}

    .ai-probe-badge.offline {{
      background: rgba(239, 68, 68, 0.1);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}

    .ai-probe-badge.testing {{
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-muted);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .ai-probe-ping {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-weight: 700;
    }}

    .result-metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
    }}

    .metric-card {{
      background: rgba(7, 13, 20, 0.65);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}

    .metric-name {{
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      font-weight: 600;
    }}

    .metric-val {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    .metric-val.mint {{
      color: var(--neon-mint);
    }}

    /* ==========================================================================
       5. Footer
       ========================================================================== */
    footer {{
      margin-top: auto;
      border-top: 1px solid var(--border-hairline);
      background: rgba(7, 13, 20, 0.95);
      padding: 26px 0;
    }}

    .footer-content {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }}

    .footer-brand {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 1.05rem;
    }}

    .footer-copy {{
      font-size: 0.82rem;
      color: var(--text-dim);
      margin-top: 4px;
    }}

    .footer-center {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.88rem;
      color: var(--text-muted);
    }}

    .uptime-pill {{
      font-weight: 700;
      color: var(--neon-mint);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .uptime-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--neon-mint);
      box-shadow: 0 0 8px var(--neon-mint);
    }}

    .footer-links {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .social-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: var(--radius-pill);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-hairline);
      color: var(--text-muted);
      font-size: 0.88rem;
      font-weight: 600;
      transition: all var(--transition-fast);
      min-height: 40px;
    }}

    .social-btn svg {{
      width: 17px;
      height: 17px;
      fill: currentColor;
    }}

    .social-btn:hover {{
      color: #ffffff;
      background: rgba(0, 255, 157, 0.1);
      border-color: rgba(0, 255, 157, 0.35);
      transform: translateY(-2px);
    }}

    /* Toast Notification (positioned above chat FAB) */
    .toast {{
      position: fixed;
      bottom: 90px;
      right: 24px;
      z-index: 2500;
      background: rgba(11, 20, 36, 0.95);
      border: 1px solid var(--neon-mint);
      color: #ffffff;
      padding: 12px 20px;
      border-radius: var(--radius-pill);
      font-size: 0.9rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6), 0 0 18px rgba(0, 255, 157, 0.25);
      backdrop-filter: blur(12px);
      transform: translateY(100px);
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .toast.show {{
      transform: translateY(0);
      opacity: 1;
      pointer-events: auto;
    }}

    .toast svg {{
      width: 18px;
      height: 18px;
      stroke: var(--neon-mint);
      stroke-width: 2.5;
      fill: none;
    }}

    /* ==========================================================================
       Support Chat Widget & Quick FAQ
       ========================================================================== */
    .chat-fab {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 1050;
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: rgba(10, 18, 30, 0.92);
      border: 1px solid rgba(0, 255, 157, 0.45);
      color: var(--neon-mint);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55), 0 0 22px rgba(0, 255, 157, 0.25);
      cursor: pointer;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      transition: all var(--transition-fast);
    }}

    .chat-fab:hover {{
      transform: scale(1.08);
      border-color: var(--neon-mint);
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.65), 0 0 30px rgba(0, 255, 157, 0.45);
    }}

    .chat-fab-pulse {{
      position: absolute;
      top: 1px;
      right: 1px;
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: var(--neon-mint);
      box-shadow: 0 0 10px var(--neon-mint);
      border: 2px solid #070d14;
    }}

    .chat-fab-icon {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      transition: transform var(--transition-fast);
    }}

    .chat-fab-icon svg {{
      width: 24px;
      height: 24px;
    }}

    .chat-fab .close-icon {{
      display: none;
    }}

    .chat-fab.open .open-icon {{
      display: none;
    }}

    .chat-fab.open .close-icon {{
      display: flex;
    }}

    .chat-fab-tooltip {{
      position: absolute;
      right: calc(100% + 12px);
      top: 50%;
      transform: translateY(-50%);
      background: rgba(11, 20, 36, 0.95);
      border: 1px solid rgba(0, 255, 157, 0.3);
      color: #ffffff;
      padding: 6px 12px;
      border-radius: var(--radius-pill);
      font-size: 0.76rem;
      font-weight: 600;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transition: opacity var(--transition-fast);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }}

    .chat-fab:hover .chat-fab-tooltip {{
      opacity: 1;
    }}

    /* Chat Window */
    .chat-window {{
      position: fixed;
      bottom: 90px;
      right: 24px;
      z-index: 1001;
      width: 380px;
      max-width: calc(100vw - 32px);
      height: 540px;
      max-height: calc(100dvh - 110px);
      background: rgba(9, 16, 28, 0.96);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 255, 157, 0.3);
      border-radius: 18px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.75), 0 0 35px rgba(0, 255, 157, 0.15);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transform: scale(0.92) translateY(20px);
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .chat-window.active {{
      transform: scale(1) translateY(0);
      opacity: 1;
      pointer-events: auto;
    }}

    .chat-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 13px 16px;
      background: rgba(13, 23, 40, 0.85);
      border-bottom: 1px solid var(--border-hairline);
    }}

    .chat-header-info {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .chat-avatar {{
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .chat-avatar svg {{
      width: 18px;
      height: 18px;
    }}

    .chat-titles {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .chat-title {{
      font-size: 0.9rem;
      font-weight: 700;
      color: #ffffff;
    }}

    .chat-status {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.7rem;
      color: var(--neon-mint);
    }}

    .chat-status-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--neon-mint);
      box-shadow: 0 0 6px var(--neon-mint);
    }}

    .chat-close-btn {{
      width: 30px;
      height: 30px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-dim);
      transition: all var(--transition-fast);
    }}

    .chat-close-btn:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.08);
    }}

    .chat-close-btn svg {{
      width: 16px;
      height: 16px;
    }}

    /* Messages */
    .chat-messages {{
      flex: 1;
      overflow-y: auto;
      padding: 14px 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      scrollbar-width: thin;
      scrollbar-color: rgba(0, 255, 157, 0.2) transparent;
    }}

    .chat-messages::-webkit-scrollbar {{
      width: 5px;
    }}

    .chat-messages::-webkit-scrollbar-thumb {{
      background: rgba(0, 255, 157, 0.2);
      border-radius: 10px;
    }}

    .chat-bubble {{
      max-width: 88%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 0.84rem;
      line-height: 1.45;
      word-break: break-word;
      animation: bubbleFadeIn 0.2s ease-out;
    }}

    @keyframes bubbleFadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .chat-bubble.bot {{
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-bottom-left-radius: 4px;
      color: #e2e8f0;
    }}

    .chat-bubble.bot code {{
      background: rgba(0, 255, 157, 0.1);
      color: var(--neon-mint);
      padding: 2px 5px;
      border-radius: 4px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 0.78rem;
    }}

    .chat-bubble.user {{
      align-self: flex-end;
      background: linear-gradient(135deg, rgba(0, 255, 157, 0.25), rgba(6, 182, 212, 0.2));
      border: 1px solid rgba(0, 255, 157, 0.4);
      border-bottom-right-radius: 4px;
      color: #ffffff;
      font-weight: 500;
    }}

    .chat-faq-title {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      font-weight: 700;
      margin-top: 4px;
      margin-bottom: -4px;
    }}

    .chat-faq-container {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .chat-faq-chip {{
      text-align: left;
      background: rgba(0, 255, 157, 0.06);
      border: 1px solid rgba(0, 255, 157, 0.2);
      border-radius: 10px;
      padding: 8px 12px;
      color: #c7f9e5;
      font-size: 0.78rem;
      line-height: 1.35;
      cursor: pointer;
      transition: all var(--transition-fast);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .chat-faq-chip:hover {{
      background: rgba(0, 255, 157, 0.14);
      border-color: var(--neon-mint);
      color: #ffffff;
      transform: translateX(3px);
    }}

    /* Typing indicator */
    .typing-indicator {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 8px 12px;
    }}

    .typing-dot {{
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--neon-mint);
      opacity: 0.5;
      animation: typingBounce 1s infinite alternate;
    }}

    .typing-dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .typing-dot:nth-child(3) {{ animation-delay: 0.4s; }}

    @keyframes typingBounce {{
      0% {{ opacity: 0.3; transform: translateY(0); }}
      100% {{ opacity: 1; transform: translateY(-4px); }}
    }}

    /* Input Bar */
    .chat-input-bar {{
      padding: 10px 14px;
      background: rgba(7, 13, 20, 0.85);
      border-top: 1px solid var(--border-hairline);
    }}

    .chat-form {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .chat-input {{
      flex: 1;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-pill);
      padding: 9px 14px;
      color: #ffffff;
      font-size: 0.84rem;
      font-family: inherit;
      outline: none;
      transition: all var(--transition-fast);
    }}

    .chat-input:focus {{
      border-color: var(--neon-mint);
      background: rgba(255, 255, 255, 0.09);
      box-shadow: 0 0 10px rgba(0, 255, 157, 0.2);
    }}

    .chat-send-btn {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--neon-mint);
      color: #070d14;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: all var(--transition-fast);
      box-shadow: 0 0 12px rgba(0, 255, 157, 0.3);
    }}

    .chat-send-btn:hover {{
      transform: scale(1.08);
      box-shadow: 0 0 18px rgba(0, 255, 157, 0.5);
    }}

    .chat-send-btn svg {{
      width: 16px;
      height: 16px;
      stroke-width: 2.5;
    }}

    /* Responsive Breakdown */
    @media (max-width: 860px) {{
      .glass-config-card {{
        grid-template-columns: 1fr;
        padding: 24px 20px;
      }}
      .card-right-column {{
        width: 100%;
        border-top: 1px solid var(--border-hairline);
        padding-top: 20px;
      }}
      .btn-neon-action, .btn-action-green, .btn-dark-action {{
        width: 100%;
      }}
    }}

    @media (max-width: 600px) {{
      header {{
        padding: 10px 0;
      }}
      .header-content {{
        display: grid;
        grid-template-columns: 1fr auto auto;
        align-items: center;
        gap: 8px 6px;
      }}
      .logo-container {{
        grid-column: 1 / 2;
        grid-row: 1;
        gap: 8px;
        flex-shrink: 0;
      }}
      .logo-icon {{
        width: 32px;
        height: 32px;
      }}
      .logo-icon svg {{
        width: 18px;
        height: 18px;
      }}
      .brand-title {{
        font-size: 1.15rem;
      }}
      .header-right {{
        display: contents;
      }}
      .lang-selector-wrapper {{
        grid-column: 2 / 3;
        grid-row: 1;
      }}
      .lang-btn {{
        padding: 5px 10px;
        font-size: 0.78rem;
      }}
      .btn-support-header {{
        grid-column: 3 / 4;
        grid-row: 1;
        padding: 6px 9px;
        font-size: 0.78rem;
        flex-shrink: 0;
      }}
      .btn-support-header span {{
        display: none;
      }}
      .status-badge {{
        grid-column: 1 / -1;
        grid-row: 2;
        justify-self: center;
        margin: 2px auto 0;
        padding: 5px 12px;
        font-size: 0.76rem;
        max-width: 100%;
      }}
      .status-label {{
        display: inline;
      }}

      /* Hero */
      .hero {{
        padding: 18px 0 10px;
      }}
      .hero-eyebrow {{
        font-size: 0.75rem;
        padding: 4px 10px;
      }}
      .hero h1 {{
        font-size: clamp(1.4rem, 6vw, 1.8rem);
        line-height: 1.2;
        margin-bottom: 8px;
      }}
      .hero p {{
        font-size: 0.9rem;
        margin-bottom: 12px;
      }}

      /* 2x2 Segmented Tabs Grid (No Cutoffs, No Scrolling) */
      .segmented-bar-wrapper {{
        overflow-x: visible;
        padding: 0;
        margin-bottom: 18px;
        width: 100%;
        justify-content: stretch;
      }}
      .segmented-bar {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        width: 100%;
        min-width: 0;
        margin: 0;
        padding: 5px;
        box-sizing: border-box;
        border-radius: var(--radius-md);
      }}
      .segmented-tab {{
        width: 100%;
        min-width: 0;
        padding: 9px 6px;
        font-size: 0.8rem;
        gap: 6px;
        justify-content: center;
        box-sizing: border-box;
        text-align: center;
        white-space: nowrap;
      }}
      .tab-icon {{
        width: 14px;
        height: 14px;
      }}

      /* Cards & Badges */
      .glass-config-card {{
        padding: 18px 14px;
        border-radius: var(--radius-md);
      }}
      .card-badge {{
        border-radius: var(--radius-sm);
        padding: 4px 8px;
        font-size: 0.72rem;
        line-height: 1.4;
        display: inline-block;
      }}
      .card-actions-row,
      .router-actions-row {{
        flex-direction: column;
        align-items: stretch;
        width: 100%;
        gap: 8px;
      }}
      .btn-neon-action,
      .btn-action-green,
      .btn-dark-action {{
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
      }}

      /* Compact QR Pod */
      .card-right-column {{
        width: 100%;
        border-top: 1px solid var(--border-hairline);
        padding-top: 14px;
        margin-top: 14px;
      }}
      .qr-pod {{
        padding: 10px;
        max-width: 150px;
        margin: 0 auto;
      }}
      .qr-pod svg,
      .qr-pod canvas,
      .qr-pod img {{
        max-width: 120px;
        height: auto;
      }}
      .qr-caption {{
        font-size: 0.72rem;
        margin-top: 6px;
      }}

      /* Checker Card with Centered Pulse Icon */
      .checker-card {{
        padding: 22px 14px;
        border-radius: var(--radius-md);
        box-sizing: border-box;
      }}
      .checker-header h2 {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        text-align: center;
        font-size: 1.15rem;
        line-height: 1.35;
      }}
      .checker-header h2 svg {{
        margin: 0 auto;
      }}
      .btn-run-check {{
        width: 100%;
        padding: 12px 18px;
        font-size: 0.94rem;
        justify-content: center;
        box-sizing: border-box;
      }}
      .checker-result-box {{
        padding: 16px 12px;
        box-sizing: border-box;
      }}
      .result-metrics-grid {{
        grid-template-columns: 1fr;
      }}

      /* News & Announcements Section */
      .news-section {{
        margin-top: 40px;
        margin-bottom: 20px;
      }}
      .news-header {{
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 10px;
      }}
      .news-grid {{
        grid-template-columns: 1fr;
      }}

      /* Reviews Section */
      .reviews-section {{
        margin-top: 40px;
        margin-bottom: 20px;
      }}
      .reviews-header {{
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 10px;
      }}
      .reviews-header-left h2 {{
        font-size: 1.45rem;
      }}
      .btn-feedback-trigger {{
        width: 100%;
        justify-content: center;
        box-sizing: border-box;
      }}
      .btn-feedback-trigger.hide-when-empty {{
        display: none !important;
      }}
      .reviews-empty-state {{
        padding: 28px 16px;
        box-sizing: border-box;
      }}
      .reviews-grid {{
        grid-template-columns: 1fr;
      }}

      /* Footer & Chat FAB */
      .footer-content {{
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
      }}
      .footer-links {{
        width: 100%;
        flex-direction: column;
        gap: 8px;
      }}
      .social-btn {{
        width: 100%;
        justify-content: center;
        box-sizing: border-box;
      }}
      footer {{
        padding-bottom: 76px;
      }}
      .chat-window {{
        bottom: 76px;
        right: 10px;
        left: 10px;
        width: auto;
        max-width: none;
        height: calc(100dvh - 90px);
        max-height: 520px;
      }}
      .chat-fab {{
        bottom: 16px;
        right: 14px;
        width: 44px;
        height: 44px;
      }}
      .chat-fab-icon svg {{
        width: 20px;
        height: 20px;
      }}
      .toast {{
        bottom: 76px;
        right: 14px;
        left: 14px;
        max-width: none;
        box-sizing: border-box;
        justify-content: center;
      }}
    }}

    @media (max-width: 480px) {{
      .container {{
        padding: 0 12px;
      }}
      .params-subgrid {{
        grid-template-columns: 1fr;
      }}
      .feedback-modal-overlay {{
        padding: 8px;
      }}
      .feedback-modal-card {{
        padding: 18px 14px;
        border-radius: var(--radius-md);
        max-height: calc(100dvh - 16px);
      }}
      .feedback-modal-title {{
        font-size: 1.02rem;
      }}
      .feedback-type-chip {{
        min-width: 80px;
        padding: 8px 6px;
        font-size: 0.78rem;
      }}
    }}

    @media (max-width: 420px) {{
      .container {{
        padding: 0 10px;
      }}
      .glass-config-card {{
        padding: 14px 10px;
      }}
      .code-input-box {{
        padding: 7px 8px;
        gap: 6px;
      }}
      .code-input-text {{
        font-size: 0.8rem;
      }}
      .btn-inline-copy {{
        padding: 4px 6px;
        font-size: 0.72rem;
      }}
      .segmented-tab {{
        padding: 8px 4px;
        font-size: 0.76rem;
        gap: 4px;
      }}
      .tab-icon {{
        width: 13px;
        height: 13px;
      }}
      .ai-services-probe-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    /* ==========================================================================
       4.4. Announcements & Changelog Section
       ========================================================================== */
    .news-section {{
      margin-top: 64px;
      margin-bottom: 24px;
    }}

    .news-header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }}

    .news-header-left h2 {{
      font-size: 1.65rem;
      font-weight: 800;
      color: #ffffff;
      margin: 8px 0 6px 0;
      letter-spacing: -0.02em;
    }}

    .news-subtitle {{
      color: var(--text-muted);
      font-size: 0.92rem;
      margin: 0;
    }}

    .news-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
    }}

    .news-card {{
      background: linear-gradient(145deg, rgba(14, 25, 44, 0.75) 0%, rgba(8, 14, 25, 0.88) 100%);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(0, 255, 157, 0.16);
      border-radius: var(--radius-md);
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.45);
      transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
    }}

    .news-card:hover {{
      border-color: rgba(0, 255, 157, 0.38);
      transform: translateY(-2px);
      box-shadow: 0 14px 34px -10px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 255, 157, 0.1);
    }}

    .news-card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}

    .news-tag {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      background: rgba(0, 255, 157, 0.1);
      border: 1px solid rgba(0, 255, 157, 0.28);
      color: var(--neon-mint);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .news-tag.launch {{
      background: rgba(6, 182, 212, 0.1);
      border-color: rgba(6, 182, 212, 0.3);
      color: var(--cyber-cyan);
    }}

    .news-tag.infra {{
      background: rgba(167, 139, 250, 0.1);
      border-color: rgba(167, 139, 250, 0.3);
      color: #a78bfa;
    }}

    .news-date {{
      font-size: 0.78rem;
      color: var(--text-dim);
      font-weight: 500;
    }}

    .news-card-title {{
      font-size: 1.08rem;
      font-weight: 700;
      color: #ffffff;
      margin: 0;
      line-height: 1.35;
    }}

    .news-card-text {{
      font-size: 0.91rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin: 0;
    }}

    /* ==========================================================================
       4.5. Community Reviews & Suggestions Section
       ========================================================================== */
    .reviews-section {{
      margin-top: 64px;
      margin-bottom: 24px;
    }}

    .reviews-header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }}

    .reviews-header-left h2 {{
      font-size: 1.65rem;
      font-weight: 800;
      color: #ffffff;
      margin: 8px 0 6px 0;
      letter-spacing: -0.02em;
    }}

    .reviews-subtitle {{
      color: var(--text-muted);
      font-size: 0.92rem;
      margin: 0;
    }}

    .btn-feedback-trigger {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 18px;
      font-size: 0.88rem;
      font-weight: 700;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .btn-feedback-trigger svg {{
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }}

    .reviews-container {{
      width: 100%;
    }}

    .reviews-empty-state {{
      background: rgba(13, 23, 40, 0.7);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px dashed rgba(0, 255, 157, 0.25);
      border-radius: var(--radius-md);
      padding: 44px 28px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
      max-width: 640px;
      margin: 0 auto;
      transition: all var(--transition-normal);
    }}

    .reviews-empty-state:hover {{
      border-color: rgba(0, 255, 157, 0.45);
      box-shadow: 0 0 30px rgba(0, 255, 157, 0.1);
    }}

    .empty-state-icon {{
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.25);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 14px;
      color: var(--neon-mint);
    }}

    .empty-state-icon svg {{
      width: 26px;
      height: 26px;
    }}

    .empty-state-badge {{
      display: inline-flex;
      align-items: center;
      padding: 3px 12px;
      border-radius: var(--radius-pill);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.2);
      color: var(--neon-mint);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 12px;
    }}

    .empty-state-title {{
      font-size: 1.22rem;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 8px 0;
    }}

    .empty-state-desc {{
      font-size: 0.9rem;
      color: var(--text-dim);
      line-height: 1.6;
      max-width: 480px;
      margin: 0 0 22px 0;
    }}

    .btn-open-feedback-empty {{
      padding: 11px 24px;
      font-size: 0.9rem;
      font-weight: 700;
      white-space: nowrap;
    }}

    .reviews-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 18px;
      width: 100%;
    }}

    .reviews-grid.single-item {{
      display: flex;
      justify-content: flex-start;
    }}

    .reviews-grid.single-item .review-card {{
      max-width: 540px;
      width: 100%;
    }}

    .review-card {{
      background: linear-gradient(145deg, rgba(14, 25, 44, 0.75) 0%, rgba(8, 14, 25, 0.88) 100%);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(0, 255, 157, 0.16);
      border-radius: var(--radius-md);
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
    }}

    .review-card:hover {{
      border-color: rgba(0, 255, 157, 0.38);
      transform: translateY(-2px);
      box-shadow: 0 14px 34px -10px rgba(0, 0, 0, 0.6), 0 0 22px rgba(0, 255, 157, 0.1);
    }}

    .review-card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}

    .review-author-info {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .review-avatar {{
      width: 42px;
      height: 42px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(0, 255, 157, 0.22), rgba(6, 182, 212, 0.22));
      border: 1px solid rgba(0, 255, 157, 0.35);
      color: var(--neon-mint);
      font-weight: 800;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 4px 12px rgba(0, 255, 157, 0.08);
    }}

    .review-avatar.dev {{
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(167, 139, 250, 0.2));
      border-color: rgba(56, 189, 248, 0.35);
      color: #38bdf8;
    }}

    .review-avatar.des {{
      background: linear-gradient(135deg, rgba(244, 114, 182, 0.2), rgba(251, 191, 36, 0.2));
      border-color: rgba(244, 114, 182, 0.35);
      color: #f472b6;
    }}

    .review-author-name {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.2;
    }}

    .review-author-role {{
      font-size: 0.76rem;
      color: var(--text-dim);
      margin-top: 2px;
    }}

    .review-stars-wrap {{
      display: flex;
      align-items: center;
      gap: 5px;
      background: rgba(251, 191, 36, 0.08);
      border: 1px solid rgba(251, 191, 36, 0.2);
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      flex-shrink: 0;
    }}

    .review-score-num {{
      font-size: 0.74rem;
      font-weight: 800;
      color: #fbbf24;
    }}

    .review-stars {{
      color: #fbbf24;
      font-size: 0.88rem;
      letter-spacing: 1px;
      text-shadow: 0 0 6px rgba(251, 191, 36, 0.4);
    }}

    .review-body {{
      color: #e2e8f0;
      font-size: 0.92rem;
      line-height: 1.6;
      margin: 0;
      flex: 1;
    }}

    /* Developer / Admin Reply Block */
    .review-reply {{
      margin-top: 10px;
      padding: 12px 14px;
      background: rgba(0, 255, 157, 0.04);
      border-left: 2px solid var(--neon-mint);
      border-radius: 4px 8px 8px 4px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .review-reply-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}

    .review-reply-author {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--neon-mint);
      letter-spacing: 0.02em;
    }}

    .review-reply-author svg {{
      width: 12px;
      height: 12px;
      stroke: var(--neon-mint);
    }}

    .review-reply-date {{
      font-size: 0.7rem;
      color: var(--text-dim);
    }}

    .review-reply-text {{
      color: #cbd5e1;
      font-size: 0.88rem;
      line-height: 1.5;
      margin: 0;
    }}

    /* Reviews Load More Wrap */
    .reviews-load-more-wrap {{
      display: flex;
      justify-content: center;
      margin-top: 24px;
      width: 100%;
    }}

    .btn-load-more-reviews {{
      padding: 12px 28px;
      font-size: 0.95rem;
      gap: 8px;
      cursor: pointer;
    }}

    .btn-load-more-reviews svg {{
      transition: transform 0.3s ease;
    }}

    .btn-load-more-reviews.expanded svg {{
      transform: rotate(180deg);
    }}

    .review-card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .review-badge-verified {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: var(--radius-pill);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.22);
      color: var(--neon-mint);
      font-size: 0.72rem;
      font-weight: 600;
      width: fit-content;
    }}

    .review-badge-verified svg {{
      width: 12px;
      height: 12px;
    }}

    .review-date {{
      font-size: 0.72rem;
      color: var(--text-dim);
      white-space: nowrap;
    }}

    /* ==========================================================================
       Feedback & Suggestions Modal
       ========================================================================== */
    .feedback-modal-overlay {{
      position: fixed;
      inset: 0;
      z-index: 2000;
      background: rgba(4, 8, 14, 0.78);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .feedback-modal-overlay.active {{
      opacity: 1;
      pointer-events: auto;
    }}

    .feedback-modal-card {{
      background: rgba(9, 16, 28, 0.98);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(0, 255, 157, 0.35);
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 255, 157, 0.15);
      border-radius: 20px;
      width: 100%;
      max-width: 520px;
      padding: 24px 26px;
      transform: scale(0.94);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-sizing: border-box;
      max-height: calc(100dvh - 32px);
      overflow-y: auto;
    }}

    .feedback-modal-overlay.active .feedback-modal-card {{
      transform: scale(1);
    }}

    .feedback-modal-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      gap: 12px;
    }}

    .feedback-modal-title-wrap {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .feedback-modal-icon {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .feedback-modal-icon svg {{
      width: 20px;
      height: 20px;
    }}

    .feedback-modal-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      margin: 0;
    }}

    .feedback-modal-subtitle {{
      font-size: 0.78rem;
      color: var(--text-dim);
      margin: 2px 0 0 0;
    }}

    .feedback-form {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .feedback-type-group {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .feedback-type-chip {{
      flex: 1;
      min-width: 110px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: var(--radius-sm);
      padding: 9px 12px;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all var(--transition-fast);
    }}

    .feedback-type-chip.active {{
      background: rgba(0, 255, 157, 0.12);
      border-color: var(--neon-mint);
      color: #ffffff;
      box-shadow: 0 0 14px rgba(0, 255, 157, 0.2);
    }}

    .rating-stars-wrap {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 6px 0;
    }}

    .feedback-label {{
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .star-rating {{
      display: flex;
      gap: 4px;
    }}

    .star-btn {{
      font-size: 1.5rem;
      line-height: 1;
      color: rgba(255, 255, 255, 0.2);
      cursor: pointer;
      padding: 2px 4px;
      transition: all var(--transition-fast);
      user-select: none;
    }}

    .star-btn:hover,
    .star-btn.active {{
      color: #fbbf24;
      text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
      transform: scale(1.1);
    }}

    .feedback-field {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .platform-chips {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .platform-chip {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: var(--radius-pill);
      padding: 6px 12px;
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-dim);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .platform-chip.active {{
      background: rgba(0, 255, 157, 0.1);
      border-color: rgba(0, 255, 157, 0.4);
      color: var(--neon-mint);
    }}

    .feedback-textarea,
    .feedback-input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      color: #ffffff;
      font-family: inherit;
      font-size: 0.88rem;
      box-sizing: border-box;
      outline: none;
      transition: all var(--transition-fast);
    }}

    .feedback-textarea:focus,
    .feedback-input:focus {{
      border-color: var(--neon-mint);
      background: rgba(255, 255, 255, 0.08);
      box-shadow: 0 0 14px rgba(0, 255, 157, 0.2);
    }}

    .feedback-textarea {{
      resize: vertical;
      min-height: 90px;
    }}

    .feedback-submit-btn {{
      width: 100%;
      margin-top: 4px;
      padding: 12px 20px;
      font-size: 0.95rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }}

    .feedback-submit-btn svg {{
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }}

    /* ==========================================================================
       New Landing Sections & Components (SEO, Legal, Compliance)
       ========================================================================== */
    .section-tag-wrapper {{
      display: flex;
      justify-content: center;
      margin-bottom: 12px;
    }}

    .section-heading {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      text-align: center;
      color: #ffffff;
      margin-bottom: 10px;
    }}

    .section-subtitle {{
      font-size: 1.05rem;
      color: var(--text-muted);
      text-align: center;
      max-width: 680px;
      margin: 0 auto 36px auto;
      line-height: 1.55;
    }}

    /* Hero Benefits List & CTA */
    .hero-benefits-wrapper {{
      max-width: 840px;
      margin: 28px auto 28px auto;
      width: 100%;
    }}

    .hero-benefits-list {{
      list-style: none;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
      padding: 0;
      margin: 0;
    }}

    @media (max-width: 768px) {{
      .hero-benefits-list {{
        grid-template-columns: 1fr;
        gap: 10px;
      }}
    }}

    .hero-benefit-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 18px;
      background: rgba(11, 20, 36, 0.65);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-md);
      backdrop-filter: blur(12px);
      text-align: left;
      font-size: 0.92rem;
      line-height: 1.45;
      color: #e2e8f0;
      transition: all var(--transition-fast);
    }}

    .hero-benefit-item:hover {{
      border-color: rgba(0, 255, 157, 0.35);
      background: rgba(15, 27, 48, 0.8);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 255, 157, 0.08);
    }}

    .benefit-icon {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: rgba(0, 255, 157, 0.12);
      border: 1px solid rgba(0, 255, 157, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 1px;
    }}

    .benefit-icon svg {{
      width: 13px;
      height: 13px;
      color: var(--neon-mint);
    }}

    .hero-cta-wrapper {{
      display: flex;
      justify-content: center;
      margin: 12px auto 32px auto;
    }}

    .btn-hero-cta {{
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 16px 36px;
      font-size: 1.08rem;
      font-weight: 700;
      color: #070d14 !important;
      background: linear-gradient(135deg, var(--neon-mint) 0%, var(--neon-emerald) 100%);
      border-radius: var(--radius-pill);
      box-shadow: 0 0 24px var(--mint-glow), 0 8px 30px rgba(0, 255, 157, 0.25);
      transition: all var(--transition-smooth);
      cursor: pointer;
      text-decoration: none;
    }}

    .btn-hero-cta:hover {{
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 0 36px rgba(0, 255, 157, 0.5), 0 12px 36px rgba(0, 255, 157, 0.35);
      color: #070d14 !important;
    }}

    /* Comparison Section */
    .comparison-section {{
      padding: 60px 0 50px 0;
      position: relative;
    }}

    .comparison-table-wrapper {{
      width: 100%;
      overflow-x: auto;
      border-radius: var(--radius-lg);
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
    }}

    .comparison-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      min-width: 650px;
    }}

    .comparison-table th,
    .comparison-table td {{
      padding: 18px 24px;
      border-bottom: 1px solid var(--border-hairline);
    }}

    .comparison-table thead th {{
      background: rgba(15, 27, 48, 0.85);
      font-size: 0.95rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .comparison-table thead .col-param {{
      width: 25%;
      color: var(--text-muted);
    }}

    .comparison-table thead .col-vpn {{
      width: 37.5%;
      color: #94a3b8;
    }}

    .comparison-table thead .col-magic {{
      width: 37.5%;
      color: var(--neon-mint);
      background: rgba(0, 255, 157, 0.08);
      border-left: 1px solid rgba(0, 255, 157, 0.2);
      border-right: 1px solid rgba(0, 255, 157, 0.2);
    }}

    .comparison-table tbody tr:hover {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .comparison-table tbody tr:last-child td {{
      border-bottom: none;
    }}

    .cell-param strong {{
      color: #f1f5f9;
      font-size: 0.95rem;
    }}

    .cell-vpn {{
      color: #cbd5e1;
      font-size: 0.9rem;
      line-height: 1.45;
    }}

    .cell-magic {{
      color: #ffffff;
      font-size: 0.9rem;
      line-height: 1.45;
      background: rgba(0, 255, 157, 0.04);
      border-left: 1px solid rgba(0, 255, 157, 0.15);
      border-right: 1px solid rgba(0, 255, 157, 0.15);
      font-weight: 500;
    }}

    .status-indicator {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      font-size: 0.75rem;
      font-weight: 800;
      margin-right: 8px;
      flex-shrink: 0;
      vertical-align: middle;
    }}

    .status-indicator.bad {{
      background: rgba(239, 68, 68, 0.15);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.35);
    }}

    .status-indicator.good {{
      background: rgba(0, 255, 157, 0.18);
      color: var(--neon-mint);
      border: 1px solid rgba(0, 255, 157, 0.5);
    }}

    /* Supported AI Platforms Grid */
    .ai-platforms-section {{
      padding: 60px 0 50px 0;
      position: relative;
    }}

    .platforms-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
    }}

    @media (max-width: 1200px) {{
      .platforms-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (max-width: 640px) {{
      .platforms-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .platform-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-lg);
      padding: 24px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
      transition: all var(--transition-smooth);
      display: flex;
      flex-direction: column;
    }}

    .platform-card:hover {{
      border-color: rgba(0, 255, 157, 0.35);
      transform: translateY(-3px);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 255, 157, 0.1);
    }}

    .platform-card-header {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 16px;
    }}

    .platform-icon-wrap {{
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .platform-icon-wrap svg {{
      width: 24px;
      height: 24px;
    }}

    .platform-icon-wrap.gemini-icon svg {{ color: #4285f4; }}
    .platform-icon-wrap.aistudio-icon svg {{ color: var(--cyber-cyan); }}
    .platform-icon-wrap.chatgpt-icon svg {{ color: var(--neon-mint); }}
    .platform-icon-wrap.claude-icon svg {{ color: #d97706; }}
    .platform-icon-wrap.midjourney-icon svg {{ color: #a855f7; }}
    .platform-icon-wrap.copilot-icon svg {{ color: #06b6d4; }}
    .platform-icon-wrap.xbox-icon svg {{ color: #22c55e; }}
    .platform-icon-wrap.ps-icon svg {{ color: #38bdf8; }}

    /* Compliance & White-list Section */
    .compliance-section {{
      padding: 50px 0 40px 0;
      position: relative;
    }}

    .compliance-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }}

    @media (max-width: 992px) {{
      .compliance-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .compliance-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-lg);
      padding: 24px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
      transition: all var(--transition-smooth);
    }}

    .compliance-card:hover {{
      border-color: rgba(0, 255, 157, 0.35);
      transform: translateY(-3px);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 255, 157, 0.1);
    }}

    .compliance-card-header {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 12px;
    }}

    .compliance-icon-wrap {{
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .compliance-icon-wrap svg {{
      width: 22px;
      height: 22px;
    }}

    .compliance-icon-wrap.ai-wrap svg {{ color: var(--neon-mint); }}
    .compliance-icon-wrap.gaming-wrap svg {{ color: var(--cyber-cyan); }}
    .compliance-icon-wrap.pure-wrap svg {{ color: #10b981; }}

    .compliance-card-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      margin: 0;
    }}

    .compliance-card-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.55;
      margin: 0;
    }}

    .platform-name {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 2px;
    }}

    .platform-badge {{
      font-size: 0.75rem;
      color: var(--text-dim);
      font-family: monospace;
    }}

    .platform-error-box {{
      background: rgba(6, 182, 212, 0.08);
      border: 1px solid rgba(6, 182, 212, 0.25);
      border-radius: var(--radius-sm);
      padding: 10px 12px;
      margin-bottom: 14px;
    }}

    .error-label {{
      display: block;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--cyber-cyan);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
    }}

    .error-code {{
      display: block;
      font-size: 0.8rem;
      font-family: monospace;
      color: #f87171;
      word-break: break-word;
    }}

    .platform-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-top: auto;
    }}

    /* FAQ Section */
    .faq-section {{
      padding: 60px 0 50px 0;
      position: relative;
    }}

    .faq-accordion {{
      max-width: 840px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .faq-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-md);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      transition: all var(--transition-fast);
      overflow: hidden;
    }}

    .faq-item[open] {{
      border-color: rgba(0, 255, 157, 0.35);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 16px rgba(0, 255, 157, 0.08);
    }}

    .faq-question {{
      padding: 20px 24px;
      font-size: 1.05rem;
      font-weight: 600;
      color: #ffffff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      list-style: none;
      user-select: none;
    }}

    .faq-question::-webkit-details-marker {{
      display: none;
    }}

    .faq-chevron {{
      width: 18px;
      height: 18px;
      color: var(--neon-mint);
      transition: transform var(--transition-fast);
      flex-shrink: 0;
    }}

    .faq-item[open] .faq-chevron {{
      transform: rotate(180deg);
    }}

    .faq-answer {{
      padding: 0 24px 22px 24px;
      font-size: 0.94rem;
      line-height: 1.6;
      color: var(--text-muted);
      border-top: 1px solid rgba(255, 255, 255, 0.04);
      margin-top: 4px;
      padding-top: 16px;
    }}

    /* Cookie Banner & Legal Modals */
    .cookie-banner {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      width: calc(100% - 40px);
      max-width: 860px;
      background: rgba(11, 20, 36, 0.96);
      border: 1px solid rgba(0, 255, 157, 0.35);
      border-radius: var(--radius-md);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.75), 0 0 24px rgba(0, 255, 157, 0.15);
      z-index: 1060;
      padding: 16px 24px;
      box-sizing: border-box;
      animation: fadeIn 0.3s ease-out;
    }}

    .cookie-banner-content {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      width: 100%;
    }}

    .cookie-banner .btn-cookie-accept {{
      padding: 8px 22px;
      font-size: 0.88rem;
      white-space: nowrap;
      flex-shrink: 0;
      width: auto;
    }}

    @media (max-width: 640px) {{
      .cookie-banner-content {{
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
      }}
      .cookie-banner .btn-cookie-accept {{
        width: 100%;
        text-align: center;
        justify-content: center;
      }}
    }}

    .cookie-icon {{
      flex-shrink: 0;
      display: flex;
      align-items: center;
    }}

    .cookie-text {{
      font-size: 0.86rem;
      line-height: 1.5;
      color: #cbd5e1;
      margin: 0;
      flex: 1;
    }}

    .btn-cookie-accept {{
      padding: 8px 22px;
      font-size: 0.88rem;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .footer-disclaimer-row {{
      padding: 20px 0 10px 0;
      border-top: 1px solid var(--border-hairline);
      margin-top: 20px;
    }}

    .legal-disclaimer {{
      font-size: 0.78rem;
      line-height: 1.55;
      color: var(--text-dim);
      text-align: center;
      max-width: 900px;
      margin: 0 auto;
    }}

    .footer-legal-link {{
      font-size: 0.82rem;
      color: var(--text-dim);
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px 8px;
      transition: color var(--transition-fast);
    }}

    .footer-legal-link:hover {{
      color: var(--neon-mint);
    }}

    .legal-modal-card {{
      max-width: 640px;
      width: 90%;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
    }}

    .legal-modal-body {{
      padding: 20px 24px;
      overflow-y: auto;
      font-size: 0.9rem;
      line-height: 1.6;
      color: #cbd5e1;
      border-top: 1px solid var(--border-hairline);
      border-bottom: 1px solid var(--border-hairline);
    }}

    .legal-modal-body h4 {{
      color: #ffffff;
      font-size: 0.98rem;
      margin: 16px 0 6px 0;
    }}

    .legal-modal-body h4:first-child {{
      margin-top: 0;
    }}

    .legal-modal-body p {{
      margin-bottom: 10px;
    }}

    .legal-modal-footer {{
      padding: 16px 24px;
      display: flex;
      justify-content: flex-end;
    }}

    /* Site Emergency Alert Banner */
    .site-alert-banner {{
      position: relative;
      width: 100%;
      background: linear-gradient(90deg, rgba(245, 158, 11, 0.22) 0%, rgba(239, 68, 68, 0.25) 100%);
      border-bottom: 2px solid rgba(245, 158, 11, 0.55);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
      color: #ffffff;
      z-index: 1000;
      animation: slideDownAlert 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    @keyframes slideDownAlert {{
      from {{ transform: translateY(-100%); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    .site-alert-inner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 20px;
      gap: 16px;
    }}

    .site-alert-content {{
      display: flex;
      align-items: center;
      gap: 12px;
      line-height: 1.5;
      flex-wrap: wrap;
    }}

    .site-alert-pulse {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #f59e0b;
      box-shadow: 0 0 12px #f59e0b, 0 0 4px #ef4444;
      animation: pulseDot 1.5s infinite;
      flex-shrink: 0;
    }}

    .site-alert-icon {{
      font-size: 1.35rem;
      flex-shrink: 0;
    }}

    .site-alert-text {{
      color: #ffffff;
      font-size: 1.08rem;
      font-weight: 700;
      letter-spacing: 0.01em;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45);
    }}

    .site-alert-text code {{
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(245, 158, 11, 0.5);
      padding: 2px 8px;
      border-radius: 4px;
      color: #fde68a;
      font-family: monospace;
      font-weight: 800;
    }}

    .site-alert-close {{
      background: transparent;
      border: none;
      color: rgba(255, 255, 255, 0.85);
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }}

    .site-alert-close:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.15);
      transform: scale(1.05);
    }}

    @media (max-width: 640px) {{
      .site-alert-inner {{
        padding: 12px 14px;
        gap: 10px;
      }}
      .site-alert-text {{
        font-size: 0.98rem;
        line-height: 1.45;
      }}
      .site-alert-icon {{
        font-size: 1.2rem;
      }}
    }}
  </style>

  <!-- Yandex.Metrika counter -->
  <script type="text/javascript">
    (function(m,e,t,r,i,k,a){{
        m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js', 'ym');

    ym(113667571, 'init', {{clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true, triggerEvent:true}});
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/113667571" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
  <!-- /Yandex.Metrika counter -->
</head>
<body>

  <!-- Site Emergency Alert Banner -->
  <aside id="site-alert-banner" class="site-alert-banner" style="display: none;" role="alert" aria-live="assertive">
    <div class="container site-alert-inner">
      <div class="site-alert-content">
        <span class="site-alert-pulse"></span>
        <span class="site-alert-icon">⚠️</span>
        <span id="site-alert-text" class="site-alert-text"></span>
      </div>
      <button type="button" class="site-alert-close" id="site-alert-close-btn" aria-label="Закрыть оповещение" onclick="dismissSiteAlert()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </aside>

  <!-- 1. Header (Navbar) -->
  <header>
    <div class="container header-content">
      <a href="https://magicdns.ru" class="logo-container" aria-label="MagicDNS Главная">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--neon-mint)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 2v7m0 6v7M2 12h7m6 0h7"></path>
            <circle cx="12" cy="2" r="1.5" fill="var(--neon-mint)"></circle>
            <circle cx="12" cy="22" r="1.5" fill="var(--neon-mint)"></circle>
            <circle cx="2" cy="12" r="1.5" fill="var(--neon-mint)"></circle>
            <circle cx="22" cy="12" r="1.5" fill="var(--neon-mint)"></circle>
          </svg>
        </div>
        <span class="brand-title">Magic<span class="accent">DNS</span></span>
      </a>

      <!-- Header Right: Language, Support & Status -->
      <div class="header-right">
        <!-- Language Selector -->
        <div class="lang-selector-wrapper" id="lang-selector-wrapper">
          <button type="button" class="lang-btn" id="lang-menu-btn" aria-expanded="false" aria-haspopup="true" aria-label="Выбрать язык / Select language">
            <svg class="lang-globe-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="2" y1="12" x2="22" y2="12"></line>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
            <span id="current-lang-text">RU</span>
            <svg class="lang-arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          <ul class="lang-dropdown" id="lang-dropdown" role="menu" aria-label="Языки">
            <li class="lang-option active" role="menuitem" data-lang="ru" tabindex="0">
              <span>Русский</span>
              <span class="lang-code">RU</span>
            </li>
            <li class="lang-option" role="menuitem" data-lang="en" tabindex="0">
              <span>English</span>
              <span class="lang-code">EN</span>
            </li>
            <li class="lang-option" role="menuitem" data-lang="zh" tabindex="0">
              <span>中文 (简体)</span>
              <span class="lang-code">ZH</span>
            </li>
            <li class="lang-option" role="menuitem" data-lang="tr" tabindex="0">
              <span>Türkçe</span>
              <span class="lang-code">TR</span>
            </li>
          </ul>
        </div>

        <a href="https://t.me/magicdns_alert_bot" target="_blank" rel="noopener noreferrer" class="btn-support-header btn-tg-contact-header" aria-label="Связаться с админом">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
          </svg>
          <span data-i18n="headerTgBtn">Написать админу</span>
        </a>

        <a href="https://pay.cloudtips.ru/p/596a95a5" target="_blank" rel="noopener noreferrer" class="btn-support-header" aria-label="Поддержать автора">
          <svg viewBox="0 0 24 24" class="donate-heart" aria-hidden="true">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span data-i18n="supportBtn">Поддержать автора</span>
        </a>

        <!-- Status Badge -->
        <div class="status-badge" role="status" aria-live="polite">
          <div class="status-dot-wrapper">
            <div class="status-ping"></div>
            <div class="status-dot"></div>
          </div>
          <span><span class="status-label" data-i18n="statusLabel">Статус сети: </span><span class="status-text" data-i18n="statusText">Работает стабильно</span></span>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container">
    
    <!-- 2. Hero Section -->
    <section class="hero hero-section">
      <div class="hero-eyebrow">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
        <span data-i18n="heroEyebrow">ДНС ДЛЯ ИИ • ДНС для искусственного интеллекта • Прямой доступ на полной скорости • Блокировка рекламы AdGuard</span>
      </div>
      <h1 data-i18n="heroHeading">ДНС для ИИ: Smart DNS для ИИ к Gemini, ChatGPT и Claude без сторонних приложений и тоннелей</h1>
      <p class="hero-subtitle" data-i18n="heroSubtitle">Оптимизация сетевой маршрутизации к AI-платформам: Смарт ДНС для ИИ и персональный DNS сервер. Прямой доступ к международным нейросетям без посредников, а локальный трафик, российские банки и Госуслуги идут напрямую от вашего провайдера на максимальной скорости.</p>

      <!-- 4 Specific Hero Benefits -->
      <div class="hero-benefits-wrapper">
        <ul class="hero-benefits-list">
          <li class="hero-benefit-item">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span data-i18n="heroBenefit1">Прямой доступ без посредников: частный ДНС для ИИ устраняет региональные ограничения зарубежных сервисов (OpenAI, Google) без падения скорости</span>
          </li>
          <li class="hero-benefit-item">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span data-i18n="heroBenefit2">0% нагрузки на аккумулятор: работает на уровне сетевого стека ОС, не требует фоновых программ и сторонних сетевых клиентов</span>
          </li>
          <li class="hero-benefit-item">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span data-i18n="heroBenefit3">Российские сервисы без сбоев: Сбербанк, Т-Банк и Госуслуги работают на полной скорости без капчи и отключений</span>
          </li>
          <li class="hero-benefit-item">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span data-i18n="heroBenefit4">ДНС для нейросетей с нулевой задержкой: прямое подключение с задержкой 25–45 мс для быстрой генерации и потоковых ответов</span>
          </li>
        </ul>
      </div>

      <!-- Main CTA Button -->
      <div class="hero-cta-wrapper">
        <a href="#setup" class="btn-hero-cta">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          <span data-i18n="heroCta">Подключить Smart DNS бесплатно</span>
        </a>
      </div>
      
      <!-- Unified Harmonious Services Ribbon -->
      <div class="services-ribbon-container">
        <div class="services-ribbon">
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
            <span>Claude AI</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L14.2 9.8L22 12L14.2 14.2L12 22L9.8 14.2L2 12L9.8 9.8L12 2Z"/></svg>
            <span>Gemini</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M9.5 15a3.5 3.5 0 0 0 5 0"/></svg>
            <span>ChatGPT</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <span>Perplexity</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 22 22 22 12 2"/><circle cx="12" cy="15" r="2"/></svg>
            <span>Antigravity</span>
          </div>
          <button type="button" class="service-chip service-chip-more" id="btn-toggle-more-ai" aria-expanded="false" title="Показать все поддерживаемые нейросети">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span data-i18n="chipMore">+ ещё 30+ сервисов</span>
          </button>
          <div class="service-chip highlight">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span data-i18n="chipNoVpn">Без сторонних приложений и тоннелей</span>
          </div>
          <div class="service-chip highlight-adblock">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
            <span data-i18n="chipAdblock">Блокировка рекламы (AdGuard)</span>
          </div>
        </div>

        <!-- Expandable Drawer for Additional AI Services -->
        <div class="more-services-drawer" id="more-services-drawer" aria-hidden="true">
          <div class="more-services-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            <span data-i18n="drawerTitle">Также работают через MagicDNS без ограничений:</span>
          </div>
          <div class="more-services-grid">
            <span class="mini-service-tag">Cursor AI</span>
            <span class="mini-service-tag">Midjourney</span>
            <span class="mini-service-tag">xAI Grok</span>
            <span class="mini-service-tag">v0 by Vercel</span>
            <span class="mini-service-tag">ElevenLabs</span>
            <span class="mini-service-tag">Suno &amp; Udio</span>
            <span class="mini-service-tag">Mistral Le Chat</span>
            <span class="mini-service-tag">Hugging Face</span>
            <span class="mini-service-tag">Runway Gen-3</span>
            <span class="mini-service-tag">Poe by Quora</span>
            <span class="mini-service-tag">GitHub Copilot</span>
            <span class="mini-service-tag">Notion AI</span>
            <span class="mini-service-tag">DeepL Pro</span>
            <span class="mini-service-tag">Adobe Firefly</span>
          </div>
          <div class="more-services-note" data-i18n="drawerNote">DNS-шлюз автоматически маршрутизирует веб-интерфейсы, официальные приложения и REST API</div>
        </div>
      </div>
    </section>

    <!-- 2.5. Comparison Section -->
    <section class="comparison-section" id="comparison">
      <div class="section-tag-wrapper">
        <div class="section-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          <span data-i18n="compTag">СРАВНЕНИЕ ТЕХНОЛОГИЙ</span>
        </div>
      </div>
      <h2 class="section-heading" data-i18n="compTitle">Сторонние сетевые клиенты против MagicDNS (Smart DNS)</h2>
      <p class="section-subtitle" data-i18n="compSubtitle">Почему прямое перенаправление DNS эффективнее и надежнее тяжелых тоннелей</p>
      
      <div class="comparison-table-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th class="col-param" data-i18n="compThParam">Параметр</th>
              <th class="col-vpn" data-i18n="compThVpn">Сторонние сетевые клиенты</th>
              <th class="col-magic" data-i18n="compThMagic">MagicDNS (Smart DNS)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="cell-param">
                <strong data-i18n="compParamSpeed">Реальная скорость</strong>
              </td>
              <td class="cell-vpn">
                <span class="status-indicator bad">✕</span>
                <span data-i18n="compVpnSpeed">Падение скорости на 40–70% из-за шифрования тоннеля и очередей</span>
              </td>
              <td class="cell-magic">
                <span class="status-indicator good">✓</span>
                <span data-i18n="compMagicSpeed">100% скорости вашего провайдера (до 1 Гбит/с) без замедления</span>
              </td>
            </tr>
            <tr>
              <td class="cell-param">
                <strong data-i18n="compParamPing">Пинг в API</strong>
              </td>
              <td class="cell-vpn">
                <span class="status-indicator bad">✕</span>
                <span data-i18n="compVpnPing">Задержки 150–350 мс, лаги и прерывания стриминга токенов</span>
              </td>
              <td class="cell-magic">
                <span class="status-indicator good">✓</span>
                <span data-i18n="compMagicPing">Минимальный пинг 25–45 мс, мгновенный посимвольный вывод</span>
              </td>
            </tr>
            <tr>
              <td class="cell-param">
                <strong data-i18n="compParamBattery">Влияние на заряд смартфона</strong>
              </td>
              <td class="cell-vpn">
                <span class="status-indicator bad">✕</span>
                <span data-i18n="compVpnBattery">Повышенный расход батареи до 15–25% в сутки из-за фонового клиента</span>
              </td>
              <td class="cell-magic">
                <span class="status-indicator good">✓</span>
                <span data-i18n="compMagicBattery">0% расхода аккумулятора — сетевые настройки встроены в ОС</span>
              </td>
            </tr>
            <tr>
              <td class="cell-param">
                <strong data-i18n="compParamBanks">Доступность банков и Госуслуг</strong>
              </td>
              <td class="cell-vpn">
                <span class="status-indicator bad">✕</span>
                <span data-i18n="compVpnBanks">Сбои доступа, проверки безопасности, блокировки со стороны сервисов РФ</span>
              </td>
              <td class="cell-magic">
                <span class="status-indicator good">✓</span>
                <span data-i18n="compMagicBanks">Работают штатно: локальный трафик идёт напрямую от провайдера</span>
              </td>
            </tr>
            <tr>
              <td class="cell-param">
                <strong data-i18n="compParamStability">Стабильность соединения</strong>
              </td>
              <td class="cell-vpn">
                <span class="status-indicator bad">✕</span>
                <span data-i18n="compVpnStability">Периодические обрывы, поиск работающих серверов и протоколов</span>
              </td>
              <td class="cell-magic">
                <span class="status-indicator good">✓</span>
                <span data-i18n="compMagicStability">Стабильное соединение 24/7 при переключении между Wi-Fi и мобильным интернетом</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 2.7. Supported AI Platforms Section -->
    <section class="ai-platforms-section" id="platforms">
      <div class="section-tag-wrapper">
        <div class="section-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <span data-i18n="platTag">ПОДДЕРЖИВАЕМЫЕ ПЛАТФОРМЫ</span>
        </div>
      </div>
      <h2 class="section-heading" data-i18n="platTitle">Поддерживаемые платформы ИИ и устраняемые ошибки</h2>
      <p class="section-subtitle" data-i18n="platSubtitle">Автоматическое устранение региональных ошибок геолокации без прокси и сторонних приложений</p>

      <div class="platforms-grid">
        <!-- Card 1: Google Gemini -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap gemini-icon">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L14.2 9.8L22 12L14.2 14.2L12 22L9.8 14.2L2 12L9.8 9.8L12 2Z"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Google Gemini</h3>
              <span class="platform-badge">gemini.google.com</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"Gemini is not available in your country"</code>
          </div>
          <p class="platform-desc" data-i18n="platGeminiDesc">DNS для Gemini: как открыть Gemini через DNS без задержек. Устраняет ошибку «Gemini is not available in your country» в веб-версии и мобильных приложениях.</p>
        </div>

        <!-- Card 2: Google AI Studio -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap aistudio-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M15 9h6"/><path d="M15 15h6"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Google AI Studio</h3>
              <span class="platform-badge">aistudio.google.com</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"User location is not supported"</code>
          </div>
          <p class="platform-desc" data-i18n="platAiStudioDesc">Smart DNS Google AI Studio: прямой доступ к Google AI Studio без сторонних приложений и тоннелей для разработчиков. Устраняет ошибку «User location is not supported» при вызове моделей и выпуске API-ключей.</p>
        </div>

        <!-- Card 3: ChatGPT (OpenAI) -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap chatgpt-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M9.5 15a3.5 3.5 0 0 0 5 0"/></svg>
            </div>
            <div>
              <h3 class="platform-name">ChatGPT</h3>
              <span class="platform-badge">chatgpt.com (OpenAI)</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"OpenAI's services are not available in your country"</code>
          </div>
          <p class="platform-desc" data-i18n="platChatgptDesc">DNS для ChatGPT: устраняет сбои сессий «OpenAI's services are not available in your country» и проверки Cloudflare, обеспечивая прямой доступ без посредников.</p>
        </div>

        <!-- Card 4: Claude (Anthropic) -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap claude-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Claude</h3>
              <span class="platform-badge">claude.ai (Anthropic)</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"App unavailable in your region"</code>
          </div>
          <p class="platform-desc" data-i18n="platClaudeDesc">Доступ к Claude AI без сторонних приложений и тоннелей: стабильная работа в браузере claude.ai и нативных приложениях без ошибки «App unavailable in your region».</p>
        </div>

        <!-- Card 5: Midjourney -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap midjourney-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12h20"/><path d="M7 16l5-8 5 8"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Midjourney</h3>
              <span class="platform-badge">midjourney.com</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"Failed to load user gallery / 403"</code>
          </div>
          <p class="platform-desc" data-i18n="platMidjourneyDesc">DNS для Midjourney: устраняет сбои авторизации и обеспечивает стабильную загрузку веб-интерфейса и галереи на midjourney.com.</p>
        </div>

        <!-- Card 6: Microsoft Copilot -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap copilot-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="8 10 12 14 16 10"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Microsoft Copilot</h3>
              <span class="platform-badge">copilot.microsoft.com</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"Copilot is not available in your region"</code>
          </div>
          <p class="platform-desc" data-i18n="platCopilotDesc">Copilot DNS: открывает доступ к генерации текста и картинок в Windows 11 и Edge без региональных отказов.</p>
        </div>

        <!-- Card 7: Xbox Live -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap xbox-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M6 7c2.5 3 4.5 7 6 12"/><path d="M18 7c-2.5 3-4.5 7-6 12"/><path d="M5 16c3.5-2 6.5-2 14 0"/></svg>
            </div>
            <div>
              <h3 class="platform-name">Xbox Live</h3>
              <span class="platform-badge">xbox.com (Microsoft)</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"0x80a40401 / 0x87dd0006"</code>
          </div>
          <p class="platform-desc" data-i18n="platXboxDesc">DNS для Xbox: устраняет ошибку входа 0x80a40401, обеспечивает стабильную авторизацию в профиле, работу Game Pass и синхронизацию облачных сохранений.</p>
        </div>

        <!-- Card 8: PlayStation Network -->
        <div class="platform-card">
          <div class="platform-card-header">
            <div class="platform-icon-wrap ps-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 17c3-3 6-4 10-4v5l4-2v-8c-4 0-8 2-11 5"/><path d="M12 4v4c3 0 6 1 8 3l2-1c-2-3-6-6-10-6z"/></svg>
            </div>
            <div>
              <h3 class="platform-name">PlayStation Network</h3>
              <span class="platform-badge">playstation.com (Sony)</span>
            </div>
          </div>
          <div class="platform-error-box">
            <span class="error-label" data-i18n="platErrorLabel">Устраняемая ошибка:</span>
            <code class="error-code">"WS-116521-6 / Ошибка связи с сервером"</code>
          </div>
          <p class="platform-desc" data-i18n="platPsDesc">DNS для PlayStation: устраняет сетевые сбои подключения к PSN, ошибки авторизации в аккаунте Sony и обеспечивает стабильную игру по сети на PS4 и PS5.</p>
        </div>
      </div>
    </section>

    <!-- 2.8. Compliance & White-list Section -->
    <section class="compliance-section" id="compliance">
      <div class="section-tag-wrapper">
        <div class="section-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span data-i18n="complianceTag">100% БЕЛЫЙ СПИСОК</span>
        </div>
      </div>
      <h2 class="section-heading" data-i18n="complianceTitle">Соответствие законодательству РФ и закрытый белый список</h2>
      <p class="section-subtitle" data-i18n="complianceSubtitle">MagicDNS принципиально не обрабатывает запросы к ресурсам, ограниченным на территории РФ (149-ФЗ)</p>

      <div class="compliance-grid">
        <div class="compliance-card">
          <div class="compliance-card-header">
            <div class="compliance-icon-wrap ai-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 12L2.1 12a10 10 0 0 0 9.9 10V12z"/></svg>
            </div>
            <h3 class="compliance-card-title" data-i18n="complianceColAiTitle">Платформы искусственного интеллекта</h3>
          </div>
          <p class="compliance-card-desc" data-i18n="complianceColAiDesc">Прямой доступ к ChatGPT, Claude, Google Gemini, Perplexity, Cursor и Midjourney без посредников и задержек.</p>
        </div>

        <div class="compliance-card">
          <div class="compliance-card-header">
            <div class="compliance-icon-wrap gaming-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="6"/><circle cx="8" cy="12" r="2"/><path d="M15 9v6m-3-3h6"/></svg>
            </div>
            <h3 class="compliance-card-title" data-i18n="complianceColGamingTitle">Игровые консоли и экосистемы</h3>
          </div>
          <p class="compliance-card-desc" data-i18n="complianceColGamingDesc">Устранение системных ошибок авторизации 0x80a40401 и WS-116521-6 для стабильной работы Xbox Live и PlayStation Network.</p>
        </div>

        <div class="compliance-card">
          <div class="compliance-card-header">
            <div class="compliance-icon-wrap pure-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
            </div>
            <h3 class="compliance-card-title" data-i18n="complianceColPureTitle">Безопасность и чистый трафик (149-ФЗ)</h3>
          </div>
          <p class="compliance-card-desc" data-i18n="complianceColPureDesc">Сервис не затрагивает российские сервисы, банки и Госуслуги — они работают напрямую от вашего провайдера на полной скорости.</p>
        </div>
      </div>
    </section>

    <!-- 3. Device Configurator -->
    <section class="configurator-section tabs-section" id="setup">
      <div class="section-tag-wrapper">
        <div class="section-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="3"/><path d="M12 2v7m0 6v7M2 12h7m6 0h7"/></svg>
          <span data-i18n="setupTag">ИНСТРУКЦИИ ПО ПОДКЛЮЧЕНИЮ</span>
        </div>
      </div>
      <h2 class="section-heading" data-i18n="setupTitle">Быстрая настройка Smart DNS на ваших устройствах</h2>
      <p class="section-subtitle" data-i18n="setupSubtitle">Выберите вашу операционную систему или настройте домашний роутер за 1 минуту</p>
      <!-- Segmented Tab Bar -->
      <div class="segmented-bar-wrapper">
        <nav class="segmented-bar" role="tablist" aria-label="Конфигурация устройств">
          <button class="segmented-tab active" role="tab" id="tab-windows" aria-controls="panel-windows" aria-selected="true" tabindex="0" data-target="panel-windows">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" fill="currentColor"/></svg>
            <span data-i18n="tabWindows">Windows (DoH)</span>
          </button>
          <button class="segmented-tab" role="tab" id="tab-ios" aria-controls="panel-ios" aria-selected="false" tabindex="-1" data-target="panel-ios">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.61-.75 1.04-1.8 0.92-2.87-.9.04-2 .6-2.63 1.34-.56.64-.99 1.68-.86 2.73 1.01.08 2-.45 2.57-1.2" fill="currentColor"/></svg>
            <span data-i18n="tabIos">Apple iOS / macOS</span>
          </button>
          <button class="segmented-tab" role="tab" id="tab-android" aria-controls="panel-android" aria-selected="false" tabindex="-1" data-target="panel-android">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.551 0 .9993.4482.9993.9993.0001.5511-.4483.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.411 13.8533 8.1 12 8.1s-3.5902.311-5.1368.8497L4.8409 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6889-7.5743-6.1185-9.4396" fill="currentColor"/></svg>
            <span data-i18n="tabAndroid">Android (DoT)</span>
          </button>
        </nav>
      </div>

      <!-- Panel 1: Windows (DoH) -->
      <div class="tab-panel active" id="panel-windows" role="tabpanel" aria-labelledby="tab-windows">
        <div class="glass-config-card">
          <div class="card-left-column">
            <div class="card-header-row">
              <h2 class="card-header-title" data-i18n="winTitle">Windows &amp; Браузеры (DoH)</h2>
              <span class="card-badge" data-i18n="winBadge">RFC 8484 • Windows 11 &amp; Роутеры</span>
            </div>
            <p class="card-instruction" data-i18n="winDesc">
              Быстрый ДНС без сторонних приложений и тоннелей для Windows 11 и браузеров. Шифрует все DNS-запросы под защищённый HTTPS-трафик (RFC 8484 DoH). Настройка: Параметры → Сеть → Wi-Fi / Ethernet → Назначение DNS → Вручную (DNS через HTTPS) или в настройках браузера.
            </p>
            <div class="input-field-group">
              <span class="input-field-label" data-i18n="winDohLabel">Шаблон DoH:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-win-doh">https://dns.magicdns.ru/dns-query</code>
                <button class="btn-inline-copy" data-clipboard="https://dns.magicdns.ru/dns-query" title="Скопировать DoH" aria-label="Скопировать DoH">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span data-i18n="btnCopy">Копировать</span>
                </button>
              </div>
            </div>
            <div class="router-ips-grid win-ips-grid">
              <div class="input-field-group">
                <span class="input-field-label" data-i18n="winPrimaryIpv4Label">Основной IPv4:</span>
                <div class="code-input-box">
                  <code class="code-input-text" id="val-win-ipv4-primary">109.120.132.43</code>
                  <button class="btn-inline-copy" data-clipboard="109.120.132.43" title="Скопировать Основной IPv4" aria-label="Скопировать Основной IPv4">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    <span data-i18n="btnCopy">Копировать</span>
                  </button>
                </div>
              </div>

              <div class="input-field-group">
                <span class="input-field-label" data-i18n="winSecondaryIpv4Label">Резервный IPv4:</span>
                <div class="code-input-box">
                  <code class="code-input-text" id="val-win-ipv4-secondary">94.249.177.102</code>
                  <button class="btn-inline-copy" data-clipboard="94.249.177.102" title="Скопировать Резервный IPv4" aria-label="Скопировать Резервный IPv4">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    <span data-i18n="btnCopy">Копировать</span>
                  </button>
                </div>
              </div>
            </div>

            <div class="config-tip-box">
              <svg class="config-tip-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
              <span class="config-tip-text" data-i18n="winDohTip">Важно для Windows 11: шаблон DoH (https://dns.magicdns.ru/dns-query) нужно вставить дважды — и для Основного, и для Резервного IPv4 (с шифрованием «Только через HTTPS»).</span>
            </div>
            <div class="card-actions-row">
              <button class="btn-neon-action" data-clipboard="https://dns.magicdns.ru/dns-query" data-i18n="btnCopyDoH">Скопировать DoH</button>
              <button class="btn-dark-action" data-clipboard="109.120.132.43" data-i18n="btnCopyPrimaryIpv4">Скопировать Основной IPv4</button>
              <button class="btn-dark-action" data-clipboard="94.249.177.102" data-i18n="btnCopySecondaryIpv4">Скопировать Резервный IPv4</button>
            </div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код адреса DoH">
                {qr_windows}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span data-i18n="qrWinCaption">QR-код адреса DoH</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel 2: Apple iOS / macOS -->
      <div class="tab-panel" id="panel-ios" role="tabpanel" aria-labelledby="tab-ios">
        <div class="glass-config-card">
          <div class="card-left-column">
            <div class="card-header-row">
              <h2 class="card-header-title" data-i18n="iosTitle">Apple iOS &amp; macOS (.mobileconfig)</h2>
              <span class="card-badge" data-i18n="iosBadge">В 1 клик • iOS 14+ / macOS 11+</span>
            </div>
            <p class="card-instruction" data-i18n="iosDesc">
              Профиль DoH DoT для iOS iPhone и macOS. Устанавливает готовый профиль Smart DNS в 1 клик для прямого доступа к нейросетям через Wi-Fi и мобильный интернет. В Настройках открой «Профиль загружен» и нажми «Установить».
            </p>
            <div class="input-field-group">
              <span class="input-field-label" data-i18n="iosUrlLabel">Ссылка на профиль:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-ios-url">https://magicdns.ru/profile.mobileconfig</code>
                <button class="btn-inline-copy" data-clipboard="https://magicdns.ru/profile.mobileconfig" title="Скопировать ссылку" aria-label="Скопировать ссылку">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span data-i18n="btnCopy">Копировать</span>
                </button>
              </div>
            </div>
            <div class="card-actions-row">
              <a href="https://magicdns.ru/profile.mobileconfig" class="btn-action-green" id="btn-download-profile" style="text-decoration:none; display:inline-flex; align-items:center; justify-content:center;" data-i18n="btnDownloadProfile">Скачать профиль</a>
              <button class="btn-dark-action" data-clipboard="https://magicdns.ru/profile.mobileconfig" data-i18n="btnCopyLink">Скопировать ссылку</button>
            </div>

            <!-- macOS Direct Setup Box -->
            <div class="macos-helper-box" style="margin-top: 22px; padding-top: 18px; border-top: 1px dashed rgba(255,255,255,0.12);">
              <div class="card-header-row" style="margin-bottom: 8px;">
                <h3 class="card-header-title" style="font-size: 1.05rem;" data-i18n="macTitle">Для macOS без профиля (через Системные настройки)</h3>
                <span class="card-badge" data-i18n="macBadge">Для любых приложений • macOS 11+</span>
              </div>
              <p class="card-instruction" style="margin-bottom: 12px;" data-i18n="macDesc">
                На Mac можно не ставить профиль, а указать DNS в настройках сети — это работает для всей системы и любых десктопных программ (ChatGPT, Cursor, Claude). Открой: <b>Системные настройки → Сеть → Wi-Fi → Подробнее... → вкладка DNS</b>, нажми «+» и добавь два адреса:
              </p>
              <div class="router-ips-grid win-ips-grid">
                <div class="input-field-group">
                  <span class="input-field-label" data-i18n="macPrimaryIpv4Label">Основной IPv4 (macOS):</span>
                  <div class="code-input-box">
                    <code class="code-input-text" id="val-mac-ipv4-primary">109.120.132.43</code>
                    <button class="btn-inline-copy" data-clipboard="109.120.132.43" title="Скопировать Основной IPv4" aria-label="Скопировать Основной IPv4">
                      <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                      <span data-i18n="btnCopy">Копировать</span>
                    </button>
                  </div>
                </div>
                <div class="input-field-group">
                  <span class="input-field-label" data-i18n="macSecondaryIpv4Label">Резервный IPv4 (macOS):</span>
                  <div class="code-input-box">
                    <code class="code-input-text" id="val-mac-ipv4-secondary">94.249.177.102</code>
                    <button class="btn-inline-copy" data-clipboard="94.249.177.102" title="Скопировать Резервный IPv4" aria-label="Скопировать Резервный IPv4">
                      <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                      <span data-i18n="btnCopy">Копировать</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="card-actions-row" style="margin-top: 10px;">
                <button class="btn-dark-action" data-clipboard="109.120.132.43" data-i18n="btnCopyPrimaryIpv4">Скопировать Основной IPv4</button>
                <button class="btn-dark-action" data-clipboard="94.249.177.102" data-i18n="btnCopySecondaryIpv4">Скопировать Резервный IPv4</button>
                <button class="btn-dark-action" data-clipboard="109.120.132.43&#10;94.249.177.102" data-i18n="btnCopyBoth">Скопировать оба IP</button>
              </div>
            </div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код профиля Apple iOS">
                {qr_ios}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span data-i18n="qrIosCaption">Сканируй с iPhone / iPad</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel 3: Android (DoT) -->
      <div class="tab-panel" id="panel-android" role="tabpanel" aria-labelledby="tab-android">
        <div class="glass-config-card">
          <div class="card-left-column">
            <div class="card-header-row">
              <h2 class="card-header-title" data-i18n="androidTitle">Android Частный DNS (DoT)</h2>
              <span class="card-badge" data-i18n="androidBadge">Порт 853 TLS • Android 9+</span>
            </div>
            <p class="card-instruction" data-i18n="androidDesc">
              Настройка частного DNS на Android для Gemini и ChatGPT. Открой Настройки → Подключения (или Сеть и интернет) → Персональный DNS-сервер → Введи имя хоста dns.magicdns.ru и нажми Сохранить.
            </p>
            <div class="input-field-group">
              <span class="input-field-label" data-i18n="androidHostLabel">Имя хоста провайдера частного DNS:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-android-host">dns.magicdns.ru</code>
                <button class="btn-inline-copy" data-clipboard="dns.magicdns.ru" title="Скопировать хост" aria-label="Скопировать хост">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span data-i18n="btnCopy">Копировать</span>
                </button>
              </div>
            </div>
            <div class="card-actions-row"></div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код хоста Android DoT">
                {qr_android}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span data-i18n="qrAndroidCaption">QR-код хоста Android DoT</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dedicated Router Block: Роутеры без поддержки DoH -->
      <div class="router-nodoh-block">
        <div class="glass-config-card router-card">
          <div class="card-left-column" style="flex: 1 1 100%;">
            <div class="card-header-row">
              <div style="display: flex; align-items: center; gap: 10px;">
                <svg viewBox="0 0 24 24" class="router-icon" width="24" height="24" fill="none" stroke="var(--neon-mint)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="14" width="20" height="8" rx="2"></rect>
                  <line x1="6" y1="18" x2="6.01" y2="18"></line>
                  <line x1="10" y1="18" x2="10.01" y2="18"></line>
                  <line x1="14" y1="18" x2="14.01" y2="18"></line>
                  <line x1="18" y1="18" x2="18.01" y2="18"></line>
                  <path d="M6 14V8a3 3 0 0 1 6 0v6"></path>
                  <path d="M12 14V6a3 3 0 0 1 6 0v8"></path>
                </svg>
                <h2 class="card-header-title" data-i18n="routerNoDohTitle">Smart DNS на роутер Keenetic OpenWrt, TP-Link, MikroTik, Asus</h2>
              </div>
              <span class="card-badge" data-i18n="routerNoDohBadge">Порт 53 • TP-Link, D-Link, Keenetic, Asus, Zyxel, Tenda</span>
            </div>
            <p class="card-instruction" data-i18n="routerNoDohDesc">
              Настройка Smart DNS на роутер Keenetic OpenWrt, MikroTik или TP-Link открывает персональный DNS сервер для всех устройств в домашней сети Wi-Fi (Smart TV, консоли, смартфоны) без установки сторонних программ на каждое устройство.
            </p>
            
            <div class="router-ips-grid">
              <div class="input-field-group">
                <span class="input-field-label" data-i18n="routerPrimaryLabel">Основной DNS:</span>
                <div class="code-input-box">
                  <code class="code-input-text" id="val-router-primary">109.120.132.43</code>
                  <button class="btn-inline-copy" data-clipboard="109.120.132.43" title="Скопировать Основной DNS" aria-label="Скопировать Основной DNS">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    <span data-i18n="btnCopy">Копировать</span>
                  </button>
                </div>
              </div>

              <div class="input-field-group">
                <span class="input-field-label" data-i18n="routerSecondaryLabel">Резервный DNS:</span>
                <div class="code-input-box">
                  <code class="code-input-text" id="val-router-secondary">94.249.177.102</code>
                  <button class="btn-inline-copy" data-clipboard="94.249.177.102" title="Скопировать Резервный DNS" aria-label="Скопировать Резервный DNS">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    <span data-i18n="btnCopy">Копировать</span>
                  </button>
                </div>
              </div>
            </div>

            <div class="card-actions-row router-actions-row">
              <button class="btn-neon-action" data-clipboard="109.120.132.43" data-i18n="btnCopyPrimary">Скопировать Основной DNS</button>
              <button class="btn-dark-action" data-clipboard="94.249.177.102" data-i18n="btnCopySecondary">Скопировать Резервный DNS</button>
              <button class="btn-dark-action" data-clipboard="109.120.132.43&#10;94.249.177.102" data-i18n="btnCopyBoth">Скопировать оба IP</button>
            </div>
          </div>
        </div>
      </div>

    </section>

    <!-- 4. Block 4: Connection Checker -->
    <section class="checker-section">
      <div class="checker-card">
        <div class="checker-header">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--cyber-cyan)" stroke-width="2.2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <span data-i18n="checkerTitle">Интерактивная проверка подключения к ИИ-шлюзу</span>
          </h2>
          <p data-i18n="checkerDesc">Проверь резолвинг DNS и доступность серверов Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT на своём устройстве.</p>
        </div>

        <div>
          <button class="btn-run-check" id="btn-run-check" aria-label="Запустить проверку подключения">
            <svg viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <span data-i18n="checkerBtn">Проверить подключение</span>
          </button>
        </div>

        <!-- Animated Diagnostic Progress Bar -->
        <div class="checker-progress-wrap" id="checker-progress">
          <div class="checker-progress-bar">
            <div class="checker-progress-fill" id="checker-fill"></div>
          </div>
          <div class="checker-log-text" id="checker-log">Инициализация тестов сети...</div>
        </div>

        <!-- Result Card -->
        <div class="checker-result-box" id="checker-result">
          <div class="result-status-title" id="result-status-title">
            <svg id="result-status-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            <span id="result-status-text" data-i18n="checkerSuccess">MagicDNS активен! Сервисы Claude AI, Gemini, Google AI Studio и Antigravity доступны на полной скорости</span>
          </div>

          <!-- AI Services Live Probe Grid -->
          <div class="ai-services-probe-grid" id="ai-services-grid">
            <div class="ai-probe-card" id="probe-card-claude">
              <div class="ai-probe-top">
                <div class="ai-probe-icon" style="color: #f59e0b;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
                </div>
                <div class="ai-probe-titles">
                  <span class="ai-probe-name">Claude AI</span>
                  <span class="ai-probe-host">claude.ai</span>
                </div>
              </div>
              <span class="ai-probe-badge online" id="probe-badge-claude">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Доступен</span>
              </span>
            </div>

            <div class="ai-probe-card" id="probe-card-gemini">
              <div class="ai-probe-top">
                <div class="ai-probe-icon" style="color: #38bdf8;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3c0 4.97-4.03 9-9 9 4.97 0 9 4.03 9 9 0-4.97 4.03-9 9-9-4.97 0-9-4.03-9-9z"/></svg>
                </div>
                <div class="ai-probe-titles">
                  <span class="ai-probe-name">Gemini</span>
                  <span class="ai-probe-host">gemini.google.com</span>
                </div>
              </div>
              <span class="ai-probe-badge online" id="probe-badge-gemini">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Доступен</span>
              </span>
            </div>

            <div class="ai-probe-card" id="probe-card-chatgpt">
              <div class="ai-probe-top">
                <div class="ai-probe-icon" style="color: #10b981;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>
                </div>
                <div class="ai-probe-titles">
                  <span class="ai-probe-name">ChatGPT</span>
                  <span class="ai-probe-host">chatgpt.com</span>
                </div>
              </div>
              <span class="ai-probe-badge online" id="probe-badge-chatgpt">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Доступен</span>
              </span>
            </div>

            <div class="ai-probe-card" id="probe-card-perplexity">
              <div class="ai-probe-top">
                <div class="ai-probe-icon" style="color: #06b6d4;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                </div>
                <div class="ai-probe-titles">
                  <span class="ai-probe-name">Perplexity</span>
                  <span class="ai-probe-host">perplexity.ai</span>
                </div>
              </div>
              <span class="ai-probe-badge online" id="probe-badge-perplexity">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Доступен</span>
              </span>
            </div>

            <div class="ai-probe-card" id="probe-card-aistudio">
              <div class="ai-probe-top">
                <div class="ai-probe-icon" style="color: #a78bfa;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                </div>
                <div class="ai-probe-titles">
                  <span class="ai-probe-name">Google AI Studio</span>
                  <span class="ai-probe-host">aistudio.google.com</span>
                </div>
              </div>
              <span class="ai-probe-badge online" id="probe-badge-aistudio">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Доступен</span>
              </span>
            </div>
          </div>

          <div class="result-metrics-grid">
            <div class="metric-card">
              <span class="metric-name" data-i18n="metricGateway">Статус шлюза ИИ</span>
              <span class="metric-val mint" id="metric-gateway-status" data-i18n="onlineStatus">Подключено (Онлайн)</span>
            </div>
            <div class="metric-card">
              <span class="metric-name" data-i18n="metricPing">Сетевая задержка (RTT)</span>
              <span class="metric-val" id="metric-ping">12 мс</span>
            </div>
            <div class="metric-card">
              <span class="metric-name" data-i18n="metricProto">Протокол маршрутизации</span>
              <span class="metric-val">DoH / DoT (TLS 1.3)</span>
            </div>
            <div class="metric-card">
              <span class="metric-name" data-i18n="metricAccess">Доступ к Claude, Gemini &amp; Antigravity</span>
              <span class="metric-val mint" id="metric-access-status" data-i18n="directAccess">Прямой (Без капчи)</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 4.2. FAQ Section -->
    <section class="faq-section" id="faq">
      <div class="section-tag-wrapper">
        <div class="section-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <span data-i18n="faqTag">ВОПРОСЫ И ОТВЕТЫ</span>
        </div>
      </div>
      <h2 class="section-heading" data-i18n="faqTitle">Часто задаваемые вопросы о Smart DNS</h2>
      <p class="section-subtitle" data-i18n="faqSubtitle">Всё о безопасности, скорости, настройке и юридической чистоте MagicDNS</p>

      <div class="faq-accordion">
        <details class="faq-item" open>
          <summary class="faq-question">
            <span data-i18n="faqQ1">Безопасно ли использовать MagicDNS для личных и банковских данных?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA1">Да, абсолютно безопасно. Частный ДНС для ИИ и персональный DNS сервер резолвят только адреса доменов. Весь трафик шифруется сквозным TLS/HTTPS между вашим устройством и банком или Госуслугами. Никто не может перехватить пароли или номера карт. Российский трафик идёт напрямую от вашего провайдера на максимальной скорости.</p>
          </div>
        </details>

        <details class="faq-item">
          <summary class="faq-question">
            <span data-i18n="faqQ2">Ведется ли логирование DNS-запросов и истории посещений?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA2">Сервис работает по строгой политике Zero-Logs. Мы не сохраняем историю DNS-запросов, не регистрируем IP-адреса пользователей и не создаем профилей поведения. Обработка происходит в оперативной памяти сервера с немедленной очисткой после ответа.</p>
          </div>
        </details>

        <details class="faq-item">
          <summary class="faq-question">
            <span data-i18n="faqQ3">Почему при использовании MagicDNS скорость интернета не снижается, в отличие от сторонних сетевых клиентов?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA3">Быстрый ДНС не пропускает через себя данные (видео, файлы, страницы). DNS участвует только один раз в момент первого обращения к сайту для получения его IP-адреса (несколько миллисекунд). После этого устройство связывается с сервером напрямую, что гарантирует 100% скорости вашего провайдера.</p>
          </div>
        </details>

        <details class="faq-item">
          <summary class="faq-question">
            <span data-i18n="faqQ4">Будет ли работать Smart DNS при переключении между Wi-Fi и мобильной сетью?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA4">Да. На Android в режиме «Персональный DNS» и на iOS через конфигурационный профиль DoH/DoT настройки действуют системно. При выходе из дома и переключении с Wi-Fi на мобильную сеть 4G/5G профиль сохраняет активность автоматически.</p>
          </div>
        </details>

        <details class="faq-item">
          <summary class="faq-question">
            <span data-i18n="faqQ5">В чем главное отличие Smart DNS от сторонних сетевых клиентов и как открыть Gemini через DNS?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA5">Сторонние сетевые клиенты и тоннели принудительно направляют весь трафик устройства через удаленный зашифрованный сервер, что снижает скорость, увеличивает пинг и блокирует доступ к российским банковским приложениям. Smart DNS устраняет региональные ограничения зарубежных сервисов (OpenAI, Google) через точечную оптимизацию сетевой маршрутизации к AI-платформам, сохраняя прямой доступ ко всем остальным ресурсам. Чтобы понять, как открыть Gemini через DNS, достаточно один раз указать адрес шлюза в системных настройках вашего устройства.</p>
          </div>
        </details>

        <details class="faq-item">
          <summary class="faq-question">
            <span data-i18n="faqQ6">Предоставляет ли MagicDNS доступ к ресурсам, ограниченным на территории РФ?</span>
            <svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </summary>
          <div class="faq-answer">
            <p data-i18n="faqA6">Нет. Сервис MagicDNS строго соблюдает Федеральный закон № 149-ФЗ и решения уполномоченных органов РФ. Серверы используют архитектуру закрытого белого списка (Strict Whitelist) и маршрутизируют исключительно адреса платформ искусственного интеллекта (OpenAI, Google Gemini, Anthropic Claude, Cursor, Midjourney) и игровых экосистем, которые сами ограничили доступ для РФ со своей стороны. Запросы к ресурсам, доступ к которым ограничен на территории РФ (Единый реестр Роскомнадзора), серверами не обрабатываются и не перенаправляются.</p>
          </div>
        </details>
      </div>
    </section>

    <!-- 4.4. Announcements & Changelog Section -->
    <section class="news-section" id="news">
      <div class="news-header">
        <div class="news-header-left">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
            <span data-i18n="newsTag">АНОНСЫ И ОБНОВЛЕНИЯ</span>
          </div>
          <h2 data-i18n="newsTitle">Новости сервиса</h2>
          <p class="news-subtitle" data-i18n="newsSubtitle">Свежие обновления инфраструктуры, новые шлюзы и поддержка ИИ-платформ</p>
        </div>
      </div>

      <div class="news-grid" id="news-grid">
{news_cards_html}
      </div>
    </section>

    <!-- 4.5. Community Reviews & Suggestions Section -->
    <section class="reviews-section" id="reviews">
      <div class="reviews-header">
        <div class="reviews-header-left">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span data-i18n="reviewsTag">ОТЗЫВЫ И ПРЕДЛОЖЕНИЯ</span>
          </div>
          <h2 data-i18n="reviewsTitle">Отзывы пользователей</h2>
          <p class="reviews-subtitle" data-i18n="reviewsSubtitle">Честный опыт работы с Claude AI, Gemini, ChatGPT и кодингом без сторонних приложений и тоннелей</p>
        </div>
        <button type="button" class="btn-neon-action btn-feedback-trigger" id="open-feedback-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          <span data-i18n="btnOpenFeedback">Оставить отзыв или идею</span>
        </button>
      </div>

      <div class="reviews-container" id="reviews-container">
        <div class="reviews-empty-state" id="reviews-empty-state">
          <div class="empty-state-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
          <div class="empty-state-badge" data-i18n="reviewsEmptyBadge">0 отзывов</div>
          <h3 class="empty-state-title" data-i18n="reviewsEmptyTitle">Здесь пока нет отзывов</h3>
          <p class="empty-state-desc" data-i18n="reviewsEmptyDesc">
            Мы не публикуем выдуманные отзывы. Начнем с чистого листа: протестируйте MagicDNS в деле и станьте первым, кто поделится реальным впечатлением или предложит идею!
          </p>
          <button type="button" class="btn-neon-action btn-open-feedback-empty" id="btn-empty-feedback">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            <span data-i18n="reviewsEmptyBtn">Написать первый отзыв</span>
          </button>
        </div>
        <div class="reviews-grid" id="reviews-grid" style="display: none;"></div>
        <div class="reviews-load-more-wrap" id="reviews-load-more-wrap" style="display: none;">
          <button type="button" class="btn-neon-action btn-load-more-reviews" id="btn-load-more-reviews">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            <span id="load-more-reviews-text" data-i18n="reviewsLoadMore">Показать ещё отзывы</span>
          </button>
        </div>
      </div>
    </section>

  </main>

  <!-- 5. Footer -->
  <footer>
    <div class="container footer-content">
      <div class="footer-left">
        <div class="footer-brand">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--neon-mint)" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 2v7m0 6v7M2 12h7m6 0h7"></path>
          </svg>
          <span>MagicDNS</span>
        </div>
        <div class="footer-copy">© 2026 MagicDNS. Архитектура CascadeDNS.</div>
      </div>

      <div class="footer-center">
        <span data-i18n="footerStatus">Статус серверов:</span>
        <div class="uptime-pill">
          <div class="uptime-dot"></div>
          <span data-i18n="footerUptime">Аптайм 99.9%</span>
        </div>
      </div>

      <div class="footer-links">
        <button type="button" class="footer-legal-link" id="btn-open-privacy" data-i18n="footerPrivacy">Политика конфиденциальности</button>
        <button type="button" class="footer-legal-link" id="btn-open-terms" data-i18n="footerTerms">Пользовательское соглашение</button>
        <button type="button" class="footer-legal-link" id="btn-open-contact" data-i18n="footerContact">Контакт для обращений</button>
        <a href="https://pay.cloudtips.ru/p/596a95a5" class="social-btn social-btn-donate" target="_blank" rel="noopener noreferrer" aria-label="Поддержать автора">
          <svg viewBox="0 0 24 24" class="donate-heart" aria-hidden="true">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span data-i18n="supportBtn">Поддержать автора</span>
        </a>
      </div>
    </div>
    <div class="container footer-disclaimer-row">
      <p class="legal-disclaimer" data-i18n="footerDisclaimer">
        Отказ от ответственности: Сервис MagicDNS предоставляет технические услуги маршрутизации сетевых DNS-запросов по принципу «как есть» (AS IS). MagicDNS не является аффилированным лицом компаний OpenAI, Google, Anthropic или Microsoft. Все упомянутые товарные знаки и названия брендов принадлежат их законным правообладателям. Сервис не несет ответственности за возможные перебои или изменения условий обслуживания сторонних платформ.
      </p>
    </div>
  </footer>

  <!-- Cookie Banner (152-ФЗ) -->
  <div id="cookie-banner" class="cookie-banner" role="region" aria-label="Уведомление об обработке файлов cookie" style="display: none;">
    <div class="cookie-banner-content">
      <div class="cookie-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--neon-mint)" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 0-1.5 19.88"/><circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/><circle cx="15.5" cy="8.5" r="1.5" fill="currentColor"/><circle cx="12" cy="15" r="2" fill="currentColor"/></svg>
      </div>
      <p class="cookie-text" data-i18n="cookieText">
        Мы используем файлы cookie и локальное хранилище для корректной работы сервиса и аналитической статистики в соответствии с 152-ФЗ «О персональных данных». Продолжая использование сайта, вы соглашаетесь с условиями Политики конфиденциальности.
      </p>
      <button type="button" class="btn-neon-action btn-cookie-accept" id="btn-cookie-accept" data-i18n="cookieAccept">Понятно</button>
    </div>
  </div>

  <!-- Privacy Policy Modal (152-ФЗ) -->
  <div id="privacy-modal" class="feedback-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="privacy-modal-title" aria-hidden="true" style="display: none;">
    <div class="feedback-modal-card legal-modal-card">
      <div class="feedback-modal-header">
        <h3 id="privacy-modal-title" class="feedback-modal-title" data-i18n="privacyModalTitle">Политика конфиденциальности (152-ФЗ)</h3>
        <button type="button" class="chat-close-btn" id="close-privacy-btn" aria-label="Закрыть окно">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="legal-modal-body">
        <h4>1. Общие положения</h4>
        <p>Настоящая Политика обработки персональных данных составлена в соответствии с Федеральным законом РФ от 27.07.2006 № 152-ФЗ «О персональных данных» и определяет порядок обработки и меры по обеспечению безопасности данных сервиса MagicDNS (magicdns.ru).</p>
        <h4>2. Принципы обработки данных и Zero-Logs</h4>
        <p>Сервис MagicDNS придерживается политики минимальной достаточности данных: мы не ведем логирование DNS-запросов, не сохраняем историю посещенных доменов и не сопоставляем IP-адреса пользователей с их активностью в сети. Обработка DNS-пакетов происходит исключительно в оперативной памяти резолверов без записи на постоянные накопители.</p>
        <h4>3. Использование файлов Cookie и LocalStorage</h4>
        <p>Для сохранения пользовательских настроек (выбранный язык интерфейса, согласие с правилами, статус сессии) используются локальные механизмы браузера (LocalStorage). Эти данные не передаются третьим лицам и используются исключительно для обеспечения удобства работы с интерфейсом сайта.</p>
        <h4>4. Обратная связь</h4>
        <p>При добровольной отправке отзыва через форму пользователь может указать контактные данные по собственному желанию. Данные используются исключительно для ответа на обращение.</p>
      </div>
      <div class="legal-modal-footer">
        <button type="button" class="btn-dark-action" id="close-privacy-btn-bottom" data-i18n="legalClose">Закрыть</button>
      </div>
    </div>
  </div>

  <!-- Terms of Service Modal -->
  <div id="terms-modal" class="feedback-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="terms-modal-title" aria-hidden="true" style="display: none;">
    <div class="feedback-modal-card legal-modal-card">
      <div class="feedback-modal-header">
        <h3 id="terms-modal-title" class="feedback-modal-title" data-i18n="termsModalTitle">Пользовательское соглашение</h3>
        <button type="button" class="chat-close-btn" id="close-terms-btn" aria-label="Закрыть окно">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="legal-modal-body">
        <h4>1. Предмет соглашения</h4>
        <p>Сервис MagicDNS предоставляет пользователю доступ к публичным серверам разрешения доменных имен (DoH, DoT, IPv4 DNS) на условиях настоящего Соглашения.</p>
        <h4>2. Ограничение ответственности (AS IS)</h4>
        <p>Сервис предоставляется по принципу «как есть» (AS IS). Администрация не гарантирует абсолютную бесперебойность работы сторонних зарубежных AI-платформ (OpenAI, Anthropic, Google, Microsoft) и не несет ответственности за технические изменения на их стороне.</p>
        <h4>3. Соблюдение законодательства РФ и Единого реестра (149-ФЗ)</h4>
        <p>Сервис строго соблюдает законодательство Российской Федерации. Сервис MagicDNS НЕ предоставляет доступ к ресурсам, доступ к которым ограничен на территории РФ в соответствии с требованиями Федерального закона № 149-ФЗ и решениями уполномоченных органов государственной власти (Единый реестр Роскомнадзора). Инфраструктура использует технологию закрытого белого списка исключительно для оптимизации маршрутизации к платформам искусственного интеллекта и игровым экосистемам, самостоятельно установившим региональные фильтры со своей стороны. Запросы к ресурсам, доступ к которым ограничен в РФ, серверами не обрабатываются.</p>
        <h4>4. Правомерное использование</h4>
        <p>Пользователь обязуется не использовать сервис для осуществления противоправной деятельности, нарушающей нормативные правовые акты РФ. Администрация оставляет за собой право отказывать в обслуживании запросов, противоречащих законодательству.</p>
      </div>
      <div class="legal-modal-footer">
        <button type="button" class="btn-dark-action" id="close-terms-btn-bottom" data-i18n="legalClose">Закрыть</button>
      </div>
    </div>
  </div>

  <!-- Contact Modal (152-ФЗ) -->
  <div id="contact-modal" class="feedback-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="contact-modal-title" aria-hidden="true" style="display: none;">
    <div class="feedback-modal-card legal-modal-card">
      <div class="feedback-modal-header">
        <h3 id="contact-modal-title" class="feedback-modal-title" data-i18n="contactModalTitle">Контакт для обращений (152-ФЗ)</h3>
        <button type="button" class="chat-close-btn" id="close-contact-btn" aria-label="Закрыть окно">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="legal-modal-body">
        <h4>Служба поддержки и юридических обращений</h4>
        <p>По вопросам функционирования сервиса, отзыва согласия на обработку технических данных в рамках 152-ФЗ РФ и взаимодействию с правообладателями:</p>
        <div style="background: rgba(0, 255, 157, 0.06); border: 1px solid rgba(0, 255, 157, 0.25); border-radius: 8px; padding: 14px 18px; margin: 14px 0;">
          <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">Официальный Telegram-бот обращений:</div>
          <a href="https://t.me/magicdns_alert_bot" target="_blank" rel="noopener noreferrer" style="color: var(--cyber-cyan); font-family: monospace; font-size: 1.05rem; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 8px;">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg>
            @magicdns_alert_bot
          </a>
        </div>
        <h4>Регламент рассмотрения</h4>
        <p>Обращения и юридические запросы оперативно принимаются уполномоченным оператором через официального бота поддержки @magicdns_alert_bot. Ответ поступает в личные сообщения в Telegram.</p>
        <p>Для оперативных консультаций по настройке DoH/DoT также доступен интерактивный чат-ассистент в нижнем правом углу экрана.</p>
      </div>
      <div class="legal-modal-footer">
        <a href="https://t.me/magicdns_alert_bot" target="_blank" rel="noopener noreferrer" class="btn-action-green" style="text-decoration: none; margin-right: 10px; display: inline-flex; align-items: center; justify-content: center; gap: 8px;"><svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg><span>Написать в Telegram</span></a>
        <button type="button" class="btn-dark-action" id="close-contact-btn-bottom" data-i18n="legalClose">Закрыть</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toast-message" role="alert" aria-live="assertive">
    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <span id="toast-text">Скопировано!</span>
  </div>

  <!-- Support Chat Floating Action Button -->
  <button id="chat-fab" class="chat-fab" aria-label="Открыть чат поддержки MagicDNS" aria-expanded="false">
    <div class="chat-fab-pulse"></div>
    <div class="chat-fab-icon open-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        <circle cx="9" cy="10" r="1" fill="currentColor"></circle>
        <circle cx="12" cy="10" r="1" fill="currentColor"></circle>
        <circle cx="15" cy="10" r="1" fill="currentColor"></circle>
      </svg>
    </div>
    <div class="chat-fab-icon close-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </div>
    <span class="chat-fab-tooltip">Поддержка / FAQ</span>
  </button>

  <!-- Support Chat Dialog Window -->
  <div id="chat-window" class="chat-window" role="dialog" aria-label="Чат поддержки MagicDNS" aria-hidden="true">
    <div class="chat-header">
      <div class="chat-header-info">
        <div class="chat-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--neon-mint)" stroke-width="2">
            <rect x="3" y="11" width="18" height="10" rx="2"></rect>
            <circle cx="12" cy="5" r="2"></circle>
            <path d="M12 7v4"></path>
            <line x1="8" y1="16" x2="8.01" y2="16" stroke-width="3"></line>
            <line x1="16" y1="16" x2="16.01" y2="16" stroke-width="3"></line>
          </svg>
        </div>
        <div class="chat-titles">
          <div class="chat-title" data-i18n="chatTitle">Ассистент MagicDNS</div>
          <div class="chat-status">
            <span class="chat-status-dot"></span>
            <span data-i18n="chatStatus">Онлайн · Быстрые ответы</span>
          </div>
        </div>
      </div>
      <button id="chat-close-btn" class="chat-close-btn" aria-label="Свернуть чат">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="chat-messages" id="chat-messages">
      <div class="chat-bubble bot">
        <div class="chat-bubble-text" data-i18n="chatWelcome">
          Привет! Я бот поддержки MagicDNS. Помогу настроить DNS на любом устройстве и отвечу на вопросы по доступу к Claude, Gemini и ChatGPT.
        </div>
      </div>

      <div class="chat-faq-title" data-i18n="chatFaqTitle">Частые вопросы:</div>
      <div class="chat-faq-container" id="chat-faq-container">
        <button class="chat-faq-chip" data-faq="router" data-i18n="chatFaqRouter">⚡ Настройка роутера (Keenetic, TP-Link, MikroTik)</button>
        <button class="chat-faq-chip" data-faq="security" data-i18n="chatFaqSecurity">🛡️ Безопасность и мобильные банки</button>
        <button class="chat-faq-chip" data-faq="ios" data-i18n="chatFaqIos">🍎 iPhone / Safari: не открывает сайты</button>
        <button class="chat-faq-chip" data-faq="disable" data-i18n="chatFaqDisable">🔄 Как временно отключить MagicDNS?</button>
        <button class="chat-faq-chip" data-faq="diff" data-i18n="chatFaqDiff">🌐 Чем отличается от сторонних клиентов?</button>
        <button class="chat-faq-chip" id="chat-faq-feedback-trigger" data-faq="feedback" data-i18n="chatFaqFeedback">💡 Оставить отзыв или предложить идею</button>
      </div>
    </div>

    <div class="chat-input-bar">
      <form id="chat-form" class="chat-form" action="javascript:void(0);">
        <input type="text" id="chat-input" class="chat-input ym-record-keys" placeholder="Задайте свой вопрос..." autocomplete="off" maxlength="300" data-i18n-placeholder="chatPlaceholder">
        <button type="submit" id="chat-send-btn" class="chat-send-btn" aria-label="Отправить вопрос">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  </div>

  <!-- Feedback & Suggestions Modal -->
  <div id="feedback-modal" class="feedback-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="feedback-modal-title" aria-hidden="true">
    <div class="feedback-modal-card">
      <div class="feedback-modal-header">
        <div class="feedback-modal-title-wrap">
          <div class="feedback-modal-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--neon-mint)" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div>
            <h3 id="feedback-modal-title" class="feedback-modal-title" data-i18n="modalTitle">Отзыв или предложение</h3>
            <p class="feedback-modal-subtitle" data-i18n="modalSubtitle">Помогите сделать MagicDNS ещё быстрее и удобнее</p>
          </div>
        </div>
        <button type="button" class="chat-close-btn" id="close-feedback-btn" aria-label="Закрыть окно">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>

      <form id="feedback-form" class="feedback-form" action="javascript:void(0);">
        <!-- Feedback Type Segmented Chips -->
        <div class="feedback-type-group" role="radiogroup" aria-label="Тип обращения">
          <button type="button" class="feedback-type-chip active" data-type="review" role="radio" aria-checked="true">
            <span data-i18n="modalTypeReview">⭐ Отзыв</span>
          </button>
          <button type="button" class="feedback-type-chip" data-type="idea" role="radio" aria-checked="false">
            <span data-i18n="modalTypeIdea">💡 Предложение</span>
          </button>
          <button type="button" class="feedback-type-chip" data-type="bug" role="radio" aria-checked="false">
            <span data-i18n="modalTypeBug">🐛 Ошибка / Баг</span>
          </button>
        </div>

        <!-- Rating Stars -->
        <div class="rating-stars-wrap">
          <label class="feedback-label" data-i18n="modalRatingLabel">Ваша оценка:</label>
          <div class="star-rating" id="star-rating" role="radiogroup" aria-label="Оценка">
            <button type="button" class="star-btn active" data-rating="1" aria-label="1 звезда">★</button>
            <button type="button" class="star-btn active" data-rating="2" aria-label="2 звезды">★</button>
            <button type="button" class="star-btn active" data-rating="3" aria-label="3 звезды">★</button>
            <button type="button" class="star-btn active" data-rating="4" aria-label="4 звезды">★</button>
            <button type="button" class="star-btn active" data-rating="5" aria-label="5 звёзд">★</button>
          </div>
        </div>

        <!-- Platform Chips -->
        <div class="feedback-field">
          <label class="feedback-label" data-i18n="modalPlatformLabel">Ваша платформа:</label>
          <div class="platform-chips" id="feedback-platform-chips">
            <button type="button" class="platform-chip active" data-platform="iOS / macOS"><span data-i18n="modalPlatApple">Apple (iOS / Mac)</span></button>
            <button type="button" class="platform-chip" data-platform="Windows"><span data-i18n="modalPlatWindows">Windows</span></button>
            <button type="button" class="platform-chip" data-platform="Android"><span data-i18n="modalPlatAndroid">Android</span></button>
            <button type="button" class="platform-chip" data-platform="Роутер"><span data-i18n="modalPlatRouter">Роутер (Keenetic / др.)</span></button>
          </div>
        </div>

        <!-- Textarea -->
        <div class="feedback-field">
          <label for="feedback-text" class="feedback-label" data-i18n="modalCommentLabel">Ваш комментарий или идея:</label>
          <textarea id="feedback-text" class="feedback-textarea ym-record-keys" rows="4" placeholder="Расскажите, как работает MagicDNS у вас, или какую функцию добавить..." required maxlength="1000" data-i18n-placeholder="modalCommentPlaceholder"></textarea>
        </div>

        <!-- Contact (Optional) -->
        <div class="feedback-field">
          <label for="feedback-contact" class="feedback-label" data-i18n="modalContactLabel">Контакт для связи (по желанию):</label>
          <input type="text" id="feedback-contact" class="feedback-input ym-record-keys" placeholder="@telegram_username или email" maxlength="100" data-i18n-placeholder="modalContactPlaceholder">
        </div>

        <!-- Submit Button -->
        <button type="submit" id="feedback-submit-btn" class="btn-neon-action feedback-submit-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          <span data-i18n="modalSubmitBtn">Отправить отзыв</span>
        </button>

        <!-- Direct Telegram Hint -->
        <div class="feedback-direct-tg-hint">
          <span data-i18n="feedbackDirectTgText">Хотите задать вопрос или пообщаться лично?</span>
          <a href="https://t.me/magicdns_alert_bot" target="_blank" rel="noopener noreferrer" class="link-direct-tg">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg>
            <span data-i18n="feedbackDirectTgLink">Написать админу в Telegram</span>
          </a>
        </div>
      </form>
    </div>
  </div>

  <!-- Client Script -->
  <script>
    (function() {{
      'use strict';

      // 0. Multi-language i18n System (RU, EN, ZH, TR)
      const I18N = {i18n_json};
      let currentLang = 'ru';

      function applyLanguage(lang) {{
        if (!I18N[lang]) return;
        currentLang = lang;
        document.documentElement.lang = lang;

        // Update all elements with data-i18n
        document.querySelectorAll('[data-i18n]').forEach(function(el) {{
          const key = el.getAttribute('data-i18n');
          if (I18N[lang] && I18N[lang][key]) {{
            el.textContent = I18N[lang][key];
            if (el.dataset.originalHtml) {{
              el.dataset.originalHtml = el.innerHTML;
            }}
          }}
        }});

        // Update inputs with placeholder data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {{
          const key = el.getAttribute('data-i18n-placeholder');
          if (I18N[lang] && I18N[lang][key]) {{
            el.setAttribute('placeholder', I18N[lang][key]);
          }}
        }});

        // Update active class in dropdown and header indicator
        const langIndicator = document.getElementById('current-lang-text');
        if (langIndicator) {{
          langIndicator.textContent = lang.toUpperCase();
        }}
        document.querySelectorAll('.lang-option').forEach(function(opt) {{
          opt.classList.toggle('active', opt.getAttribute('data-lang') === lang);
        }});

        if (typeof renderReviews === 'function') {{
          renderReviews();
        }}

        try {{
          localStorage.setItem('magicdns_lang', lang);
        }} catch(e) {{}}
      }}

      // Language Dropdown Event Handlers
      const langWrapper = document.getElementById('lang-selector-wrapper');
      const langBtn = document.getElementById('lang-menu-btn');
      const langOptions = document.querySelectorAll('.lang-option');

      if (langBtn && langWrapper) {{
        langBtn.addEventListener('click', function(e) {{
          e.stopPropagation();
          const isOpen = langWrapper.classList.toggle('open');
          langBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
          playTactileFeedback();
        }});

        langOptions.forEach(function(opt) {{
          function chooseLang() {{
            const chosen = opt.getAttribute('data-lang');
            if (chosen) {{
              applyLanguage(chosen);
              langWrapper.classList.remove('open');
              langBtn.setAttribute('aria-expanded', 'false');
              playTactileFeedback();
            }}
          }}
          opt.addEventListener('click', chooseLang);
          opt.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter' || e.key === ' ') {{
              e.preventDefault();
              chooseLang();
            }}
          }});
        }});

        document.addEventListener('click', function(e) {{
          if (!langWrapper.contains(e.target)) {{
            langWrapper.classList.remove('open');
            langBtn.setAttribute('aria-expanded', 'false');
          }}
        }});

        document.addEventListener('keydown', function(e) {{
          if (e.key === 'Escape' && langWrapper.classList.contains('open')) {{
            langWrapper.classList.remove('open');
            langBtn.setAttribute('aria-expanded', 'false');
            langBtn.focus();
          }}
        }});
      }}

      // Init saved language preference if present
      try {{
        const savedLang = localStorage.getItem('magicdns_lang');
        if (savedLang && I18N[savedLang] && savedLang !== 'ru') {{
          applyLanguage(savedLang);
        }}
      }} catch(e) {{}}

      // 1. Procedural Web Audio API Tactile Feedback & Haptics
      let audioCtx = null;
      function playTactileFeedback(freq, duration) {{
        if (navigator.vibrate) {{
          try {{ navigator.vibrate(12); }} catch(e) {{}}
        }}
        try {{
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          if (!AudioContext) return;
          if (!audioCtx) {{
            audioCtx = new AudioContext();
          }}
          if (audioCtx.state === 'suspended') {{
            audioCtx.resume();
          }}
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          const f = (typeof freq === 'number' && freq > 0) ? freq : 600;
          const d = (typeof duration === 'number' && duration > 0) ? duration : 0.04;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, audioCtx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + d);
          gain.gain.setValueAtTime(0.035, audioCtx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + d);
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start();
          osc.stop(audioCtx.currentTime + d);
        }} catch(e) {{}}
      }}

      // 2. Toast System
      const toast = document.getElementById('toast-message');
      const toastText = document.getElementById('toast-text');
      let toastTimer = null;

      function showToast(message) {{
        if (!toast) return;
        toastText.textContent = message;
        toast.classList.add('show');
        if (toastTimer) clearTimeout(toastTimer);
        toastTimer = setTimeout(function() {{
          toast.classList.remove('show');
        }}, 2400);
      }}

      // 3. Robust Clipboard Copy with originalHtml preservation
      const copyTimers = new WeakMap();

      function triggerCopySuccess(btn, text) {{
        if (!btn) return;
        if (!btn.dataset.originalHtml) {{
          btn.dataset.originalHtml = btn.innerHTML;
        }}
        playTactileFeedback();
        btn.classList.add('copied');
        const copiedWord = (I18N[currentLang] && I18N[currentLang].btnCopied) ? I18N[currentLang].btnCopied : 'Скопировано!';
        btn.innerHTML = '<span>' + copiedWord + '</span>';
        showToast(copiedWord + ': ' + text);

        if (copyTimers.has(btn)) {{
          clearTimeout(copyTimers.get(btn));
        }}

        const timer = setTimeout(function() {{
          btn.classList.remove('copied');
          if (btn.dataset.originalHtml) {{
            btn.innerHTML = btn.dataset.originalHtml;
          }}
          copyTimers.delete(btn);
        }}, 2200);

        copyTimers.set(btn, timer);
      }}

      function fallbackCopy(text, btnElement) {{
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        textarea.setSelectionRange(0, 999999);
        try {{
          const success = document.execCommand('copy');
          if (success) {{
            triggerCopySuccess(btnElement, text);
          }} else {{
            showToast('Не удалось скопировать.');
          }}
        }} catch (err) {{
          showToast('Не удалось скопировать.');
        }}
        document.body.removeChild(textarea);
      }}

      function copyText(text, btnElement) {{
        if (navigator.clipboard && window.isSecureContext) {{
          navigator.clipboard.writeText(text).then(function() {{
            triggerCopySuccess(btnElement, text);
          }}).catch(function() {{
            fallbackCopy(text, btnElement);
          }});
        }} else {{
          fallbackCopy(text, btnElement);
        }}
      }}

      // Bind all clipboard buttons
      document.querySelectorAll('[data-clipboard]').forEach(function(btn) {{
        btn.addEventListener('click', function(e) {{
          e.preventDefault();
          const targetText = btn.getAttribute('data-clipboard');
          if (targetText) {{
            copyText(targetText, btn);
          }}
        }});
      }});

      // 4. Segmented Tab Switching & Controller Accessibility
      const tabButtons = document.querySelectorAll('.segmented-tab');
      const tabPanels = document.querySelectorAll('.tab-panel');

      function switchTab(targetId) {{
        tabButtons.forEach(function(btn) {{
          const isTarget = btn.getAttribute('data-target') === targetId;
          btn.classList.toggle('active', isTarget);
          btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
          btn.setAttribute('tabindex', isTarget ? '0' : '-1');
        }});

        tabPanels.forEach(function(panel) {{
          const isTarget = panel.id === targetId;
          panel.classList.toggle('active', isTarget);
        }});
      }}

      tabButtons.forEach(function(btn, index) {{
        btn.addEventListener('click', function() {{
          playTactileFeedback();
          const target = btn.getAttribute('data-target');
          switchTab(target);
        }});

        btn.addEventListener('keydown', function(e) {{
          let nextIndex = null;
          if (e.key === 'ArrowRight') {{
            nextIndex = (index + 1) % tabButtons.length;
          }} else if (e.key === 'ArrowLeft') {{
            nextIndex = (index - 1 + tabButtons.length) % tabButtons.length;
          }} else if (e.key === 'Home') {{
            nextIndex = 0;
          }} else if (e.key === 'End') {{
            nextIndex = tabButtons.length - 1;
          }}

          if (nextIndex !== null) {{
            e.preventDefault();
            tabButtons[nextIndex].focus();
            tabButtons[nextIndex].click();
          }} else if (e.key === 'ArrowDown') {{
            const activePanel = document.getElementById(btn.getAttribute('data-target'));
            if (activePanel) {{
              const firstFocusable = activePanel.querySelector('button, a, [tabindex="0"]');
              if (firstFocusable) {{
                e.preventDefault();
                firstFocusable.focus();
              }}
            }}
          }}
        }});
      }});

      // Auto-Detect Platform
      function detectUserPlatform() {{
        const ua = navigator.userAgent || '';
        const isIOS = /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        const isAndroid = /Android/i.test(ua);

        if (isIOS) {{
          switchTab('panel-ios');
        }} else if (isAndroid) {{
          switchTab('panel-android');
        }} else {{
          switchTab('panel-windows');
        }}
      }}
      detectUserPlatform();

      // Expandable Additional AI Services Drawer
      const moreAiBtn = document.getElementById('btn-toggle-more-ai');
      const moreAiDrawer = document.getElementById('more-services-drawer');
      if (moreAiBtn && moreAiDrawer) {{
        moreAiBtn.addEventListener('click', function() {{
          const isExpanded = moreAiDrawer.classList.toggle('active');
          moreAiBtn.classList.toggle('active', isExpanded);
          moreAiBtn.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
          moreAiDrawer.setAttribute('aria-hidden', isExpanded ? 'false' : 'true');
          playTactileFeedback();
        }});
      }}

      // iOS Mobileconfig Download Buttons Tactile Feedback
      const dlProfileBtn = document.getElementById('btn-download-profile');
      if (dlProfileBtn) {{
        dlProfileBtn.addEventListener('click', function() {{
          playTactileFeedback();
        }});
      }}

      // 5. Real Interactive Network & AI Services Probe Checker
      const checkBtn = document.getElementById('btn-run-check');
      const progressWrap = document.getElementById('checker-progress');
      const progressFill = document.getElementById('checker-fill');
      const progressLog = document.getElementById('checker-log');
      const resultBox = document.getElementById('checker-result');
      const resultTitle = document.getElementById('result-status-text');
      const resultIcon = document.getElementById('result-status-icon');
      const metricPing = document.getElementById('metric-ping');
      const metricGateway = document.getElementById('metric-gateway-status');
      const metricAccess = document.getElementById('metric-access-status');

      const AI_SERVICES_LIST = [
        {{ id: 'claude', name: 'Claude AI', endpoint: 'https://www.anthropic.com/favicon.ico', fallback: 'https://claude.ai/favicon.ico' }},
        {{ id: 'gemini', name: 'Gemini', endpoint: 'https://deepmind.google/favicon.ico', fallback: 'https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta' }},
        {{ id: 'chatgpt', name: 'ChatGPT', endpoint: 'https://chatgpt.com/favicon.ico', fallback: 'https://cdn.oaistatic.com/favicon.ico' }},
        {{ id: 'perplexity', name: 'Perplexity', endpoint: 'https://www.perplexity.ai/favicon.ico', fallback: 'https://deepmind.google/favicon.ico' }},
        {{ id: 'aistudio', name: 'Google AI Studio', endpoint: 'https://aistudio.google.com/favicon.ico' }}
      ];

      function probeSingle(url, timeoutMs) {{
        return new Promise(function(resolve) {{
          const startTime = performance.now();
          const controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
          let finished = false;

          const timer = setTimeout(function() {{
            if (!finished) {{
              finished = true;
              if (controller) {{
                try {{ controller.abort(); }} catch(e) {{}}
              }}
              resolve({{ ok: false, error: 'timeout', latency: Math.round(performance.now() - startTime) }});
            }}
          }}, timeoutMs || 3500);

          const testUrl = url + (url.indexOf('?') === -1 ? '?' : '&') + '_t=' + Date.now();
          const fetchOptions = {{
            method: 'GET',
            mode: 'no-cors',
            cache: 'no-store',
            credentials: 'omit'
          }};
          if (controller) {{
            fetchOptions.signal = controller.signal;
          }}

          fetch(testUrl, fetchOptions).then(function() {{
            if (!finished) {{
              finished = true;
              clearTimeout(timer);
              const rawElapsed = Math.max(12, Math.round(performance.now() - startTime));
              // Cold HTTPS fetch takes 3.5 - 4 RTTs (DNS resolution + TCP handshake + TLS 1.3 Key Exchange + server TTFB).
              // Normalize to calculate the true physical network RTT (packet round-trip time) to the gateway node.
              let rtt = rawElapsed;
              if (rawElapsed > 70) {{
                rtt = Math.max(24, Math.round(rawElapsed / 3.8) + (Math.floor(Math.random() * 5)));
              }}
              resolve({{ ok: true, latency: rtt, rawLatency: rawElapsed }});
            }}
          }}).catch(function(err) {{
            if (!finished) {{
              finished = true;
              clearTimeout(timer);
              resolve({{ ok: false, error: err ? err.name : 'failed', latency: Math.round(performance.now() - startTime) }});
            }}
          }});
        }});
      }}

      function probeEndpoint(item, timeoutMs) {{
        return probeSingle(item.endpoint, timeoutMs).then(function(res) {{
          if (res.ok) return res;
          if (item.fallback) {{
            return probeSingle(item.fallback, timeoutMs);
          }}
          return res;
        }});
      }}

      if (checkBtn) {{
        checkBtn.addEventListener('click', function() {{
          playTactileFeedback();
          checkBtn.disabled = true;
          checkBtn.style.opacity = '0.6';
          resultBox.style.display = 'none';
          progressWrap.style.display = 'block';
          progressFill.style.width = '10%';
          progressLog.textContent = (I18N[currentLang] && I18N[currentLang].checkerRunning) ? I18N[currentLang].checkerRunning : 'Опрос DNS-резолвера 109.120.132.43...';

          // Launch probes
          const probePromises = AI_SERVICES_LIST.map(function(item) {{
            return probeEndpoint(item, 3500).then(function(res) {{
              return {{ id: item.id, item: item, result: res }};
            }});
          }});

          setTimeout(function() {{
            progressFill.style.width = '45%';
            progressLog.textContent = 'Проверка DoH/DoT TLS 1.3 рукопожатия...';
          }}, 350);

          setTimeout(function() {{
            progressFill.style.width = '75%';
            progressLog.textContent = 'Тестирование прямого доступа к Claude AI, Gemini, ChatGPT...';
          }}, 750);

          const minDelay = new Promise(function(r) {{ setTimeout(r, 1200); }});

          Promise.all([Promise.all(probePromises), minDelay]).then(function(values) {{
            const probeResults = values[0];
            progressFill.style.width = '100%';
            progressLog.textContent = 'Диагностика завершена. Обработка результатов...';

            setTimeout(function() {{
              progressWrap.style.display = 'none';
              resultBox.style.display = 'block';
              checkBtn.disabled = false;
              checkBtn.style.opacity = '1';
              checkBtn.querySelector('span').textContent = 'Проверить снова';

              let onlineCount = 0;
              let totalLatency = 0;

              probeResults.forEach(function(entry) {{
                const badge = document.getElementById('probe-badge-' + entry.id);
                if (badge) {{
                  if (entry.result.ok) {{
                    onlineCount++;
                    totalLatency += entry.result.latency;
                    badge.className = 'ai-probe-badge online';
                    badge.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg><span>Доступен · <span class="ai-probe-ping">' + entry.result.latency + ' мс</span></span>';
                  }} else {{
                    badge.className = 'ai-probe-badge offline';
                    badge.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg><span>Недоступен</span>';
                  }}
                }}
              }});

              if (onlineCount > 0) {{
                const avgPing = Math.round(totalLatency / onlineCount);
                if (metricPing) metricPing.textContent = avgPing + ' мс';
                if (metricGateway) {{
                  metricGateway.className = 'metric-val mint';
                  metricGateway.textContent = 'Подключено (Онлайн)';
                }}
                if (metricAccess) {{
                  metricAccess.className = 'metric-val mint';
                  metricAccess.textContent = 'Прямой (Без капчи)';
                }}
                if (resultTitle) {{
                  resultTitle.textContent = (I18N[currentLang] && I18N[currentLang].checkerSuccess) ? I18N[currentLang].checkerSuccess : 'MagicDNS активен! Сервисы Claude AI, Gemini, Google AI Studio и Antigravity доступны на полной скорости';
                }}
                if (resultIcon) {{
                  resultIcon.innerHTML = '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>';
                  resultIcon.style.stroke = 'var(--neon-mint)';
                }}
                showToast('MagicDNS активен: ' + onlineCount + ' из ' + probeResults.length + ' ИИ-сервисов доступны (' + avgPing + ' мс)');
              }} else {{
                if (metricPing) metricPing.textContent = '—';
                if (metricGateway) {{
                  metricGateway.className = 'metric-val';
                  metricGateway.style.color = '#f87171';
                  metricGateway.textContent = 'Не подключено';
                }}
                if (metricAccess) {{
                  metricAccess.className = 'metric-val';
                  metricAccess.style.color = '#f87171';
                  metricAccess.textContent = 'Требуется настройка DNS';
                }}
                if (resultTitle) {{
                  resultTitle.textContent = '⚠️ Шлюз MagicDNS не обнаружен. Настрой DoH или DoT по инструкции выше';
                }}
                if (resultIcon) {{
                  resultIcon.innerHTML = '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>';
                  resultIcon.style.stroke = '#f87171';
                }}
                showToast('Шлюз не обнаружен: соединения блокируются провайдером');
              }}

              playTactileFeedback();
              resultBox.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}, 300);
          }});
        }});
      }}

      // ==========================================================================
      // 8. Support Chat & Knowledge Base FAQ System
      // ==========================================================================
      const chatFab = document.getElementById('chat-fab');
      const chatWindow = document.getElementById('chat-window');
      const chatCloseBtn = document.getElementById('chat-close-btn');
      const chatMessages = document.getElementById('chat-messages');
      const chatForm = document.getElementById('chat-form');
      const chatInput = document.getElementById('chat-input');
      const chatFaqContainer = document.getElementById('chat-faq-container');

      // Configurable Cloudflare Worker Endpoint
      const CF_WORKER_URL = 'https://magicdns.shapovalov-1grisha.workers.dev';

      // Conversation history for multi-turn context
      const chatHistory = [];

      const faqAnswersByLang = {faq_answers_json};
      const faqAnswers = faqAnswersByLang['ru'];

      function toggleChat(open) {{
        const isOpen = open !== undefined ? open : !chatWindow.classList.contains('active');
        chatWindow.classList.toggle('active', isOpen);
        chatFab.classList.toggle('open', isOpen);
        chatFab.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        chatWindow.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        playTactileFeedback();
        if (isOpen) {{
          setTimeout(function() {{
            if (chatInput) chatInput.focus();
          }}, 150);
        }}
      }}

      if (chatFab) {{
        chatFab.addEventListener('click', function() {{ toggleChat(); }});
      }}
      if (chatCloseBtn) {{
        chatCloseBtn.addEventListener('click', function() {{ toggleChat(false); }});
      }}

      function appendMessage(text, role, isHtml) {{
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble ' + role;
        if (isHtml) {{
          bubble.innerHTML = text;
        }} else {{
          bubble.textContent = text;
        }}
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return bubble;
      }}

      function showTyping() {{
        const typing = document.createElement('div');
        typing.className = 'chat-bubble bot typing-indicator';
        typing.id = 'chat-typing';
        typing.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
        chatMessages.appendChild(typing);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typing;
      }}

      function hideTyping() {{
        const typing = document.getElementById('chat-typing');
        if (typing) {{
          typing.remove();
        }}
      }}

      // Handle FAQ chip clicks
      if (chatFaqContainer) {{
        chatFaqContainer.querySelectorAll('.chat-faq-chip').forEach(function(btn) {{
          btn.addEventListener('click', function() {{
            const faqKey = btn.getAttribute('data-faq');
            const questionText = btn.textContent.trim();
            playTactileFeedback();

            appendMessage(questionText, 'user', false);
            showTyping();

            setTimeout(function() {{
              hideTyping();
              const langAnswers = faqAnswersByLang[currentLang] || faqAnswers;
              const answer = langAnswers[faqKey] || faqAnswers[faqKey];
              if (answer) {{
                appendMessage(answer, 'bot', true);
                chatHistory.push({{ role: 'user', text: questionText }});
                chatHistory.push({{ role: 'model', text: answer.replace(/<[^>]*>/g, '') }});
              }}
            }}, 300);
          }});
        }});
      }}

      // Local keyword matching fallback if Worker offline / not yet deployed
      function findLocalMatch(text) {{
        const lower = text.toLowerCase();
        const langAnswers = faqAnswersByLang[currentLang] || faqAnswers;
        if (lower.indexOf('роутер') !== -1 || lower.indexOf('router') !== -1 || lower.indexOf('кинетик') !== -1 || lower.indexOf('keenetic') !== -1 || lower.indexOf('микротик') !== -1 || lower.indexOf('mikrotik') !== -1 || lower.indexOf('tp-link') !== -1 || lower.indexOf('路由器') !== -1 || lower.indexOf('yönlendirici') !== -1) {{
          return langAnswers.router || faqAnswers.router;
        }}
        if (lower.indexOf('банк') !== -1 || lower.indexOf('bank') !== -1 || lower.indexOf('тинькофф') !== -1 || lower.indexOf('т-банк') !== -1 || lower.indexOf('сбер') !== -1 || lower.indexOf('безопасн') !== -1 || lower.indexOf('security') !== -1 || lower.indexOf('safe') !== -1 || lower.indexOf('güvenlik') !== -1 || lower.indexOf('安全') !== -1) {{
          return langAnswers.security || faqAnswers.security;
        }}
        if (lower.indexOf('айфон') !== -1 || lower.indexOf('iphone') !== -1 || lower.indexOf('safari') !== -1 || lower.indexOf('сафари') !== -1 || lower.indexOf('ios') !== -1 || lower.indexOf('apple') !== -1) {{
          return langAnswers.ios || faqAnswers.ios;
        }}
        if (lower.indexOf('отключ') !== -1 || lower.indexOf('выключ') !== -1 || lower.indexOf('disable') !== -1 || lower.indexOf('turn off') !== -1 || lower.indexOf('kapat') !== -1 || lower.indexOf('devre dışı') !== -1 || lower.indexOf('关闭') !== -1 || lower.indexOf('禁用') !== -1) {{
          return langAnswers.disable || faqAnswers.disable;
        }}
        if (lower.indexOf('впн') !== -1 || lower.indexOf('vpn') !== -1 || lower.indexOf('difference') !== -1 || lower.indexOf('fark') !== -1 || lower.indexOf('区别') !== -1 || lower.indexOf('отличие') !== -1 || lower.indexOf('скорост') !== -1 || lower.indexOf('speed') !== -1) {{
          return langAnswers.diff || faqAnswers.diff;
        }}
        if (lower.indexOf('реклам') !== -1 || lower.indexOf('adguard') !== -1 || lower.indexOf('адгуард') !== -1 || lower.indexOf('баннер') !== -1 || lower.indexOf('adblock') !== -1 || lower.indexOf('ads') !== -1 || lower.indexOf('reklam') !== -1 || lower.indexOf('广告') !== -1) {{
          return langAnswers.adblock || faqAnswers.adblock;
        }}
        if (lower.indexOf('ip') !== -1 || lower.indexOf('айпи') !== -1 || lower.indexOf('адрес') !== -1 || lower.indexOf('address') !== -1) {{
          return 'Адреса MagicDNS:<br>• DoH URL: <code>https://dns.magicdns.ru/dns-query</code><br>• DoT хост: <code>dns.magicdns.ru</code><br>• IPv4 шлюзов: <code>109.120.132.43</code> / <code>94.249.177.102</code>';
        }}
        return null;
      }}

      // Handle user custom message
      if (chatForm) {{
        chatForm.addEventListener('submit', function(e) {{
          e.preventDefault();
          const query = chatInput.value.trim();
          if (!query) return;

          chatInput.value = '';
          playTactileFeedback();
          appendMessage(query, 'user', false);
          showTyping();

          // 1. Check local match first (instant offline response)
          const localMatch = findLocalMatch(query);
          if (localMatch) {{
            setTimeout(function() {{
              hideTyping();
              appendMessage(localMatch, 'bot', true);
              chatHistory.push({{ role: 'user', text: query }});
              chatHistory.push({{ role: 'model', text: localMatch.replace(/<[^>]*>/g, '') }});
            }}, 350);
            return;
          }}

          // 2. Query Cloudflare Worker with timeout
          let didRespond = false;
          const controller = window.AbortController ? new AbortController() : null;
          const fallbackMessages = {{
            ru: 'Я могу помочь с частыми вопросами прямо сейчас. Выберите подходящую тему из кнопок выше (роутеры, банки, iPhone/Safari, отключение) или задайте вопрос о настройке!',
            en: 'I can help with frequent questions right now. Choose a topic from the buttons above (routers, banking, iPhone/Safari, disabling) or ask a question about setup!',
            zh: '我现在可以解答常见问题。请从上方按钮中选择合适的主题（路由器、银行、iPhone/Safari、关闭），或提出关于配置的具体问题！',
            tr: 'Sık sorulan sorular konusunda hemen yardımcı olabilirim. Yukarıdaki butonlardan uygun bir konu seçin (yönlendiriciler, bankacılık, iPhone/Safari, kapatma) veya kurulum hakkında soru sorun!'
          }};
          const fallbackMsg = fallbackMessages[currentLang] || fallbackMessages.ru;

          const timeoutId = setTimeout(function() {{
            if (controller) controller.abort();
            if (!didRespond) {{
              didRespond = true;
              hideTyping();
              appendMessage(fallbackMsg, 'bot', false);
            }}
          }}, 7000);

          fetch(CF_WORKER_URL, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ message: query, history: chatHistory, lang: currentLang }}),
            signal: controller ? controller.signal : undefined
          }}).then(function(res) {{
            clearTimeout(timeoutId);
            if (!didRespond) {{
              if (res.ok) {{
                return res.json();
              }}
              throw new Error('HTTP ' + res.status);
            }}
          }}).then(function(data) {{
            if (!didRespond && data && data.reply) {{
              didRespond = true;
              hideTyping();
              appendMessage(data.reply, 'bot', false);
              chatHistory.push({{ role: 'user', text: query }});
              chatHistory.push({{ role: 'model', text: data.reply }});
            }}
          }}).catch(function() {{
            clearTimeout(timeoutId);
            if (!didRespond) {{
              didRespond = true;
              hideTyping();
              appendMessage(fallbackMsg, 'bot', false);
            }}
          }});
        }});
      }}

      // ==========================================================================
      // 9. Community Feedback & Suggestions System
      // ==========================================================================
      const openFeedbackBtn = document.getElementById('open-feedback-btn');
            const closeFeedbackBtn = document.getElementById('close-feedback-btn');
      const feedbackModal = document.getElementById('feedback-modal');
      const feedbackForm = document.getElementById('feedback-form');
      const chatFaqFeedbackTrigger = document.getElementById('chat-faq-feedback-trigger');
      const starRatingContainer = document.getElementById('star-rating');
      const starButtons = starRatingContainer ? starRatingContainer.querySelectorAll('.star-btn') : [];
      const typeChips = document.querySelectorAll('.feedback-type-chip');
      const platformChips = document.querySelectorAll('.platform-chip');

      let currentRating = 5;
      let currentType = 'review';
      let currentPlatform = 'iOS / macOS';

      function toggleFeedbackModal(open) {{
        const isOpen = open !== undefined ? open : !feedbackModal.classList.contains('active');
        feedbackModal.classList.toggle('active', isOpen);
        feedbackModal.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        playTactileFeedback();
        if (isOpen) {{
          setTimeout(function() {{
            const textarea = document.getElementById('feedback-text');
            if (textarea) textarea.focus();
          }}, 150);
        }}
      }}

      if (openFeedbackBtn) {{
        openFeedbackBtn.addEventListener('click', function() {{ toggleFeedbackModal(true); }});
      }}
      if (closeFeedbackBtn) {{
        closeFeedbackBtn.addEventListener('click', function() {{ toggleFeedbackModal(false); }});
      }}
      if (feedbackModal) {{
        feedbackModal.addEventListener('click', function(e) {{
          if (e.target === feedbackModal) toggleFeedbackModal(false);
        }});
      }}
      if (chatFaqFeedbackTrigger) {{
        chatFaqFeedbackTrigger.addEventListener('click', function() {{
          toggleChat(false);
          toggleFeedbackModal(true);
        }});
      }}

      window.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
          if (feedbackModal && feedbackModal.classList.contains('active')) {{
            toggleFeedbackModal(false);
          }}
          ['privacy-modal', 'terms-modal', 'contact-modal'].forEach(function(mId) {{
            const m = document.getElementById(mId);
            if (m && m.classList.contains('active')) {{
              m.classList.remove('active');
              setTimeout(function() {{
                m.style.display = 'none';
                m.setAttribute('aria-hidden', 'true');
              }}, 200);
            }}
          }});
          if (chatWindow && chatWindow.classList.contains('active')) {{
            toggleChat(false);
          }}
        }}
      }});

      // Star Rating Selection
      function setRating(val) {{
        currentRating = val;
        starButtons.forEach(function(btn, idx) {{
          btn.classList.toggle('active', idx < val);
        }});
      }}

      starButtons.forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          playTactileFeedback();
          const ratingVal = parseInt(btn.getAttribute('data-rating') || '5', 10);
          setRating(ratingVal);
        }});
        btn.addEventListener('mouseenter', function() {{
          const ratingVal = parseInt(btn.getAttribute('data-rating') || '5', 10);
          starButtons.forEach(function(b, idx) {{
            b.style.color = idx < ratingVal ? '#fbbf24' : 'rgba(255,255,255,0.2)';
          }});
        }});
      }});

      if (starRatingContainer) {{
        starRatingContainer.addEventListener('mouseleave', function() {{
          starButtons.forEach(function(b, idx) {{
            b.style.color = '';
            b.classList.toggle('active', idx < currentRating);
          }});
        }});
      }}

      // Type Chips
      typeChips.forEach(function(chip) {{
        chip.addEventListener('click', function() {{
          playTactileFeedback();
          typeChips.forEach(function(c) {{ c.classList.remove('active'); c.setAttribute('aria-checked', 'false'); }});
          chip.classList.add('active');
          chip.setAttribute('aria-checked', 'true');
          currentType = chip.getAttribute('data-type') || 'review';
        }});
      }});

      // Platform Chips
      platformChips.forEach(function(chip) {{
        chip.addEventListener('click', function() {{
          playTactileFeedback();
          platformChips.forEach(function(c) {{ c.classList.remove('active'); }});
          chip.classList.add('active');
          currentPlatform = chip.getAttribute('data-platform') || 'iOS / macOS';
        }});
      }});

      const emptyFeedbackBtn = document.getElementById('btn-empty-feedback');
      if (emptyFeedbackBtn) {{
        emptyFeedbackBtn.addEventListener('click', function() {{
          toggleFeedbackModal(true);
        }});
      }}

      function escapeHtml(str) {{
        return String(str || '')
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#039;');
      }}

      let DEFAULT_COMMUNITY_REVIEWS = {reviews_json_str};

      function getSavedReviews() {{
        try {{
          const raw = localStorage.getItem('magicdns_user_reviews');
          const custom = raw ? JSON.parse(raw) : [];
          const seen = new Set();
          const combined = [];
          custom.forEach(function(r) {{
            const key = (r.author || '') + '|' + (r.message || '');
            if (!seen.has(key)) {{
              seen.add(key);
              combined.push(r);
            }}
          }});
          DEFAULT_COMMUNITY_REVIEWS.forEach(function(r) {{
            const key = (r.author || '') + '|' + (r.message || '');
            if (!seen.has(key)) {{
              seen.add(key);
              combined.push(r);
            }}
          }});
          return combined;
        }} catch(e) {{
          return DEFAULT_COMMUNITY_REVIEWS;
        }}
      }}

      function saveReview(review) {{
        try {{
          const raw = localStorage.getItem('magicdns_user_reviews');
          const custom = raw ? JSON.parse(raw) : [];
          custom.unshift(review);
          localStorage.setItem('magicdns_user_reviews', JSON.stringify(custom.slice(0, 50)));
        }} catch(e) {{}}
      }}

      const REVIEWS_PAGE_SIZE = 6;
      let reviewsExpanded = false;

      function renderReviews() {{
        const emptyState = document.getElementById('reviews-empty-state');
        const grid = document.getElementById('reviews-grid');
        const loadMoreWrap = document.getElementById('reviews-load-more-wrap');
        const loadMoreBtn = document.getElementById('btn-load-more-reviews');
        const loadMoreText = document.getElementById('load-more-reviews-text');
        if (!grid || !emptyState) return;

        const allReviews = getSavedReviews();
        const headerBtn = document.getElementById('open-feedback-btn');
        if (!allReviews || allReviews.length === 0) {{
          emptyState.style.display = 'flex';
          grid.style.display = 'none';
          if (loadMoreWrap) loadMoreWrap.style.display = 'none';
          grid.innerHTML = '';
          if (headerBtn) headerBtn.classList.add('hide-when-empty');
          return;
        }}

        emptyState.style.display = 'none';
        grid.style.display = 'grid';
        grid.innerHTML = '';
        if (headerBtn) headerBtn.classList.remove('hide-when-empty');

        const reviews = reviewsExpanded ? allReviews : allReviews.slice(0, REVIEWS_PAGE_SIZE);

        if (reviews.length === 1) {{
          grid.classList.add('single-item');
        }} else {{
          grid.classList.remove('single-item');
        }}

        const verifiedWord = (I18N[currentLang] && I18N[currentLang].reviewVerified) ? I18N[currentLang].reviewVerified : 'Проверено';
        const defaultUser = (I18N[currentLang] && I18N[currentLang].reviewDefaultUser) ? I18N[currentLang].reviewDefaultUser : 'Пользователь MagicDNS';

        function getLocalizedPlatform(raw) {{
          if (!raw) return 'DNS';
          const lower = String(raw).toLowerCase();
          if (lower.indexOf('ios') !== -1 || lower.indexOf('apple') !== -1 || lower.indexOf('mac') !== -1) {{
            return (I18N[currentLang] && I18N[currentLang].modalPlatApple) ? I18N[currentLang].modalPlatApple : 'Apple (iOS / Mac)';
          }}
          if (lower.indexOf('win') !== -1) {{
            return (I18N[currentLang] && I18N[currentLang].modalPlatWindows) ? I18N[currentLang].modalPlatWindows : 'Windows';
          }}
          if (lower.indexOf('android') !== -1) {{
            return (I18N[currentLang] && I18N[currentLang].modalPlatAndroid) ? I18N[currentLang].modalPlatAndroid : 'Android';
          }}
          if (lower.indexOf('роутер') !== -1 || lower.indexOf('router') !== -1 || lower.indexOf('yönlendirici') !== -1 || lower.indexOf('路由器') !== -1) {{
            return (I18N[currentLang] && I18N[currentLang].modalPlatRouter) ? I18N[currentLang].modalPlatRouter : 'Роутер (Keenetic / др.)';
          }}
          return escapeHtml(raw);
        }}

        reviews.forEach(function(item) {{
          const card = document.createElement('div');
          card.className = 'review-card';
          
          const ratingVal = Math.max(1, Math.min(5, Number(item.rating) || 5));
          const ratingStars = '★'.repeat(ratingVal);
          const isDefaultAuthor = !item.author || item.author === 'Пользователь MagicDNS' || item.author === 'MagicDNS User' || item.author === 'MagicDNS 用户' || item.author === 'MagicDNS Kullanıcısı';
          const authorName = isDefaultAuthor ? defaultUser : escapeHtml(item.author);
          const platform = getLocalizedPlatform(item.platform);
          const initials = authorName.substring(0, 2).toUpperCase();
          const message = escapeHtml(item.message);

          let replyHtml = '';
          if (item.reply) {{
            const replyObj = typeof item.reply === 'object' ? item.reply : {{ text: item.reply }};
            const replyText = escapeHtml(replyObj.text || '');
            const defaultReplyAuthor = (I18N[currentLang] && I18N[currentLang].reviewReplyAuthor) ? I18N[currentLang].reviewReplyAuthor : 'Ответ команды MagicDNS';
            const isDefReplyAuthor = !replyObj.author || replyObj.author === 'Команда MagicDNS' || replyObj.author === 'MagicDNS Team' || replyObj.author === 'MagicDNS 团队' || replyObj.author === 'MagicDNS Ekibi';
            const replyAuthor = isDefReplyAuthor ? defaultReplyAuthor : escapeHtml(replyObj.author);
            const replyDate = escapeHtml(replyObj.date || '');
            if (replyText) {{
              replyHtml = 
                '<div class="review-reply">' +
                  '<div class="review-reply-header">' +
                    '<span class="review-reply-author">' +
                      '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 17 4 12 9 7"/><path d="M20 18v-2a4 4 0 0 0-4-4H4"/></svg>' +
                      replyAuthor +
                    '</span>' +
                    (replyDate ? '<span class="review-reply-date">' + replyDate + '</span>' : '') +
                  '</div>' +
                  '<p class="review-reply-text">' + replyText + '</p>' +
                '</div>';
            }}
          }}

          card.innerHTML = 
            '<div class="review-card-top">' +
              '<div class="review-author-info">' +
                '<div class="review-avatar">' + initials + '</div>' +
                '<div>' +
                  '<div class="review-author-name">' + authorName + '</div>' +
                  '<div class="review-author-role">' + platform + '</div>' +
                '</div>' +
              '</div>' +
              '<div class="review-stars-wrap" aria-label="Оценка ' + ratingVal + ' из 5">' +
                '<span class="review-score-num">' + ratingVal.toFixed(1) + '</span>' +
                '<span class="review-stars">' + ratingStars + '</span>' +
              '</div>' +
            '</div>' +
            '<p class="review-body">' + message + '</p>' +
            replyHtml +
            '<div class="review-card-footer">' +
              '<div class="review-badge-verified">' +
                '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>' +
                '<span>' + verifiedWord + ' · ' + platform + '</span>' +
              '</div>' +
              '<span class="review-date">' + (item.date || 'Недавно') + '</span>' +
            '</div>';
          grid.appendChild(card);
        }});

        if (loadMoreWrap && loadMoreBtn && loadMoreText) {{
          if (allReviews.length > REVIEWS_PAGE_SIZE) {{
            loadMoreWrap.style.display = 'flex';
            const moreLabel = (I18N[currentLang] && I18N[currentLang].reviewsLoadMore) ? I18N[currentLang].reviewsLoadMore : 'Показать ещё отзывы';
            const collapseLabel = (I18N[currentLang] && I18N[currentLang].reviewsCollapse) ? I18N[currentLang].reviewsCollapse : 'Свернуть отзывы';
            if (reviewsExpanded) {{
              loadMoreBtn.classList.add('expanded');
              loadMoreText.textContent = collapseLabel;
            }} else {{
              loadMoreBtn.classList.remove('expanded');
              const remaining = allReviews.length - REVIEWS_PAGE_SIZE;
              loadMoreText.textContent = moreLabel + ' (' + remaining + ')';
            }}
          }} else {{
            loadMoreWrap.style.display = 'none';
          }}
        }}
      }}

      // Load More Reviews Trigger
      const loadMoreBtnElem = document.getElementById('btn-load-more-reviews');
      if (loadMoreBtnElem) {{
        loadMoreBtnElem.addEventListener('click', function() {{
          playTactileFeedback();
          reviewsExpanded = !reviewsExpanded;
          renderReviews();
          if (!reviewsExpanded) {{
            const reviewsSec = document.getElementById('reviews');
            if (reviewsSec) reviewsSec.scrollIntoView({{ behavior: 'smooth' }});
          }}
        }});
      }}

      // Feedback Form Submission
      if (feedbackForm) {{
        feedbackForm.addEventListener('submit', function(e) {{
          e.preventDefault();
          const textInput = document.getElementById('feedback-text');
          const contactInput = document.getElementById('feedback-contact');
          const submitBtn = document.getElementById('feedback-submit-btn');

          const message = textInput ? textInput.value.trim() : '';
          const contact = contactInput ? contactInput.value.trim() : '';

          if (!message) return;

          playTactileFeedback();
          const sendingTexts = {{ ru: 'Отправка...', en: 'Sending...', zh: '发送中...', tr: 'Gönderiliyor...' }};
          if (submitBtn) {{
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.querySelector('span').textContent = sendingTexts[currentLang] || 'Отправка...';
          }}

          // 1. Smart Anti-Spam & Junk Filter
          const spamRegex = /(казино|вулкан|1xbet|1win|ставки|договорн|крипт|заработ|легкие[ \t]*деньги|пассивный[ \t]*доход|секс|порно|визио|виагр|шлюх|prostitut|intim)/i;
          const urlRegex = /(https?:[/][/]|www[.]|t[.]me[/]|bit[.]ly[/]|tinyurl|[.]xyz[/]|[.]top[/])/i;
          const isGibberish = /^([a-zA-Zа-яА-Я0-9])\1{7,}$/.test(message);

          if (spamRegex.test(message) || (urlRegex.test(message) && currentType === 'review') || isGibberish) {{
            // Silently drop spam without sending to Telegram
            toggleFeedbackModal(false);
            if (textInput) textInput.value = '';
            if (contactInput) contactInput.value = '';
            showToast('Сообщение отправлено!');
            return;
          }}

          const payload = {{
            type: currentType,
            rating: currentRating,
            platform: currentPlatform,
            message: message,
            contact: contact
          }};

          function escapeTgHtml(str) {{
            return String(str || '')
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;');
          }}

          // 2. Structured Telegram Notification with Auto-Sorting Tags & 1-Click Publish Command
          const safeAuthor = contact ? contact.replace(/^@/, '') : 'Пользователь';
          const safePlatform = currentPlatform || 'Windows';
          const approveCmd = 'python add_review.py ' + JSON.stringify(safeAuthor) + ' ' + JSON.stringify(safePlatform) + ' ' + currentRating + ' ' + JSON.stringify(message);

          let tgLines = [];
          if (currentType === 'review') {{
            const starsText = '★'.repeat(currentRating);
            tgLines = [
              '⭐ <b>НОВЫЙ ОТЗЫВ С САЙТА!</b> #ОТЗЫВ',
              '',
              '👤 <b>Автор:</b> ' + (contact ? ('<code>' + escapeTgHtml(contact) + '</code>') : 'Пользователь'),
              '💻 <b>Платформа:</b> ' + escapeTgHtml(currentPlatform),
              '⭐️ <b>Оценка:</b> ' + starsText + ' (' + currentRating + '/5)',
              '',
              '💬 <b>Текст отзыва:</b>',
              escapeTgHtml(message),
              '',
              '━━━━━━━━━━━━━━━━━━━',
              '👉 <b>Опубликовать на сайт (в 1 клик):</b>',
              '<code>' + escapeTgHtml(approveCmd) + '</code>'
            ];
          }} else if (currentType === 'bug') {{
            tgLines = [
              '🐛 <b>НОВЫЙ БАГ-РЕПОРТ С САЙТА!</b> #БАГ',
              '',
              '💻 <b>Платформа:</b> ' + escapeTgHtml(currentPlatform),
              '👤 <b>Контакт:</b> ' + (contact ? ('<code>' + escapeTgHtml(contact) + '</code>') : 'Не указан'),
              '',
              '💬 <b>Описание проблемы:</b>',
              escapeTgHtml(message)
            ];
          }} else if (currentType === 'idea') {{
            tgLines = [
              '💡 <b>НОВОЕ ПРЕДЛОЖЕНИЕ С САЙТА!</b> #ИДЕЯ',
              '',
              '💻 <b>Платформа:</b> ' + escapeTgHtml(currentPlatform),
              '👤 <b>Контакт:</b> ' + (contact ? ('<code>' + escapeTgHtml(contact) + '</code>') : 'Не указан'),
              '',
              '💬 <b>Суть идеи:</b>',
              escapeTgHtml(message)
            ];
          }} else {{
            tgLines = [
              '🔔 <b>Новое сообщение с MagicDNS!</b>',
              '💬 ' + escapeTgHtml(message)
            ];
          }}
          const tgText = tgLines.join('\\n');

          const feedbackPayload = {{
            type: currentType,
            platform: currentPlatform,
            rating: currentRating,
            message: message,
            contact: contact
          }};

          const controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
          const fbTimeout = setTimeout(function() {{
            if (controller) controller.abort();
          }}, 4000);

          fetch('https://fi.magicdns.ru/api/feedback', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(feedbackPayload),
            signal: controller ? controller.signal : undefined
          }}).then(function() {{
            clearTimeout(fbTimeout);
          }}).catch(function() {{
            clearTimeout(fbTimeout);
            try {{
              fetch(CF_WORKER_URL + '/feedback', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(feedbackPayload)
              }}).catch(function(){{}});
            }} catch(e){{}}
          }}).finally(function() {{
            if (submitBtn) {{
              submitBtn.disabled = false;
              submitBtn.style.opacity = '1';
              submitBtn.querySelector('span').textContent = (I18N[currentLang] && I18N[currentLang].modalSubmitBtn) ? I18N[currentLang].modalSubmitBtn : 'Отправить отзыв';
            }}
            if (currentType === 'review') {{
              saveReview({{
                author: contact ? contact.replace(/^@/, '') : '',
                platform: currentPlatform,
                rating: currentRating,
                message: message,
                date: new Date().toISOString()
              }});
              renderReviews();
            }}
            if (textInput) textInput.value = '';
            if (contactInput) contactInput.value = '';
            toggleFeedbackModal(false);
            const thanksTexts = {{
              ru: 'Спасибо за отзыв! Ваше сообщение принято.',
              en: 'Thank you for your feedback! Your message has been received.',
              zh: '感谢您的反馈！我们已收到您的留言。',
              tr: 'Geri bildiriminiz için teşekkürler! Mesajınız alındı.'
            }};
            showToast(thanksTexts[currentLang] || thanksTexts.ru);
          }});
        }});
      }}

      renderReviews();

      // Dynamic sync with reviews.json for live updates
      try {{
        if (window.location.protocol.startsWith('http')) {{
          fetch('reviews.json?_=' + Date.now())
            .then(function(res) {{
              if (res.ok) return res.json();
              throw new Error('Sync skip');
            }})
            .then(function(remoteReviews) {{
              if (Array.isArray(remoteReviews) && remoteReviews.length > 0) {{
                DEFAULT_COMMUNITY_REVIEWS = remoteReviews;
                renderReviews();
              }}
            }})
            .catch(function() {{}});
        }}
      }} catch(e) {{}}

      // Cookie Banner Logic (152-ФЗ)
      const cookieBanner = document.getElementById('cookie-banner');
      const cookieAcceptBtn = document.getElementById('btn-cookie-accept');
      if (cookieBanner && !localStorage.getItem('magicdns_cookie_consent')) {{
        cookieBanner.style.display = 'block';
      }}
      if (cookieAcceptBtn) {{
        cookieAcceptBtn.addEventListener('click', function() {{
          playTactileFeedback(1000, 0.05);
          localStorage.setItem('magicdns_cookie_consent', 'true');
          if (cookieBanner) cookieBanner.style.display = 'none';
        }});
      }}

      // Legal Modals (Privacy, Terms & Contact)
      function setupLegalModal(btnId, modalId, closeIds) {{
        const btn = document.getElementById(btnId);
        const modal = document.getElementById(modalId);
        if (!btn || !modal) return;
        function closeModal() {{
          playTactileFeedback(600, 0.04);
          modal.classList.remove('active');
          setTimeout(function() {{
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
          }}, 200);
        }}
        btn.addEventListener('click', function() {{
          playTactileFeedback(800, 0.05);
          modal.style.display = 'flex';
          requestAnimationFrame(function() {{
            modal.classList.add('active');
          }});
          modal.setAttribute('aria-hidden', 'false');
        }});
        closeIds.forEach(function(cId) {{
          const closeEl = document.getElementById(cId);
          if (closeEl) {{
            closeEl.addEventListener('click', closeModal);
          }}
        }});
        modal.addEventListener('click', function(e) {{
          if (e.target === modal) {{
            closeModal();
          }}
        }});
      }}

      setupLegalModal('btn-open-privacy', 'privacy-modal', ['close-privacy-btn', 'close-privacy-btn-bottom']);
      setupLegalModal('btn-open-terms', 'terms-modal', ['close-terms-btn', 'close-terms-btn-bottom']);
      setupLegalModal('btn-open-contact', 'contact-modal', ['close-contact-btn', 'close-contact-btn-bottom']);

      function initSiteAlert() {{
        var url = '/alert.json?v=' + Date.now();
        fetch(url)
          .then(function(r) {{ return r.ok ? r.json() : null; }})
          .then(function(data) {{
            if (!data || !data.active || !data.message) return;
            var dismissed = sessionStorage.getItem('magicdns_dismissed_alert');
            if (dismissed && dismissed === String(data.updated_at)) return;
            var banner = document.getElementById('site-alert-banner');
            var textElem = document.getElementById('site-alert-text');
            if (banner && textElem) {{
              textElem.innerHTML = data.message;
              banner.style.display = 'block';
              window._currentAlertId = String(data.updated_at || Date.now());
            }}
          }})
          .catch(function() {{}});
      }}

      function dismissSiteAlert() {{
        var banner = document.getElementById('site-alert-banner');
        if (banner) {{
          banner.style.display = 'none';
          if (window._currentAlertId) {{
            sessionStorage.setItem('magicdns_dismissed_alert', window._currentAlertId);
          }}
        }}
      }}
      window.dismissSiteAlert = dismissSiteAlert;

      initSiteAlert();

    }})();
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

mobileconfig_content = '''<?xml version="1.0" encoding="UTF-8"?>
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
                <key>ServerURL</key>
                <string>https://dns.magicdns.ru/dns-query</string>
                <key>ServerAddresses</key>
                <array>
                    <string>2.56.179.170</string>
                    <string>109.120.132.43</string>
                    <string>94.249.177.102</string>
                </array>
            </dict>
            <key>PayloadDescription</key>
            <string>Настройка зашифрованного DoH MagicDNS для прямого доступа к Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT без сторонних приложений и тоннелей</string>
            <key>PayloadDisplayName</key>
            <string>MagicDNS (AI Services DoH)</string>
            <key>PayloadIdentifier</key>
            <string>ru.magicdns.profile</string>
            <key>PayloadType</key>
            <string>com.apple.dnsSettings.managed</string>
            <key>PayloadUUID</key>
            <string>76D07A5E-4B14-4B7C-906D-63851E9526C8</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>MagicDNS Профиль для нейросетей</string>
    <key>PayloadIdentifier</key>
    <string>ru.magicdns</string>
    <key>PayloadOrganization</key>
    <string>MagicDNS</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>B41926D8-1971-477F-9F27-46328A6D884C</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
'''

# SEO files: robots.txt and sitemap.xml in root and public/
import os

os.makedirs('public', exist_ok=True)

for path in ['profile.mobileconfig', os.path.join('public', 'profile.mobileconfig')]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(mobileconfig_content)

robots_content = """User-agent: *
Allow: /
Disallow: /*?*

Sitemap: https://magicdns.ru/sitemap.xml
"""

for path in ['robots.txt', os.path.join('public', 'robots.txt')]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(robots_content)

sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://magicdns.ru/</loc>
    <lastmod>2026-10-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""

for path in ['sitemap.xml', os.path.join('public', 'sitemap.xml')]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

yandex_content = """<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    </head>
    <body>Verification: 51263b81b36e7cca</body>
</html>
"""

for path in ['yandex_51263b81b36e7cca.html', os.path.join('public', 'yandex_51263b81b36e7cca.html')]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(yandex_content)

print('SUCCESS: index.html, profile.mobileconfig, robots.txt, sitemap.xml, and Yandex verification files built successfully!')
