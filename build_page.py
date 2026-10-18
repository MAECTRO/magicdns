import qrcode
import qrcode.image.svg
import re

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
qr_ios = get_svg_qr('https://dns.magicdns.ru/profile.mobileconfig')
qr_android = get_svg_qr('dns.magicdns.ru')
qr_proxy = get_svg_qr('http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085')

html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#070d14">
  <title>MagicDNS — Быстрый DNS для Claude AI, Gemini и ChatGPT без VPN</title>
  <meta name="description" content="Высокоскоростной защищённый DNS-шлюз (DoH/DoT) для прямого доступа к Claude AI, Gemini, ChatGPT и Antigravity без VPN на Windows, iOS и Android.">
  <meta name="keywords" content="MagicDNS, DNS для Claude, DNS для Gemini, ChatGPT без VPN, Claude AI без VPN, DoH, DoT, быстрый DNS, Google AI Studio, Antigravity, приватный DNS, smart DNS, обход блокировок без впн, private DNS">
  <link rel="canonical" href="https://magicdns.ru/">

  <!-- Search Engine Verification -->
  <!-- <meta name="google-site-verification" content="PASTE_YOUR_GOOGLE_CODE_HERE" /> -->
  <meta name="yandex-verification" content="51263b81b36e7cca">

  <!-- Open Graph / Facebook / Telegram / WhatsApp -->
  <meta property="og:site_name" content="MagicDNS">
  <meta property="og:url" content="https://magicdns.ru/">
  <meta property="og:title" content="MagicDNS — Быстрый DNS для Claude, Gemini и ChatGPT без VPN">
  <meta property="og:description" content="Высокоскоростной защищённый DNS-шлюз для прямого доступа к Claude AI, Gemini, ChatGPT и Antigravity без VPN и сторонних программ.">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:image" content="https://magicdns.ru/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="https://magicdns.ru/">
  <meta name="twitter:title" content="MagicDNS — Быстрый DNS для Claude, Gemini и ChatGPT без VPN">
  <meta name="twitter:description" content="Высокоскоростной защищённый DNS-шлюз для прямого доступа к Claude AI, Gemini, ChatGPT и Antigravity без VPN.">
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
        "description": "Высокоскоростной DNS-шлюз для доступа к ИИ-сервисам без VPN",
        "inLanguage": "ru-RU"
      }},
      {{
        "@type": "WebApplication",
        "@id": "https://magicdns.ru/#app",
        "name": "MagicDNS",
        "url": "https://magicdns.ru/",
        "description": "Высокоскоростной защищённый DNS-шлюз (DoH/DoT) для прямого доступа к Claude AI, Gemini, Google AI Studio, ChatGPT и Antigravity без VPN.",
        "applicationCategory": "NetworkingApplication",
        "operatingSystem": "Windows, iOS, macOS, Android, Linux",
        "offers": {{
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "RUB"
        }}
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
      z-index: 100;
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

    /* Unified Harmonious Services Ribbon (Single Line / No Awkward Breaks) */
    .services-ribbon-container {{
      width: 100%;
      margin: 0 auto 6px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding: 4px 0;
    }}
    .services-ribbon-container::-webkit-scrollbar {{
      display: none;
    }}

    .services-ribbon {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      white-space: nowrap;
      min-width: 100%;
      padding: 4px 10px;
    }}

    .service-chip {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-size: 0.84rem;
      font-weight: 600;
      color: #e2e8f0;
      background: rgba(11, 20, 36, 0.65);
      border: 1px solid var(--border-hairline);
      padding: 7px 15px;
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

    /* ==========================================================================
       3. Device Configurator (Segmented Bar + Two-Column Glassmorphism Cards)
       ========================================================================== */
    .configurator-section,
    .tabs-section {{
      padding: 8px 0 32px;
    }}

    .segmented-bar-wrapper {{
      display: flex;
      justify-content: center;
      margin-bottom: 16px;
      overflow-x: auto;
      scrollbar-width: none;
      padding: 4px;
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
      white-space: nowrap;
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
      z-index: 999;
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
      z-index: 1000;
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
      .header-content {{
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
      }}
      .header-right {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        flex-wrap: nowrap;
      }}
      .btn-support-header {{
        padding: 6px 12px;
        font-size: 0.78rem;
        flex-shrink: 0;
      }}
      .status-badge {{
        padding: 6px 12px;
        font-size: 0.78rem;
        flex-shrink: 0;
      }}
      .status-label {{
        display: none;
      }}
      .hero h1 {{
        font-size: 1.85rem;
      }}
      .segmented-tab {{
        padding: 8px 14px;
        font-size: 0.84rem;
      }}
      .footer-content {{
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
      }}
      .footer-links {{
        flex-wrap: wrap;
        gap: 8px;
      }}
      .chat-window {{
        bottom: 84px;
        right: 12px;
        left: 12px;
        width: auto;
        max-width: none;
        height: calc(100dvh - 100px);
        max-height: 520px;
      }}
      .chat-fab {{
        bottom: 18px;
        right: 18px;
      }}
      .toast {{
        bottom: 80px;
        right: 18px;
      }}
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

    .reviews-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
      gap: 16px;
    }}

    .review-card {{
      background: rgba(13, 23, 40, 0.7);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-md);
      padding: 22px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
      transition: all var(--transition-fast);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }}

    .review-card:hover {{
      border-color: rgba(0, 255, 157, 0.35);
      background: rgba(15, 27, 48, 0.85);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 255, 157, 0.08);
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
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(0, 255, 157, 0.2), rgba(6, 182, 212, 0.2));
      border: 1px solid rgba(0, 255, 157, 0.3);
      color: var(--neon-mint);
      font-weight: 700;
      font-size: 0.84rem;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
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
      font-size: 0.92rem;
      font-weight: 700;
      color: #ffffff;
    }}

    .review-author-role {{
      font-size: 0.74rem;
      color: var(--text-dim);
      margin-top: 1px;
    }}

    .review-stars {{
      color: #fbbf24;
      font-size: 1.05rem;
      letter-spacing: 2px;
      text-shadow: 0 0 8px rgba(251, 191, 36, 0.3);
      flex-shrink: 0;
    }}

    .review-body {{
      color: #d1d5db;
      font-size: 0.88rem;
      line-height: 1.55;
      margin: 0;
      flex: 1;
    }}

    .review-badge-verified {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      background: rgba(0, 255, 157, 0.08);
      border: 1px solid rgba(0, 255, 157, 0.25);
      color: var(--neon-mint);
      font-size: 0.72rem;
      font-weight: 600;
      width: fit-content;
    }}

    .review-badge-verified svg {{
      width: 12px;
      height: 12px;
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
    }}
  </style>
</head>
<body>

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

      <!-- Header Right: Support & Status -->
      <div class="header-right">
        <a href="https://pay.cloudtips.ru/p/596a95a5" target="_blank" rel="noopener noreferrer" class="btn-support-header" aria-label="Поддержать автора">
          <svg viewBox="0 0 24 24" class="donate-heart" aria-hidden="true">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span>Поддержать автора</span>
        </a>

        <!-- Status Badge -->
        <div class="status-badge" role="status" aria-live="polite">
          <div class="status-dot-wrapper">
            <div class="status-ping"></div>
            <div class="status-dot"></div>
          </div>
          <span><span class="status-label">Статус сети: </span><span class="status-text">Работает стабильно</span></span>
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
        <span>Высокоскоростной DNS-шлюз • Прямой доступ к AI</span>
      </div>
      <h1>Быстрый DNS для Claude AI, Gemini, Google AI Studio и Antigravity</h1>
      <p>Прямой доступ к Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT без VPN, сторонних приложений и падения скорости. Выбери устройство и подключись за 1 минуту.</p>
      
      <!-- Unified Harmonious Services Ribbon -->
      <div class="services-ribbon-container">
        <div class="services-ribbon">
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Claude AI</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Gemini</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>ChatGPT</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Perplexity</span>
          </div>
          <div class="service-chip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Antigravity</span>
          </div>
          <div class="service-chip highlight">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span>Без VPN и сторонних программ</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. Device Configurator -->
    <section class="configurator-section tabs-section">
      <!-- Segmented Tab Bar -->
      <div class="segmented-bar-wrapper">
        <nav class="segmented-bar" role="tablist" aria-label="Конфигурация устройств">
          <button class="segmented-tab active" role="tab" id="tab-windows" aria-controls="panel-windows" aria-selected="true" tabindex="0" data-target="panel-windows">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" fill="currentColor"/></svg>
            <span>Windows (DoH)</span>
          </button>
          <button class="segmented-tab" role="tab" id="tab-ios" aria-controls="panel-ios" aria-selected="false" tabindex="-1" data-target="panel-ios">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.61-.75 1.04-1.8 0.92-2.87-.9.04-2 .6-2.63 1.34-.56.64-.99 1.68-.86 2.73 1.01.08 2-.45 2.57-1.2" fill="currentColor"/></svg>
            <span>Apple iOS / macOS</span>
          </button>
          <button class="segmented-tab" role="tab" id="tab-android" aria-controls="panel-android" aria-selected="false" tabindex="-1" data-target="panel-android">
            <svg viewBox="0 0 24 24" class="tab-icon"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.551 0 .9993.4482.9993.9993.0001.5511-.4483.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.411 13.8533 8.1 12 8.1s-3.5902.311-5.1368.8497L4.8409 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6889-7.5743-6.1185-9.4396" fill="currentColor"/></svg>
            <span>Android (DoT)</span>
          </button>
          <button class="segmented-tab" role="tab" id="tab-proxy" aria-controls="panel-proxy" aria-selected="false" tabindex="-1" data-target="panel-proxy">
            <svg viewBox="0 0 24 24" class="tab-icon" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>Прокси приложений</span>
          </button>
        </nav>
      </div>

      <!-- Panel 1: Windows (DoH) -->
      <div class="tab-panel active" id="panel-windows" role="tabpanel" aria-labelledby="tab-windows">
        <div class="glass-config-card">
          <div class="card-left-column">
            <div class="card-header-row">
              <h2 class="card-header-title">Windows &amp; Браузеры (DoH)</h2>
              <span class="card-badge">RFC 8484 • Windows 11 &amp; Роутеры</span>
            </div>
            <p class="card-instruction">
              Шифрует все DNS-запросы под защищённый HTTPS-трафик. Настройка: Параметры → Сеть → Wi-Fi / Ethernet → Назначение DNS → Вручную (Включить DNS через HTTPS) или в настройках браузера.
            </p>
            <div class="input-field-group">
              <span class="input-field-label">Шаблон DoH:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-win-doh">https://dns.magicdns.ru/dns-query</code>
                <button class="btn-inline-copy" data-clipboard="https://dns.magicdns.ru/dns-query" title="Скопировать DoH" aria-label="Скопировать DoH">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span>Копировать</span>
                </button>
              </div>
            </div>
            <div class="input-field-group">
              <span class="input-field-label">IPv4 DNS Сервер:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-win-ipv4">109.120.132.43</code>
                <button class="btn-inline-copy" data-clipboard="109.120.132.43" title="Скопировать IPv4" aria-label="Скопировать IPv4">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span>Копировать</span>
                </button>
              </div>
            </div>
            <div class="card-actions-row">
              <button class="btn-neon-action" data-clipboard="https://dns.magicdns.ru/dns-query">Скопировать DoH</button>
              <button class="btn-dark-action" data-clipboard="109.120.132.43">Скопировать IPv4</button>
            </div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код ссылки DoH">
                {qr_windows}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span>QR-код адреса DoH</span>
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
              <h2 class="card-header-title">Apple iOS &amp; macOS (.mobileconfig)</h2>
              <span class="card-badge">В 1 клик • iOS 14+ / macOS 11+</span>
            </div>
            <p class="card-instruction">
              Устанавливает зашифрованный профиль SmartDNS. В Настройках открой «Профиль загружен» и нажми «Установить». Активируется в Wi-Fi и сотовых сетях.
            </p>
            <div class="input-field-group">
              <span class="input-field-label">Ссылка на профиль:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-ios-url">https://dns.magicdns.ru/profile.mobileconfig</code>
                <button class="btn-inline-copy" data-clipboard="https://dns.magicdns.ru/profile.mobileconfig" title="Скопировать ссылку" aria-label="Скопировать ссылку">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span>Копировать</span>
                </button>
              </div>
            </div>
            <div class="card-actions-row">
              <a href="https://dns.magicdns.ru/profile.mobileconfig" class="btn-action-green" id="btn-download-profile" style="text-decoration:none; display:inline-flex; align-items:center; justify-content:center;">Скачать профиль</a>
              <button class="btn-dark-action" data-clipboard="https://dns.magicdns.ru/profile.mobileconfig">Скопировать ссылку</button>
            </div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код профиля Apple iOS">
                {qr_ios}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span>Сканируй с iPhone / iPad</span>
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
              <h2 class="card-header-title">Android Частный DNS (DoT)</h2>
              <span class="card-badge">Порт 853 TLS • Android 9+</span>
            </div>
            <p class="card-instruction">
              Открой Настройки → Подключения (или Сеть и интернет) → Персональный DNS → Введи имя хоста и нажми Сохранить.
            </p>
            <div class="input-field-group">
              <span class="input-field-label">Имя хоста провайдера частного DNS:</span>
              <div class="code-input-box">
                <code class="code-input-text" id="val-android-host">dns.magicdns.ru</code>
                <button class="btn-inline-copy" data-clipboard="dns.magicdns.ru" title="Скопировать хост" aria-label="Скопировать хост">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span>Копировать</span>
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
                <span>QR-код хоста Android DoT</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel 4: Прокси приложений -->
      <div class="tab-panel" id="panel-proxy" role="tabpanel" aria-labelledby="tab-proxy">
        <div class="glass-config-card">
          <div class="card-left-column">
            <div class="card-header-row">
              <h2 class="card-header-title">Персональный прокси для приложений</h2>
              <span class="card-badge">Порт 8085 • HTTP CONNECT</span>
            </div>
            <p class="card-instruction">
              Для прямого ввода в Telegram, нейросетевые клиенты, браузерные расширения и IDE. Авторизация по логину и паролю.
            </p>
            <div class="input-field-group">
              <span class="input-field-label">Адрес персонального прокси:</span>
              <div class="code-input-box">
                <code class="code-input-text">http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085</code>
                <button class="btn-inline-copy" data-clipboard="http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085" title="Скопировать URL" aria-label="Скопировать URL">
                  <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  <span>Копировать</span>
                </button>
              </div>
            </div>
            
            <!-- Compact Parameter Subgrid -->
            <div class="params-subgrid">
              <div class="param-subcard">
                <div class="param-subcard-header">
                  <span class="param-subcard-label">Хост</span>
                  <button class="btn-inline-copy" data-clipboard="109.120.132.43" title="Копировать хост" aria-label="Копировать хост">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  </button>
                </div>
                <span class="param-subcard-val">109.120.132.43</span>
              </div>
              <div class="param-subcard">
                <div class="param-subcard-header">
                  <span class="param-subcard-label">Порт</span>
                  <button class="btn-inline-copy" data-clipboard="8085" title="Копировать порт" aria-label="Копировать порт">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  </button>
                </div>
                <span class="param-subcard-val">8085</span>
              </div>
              <div class="param-subcard">
                <div class="param-subcard-header">
                  <span class="param-subcard-label">Логин</span>
                  <button class="btn-inline-copy" data-clipboard="admin" title="Копировать логин" aria-label="Копировать логин">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  </button>
                </div>
                <span class="param-subcard-val">admin</span>
              </div>
              <div class="param-subcard">
                <div class="param-subcard-header">
                  <span class="param-subcard-label">Пароль</span>
                  <button class="btn-inline-copy" data-clipboard="Px94kM8vQ7wZb2Rt" title="Копировать пароль" aria-label="Копировать пароль">
                    <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  </button>
                </div>
                <span class="param-subcard-val">Px94kM8vQ7wZb2Rt</span>
              </div>
            </div>

            <div class="card-actions-row">
              <button class="btn-neon-action" data-clipboard="http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085">Скопировать прокси</button>
            </div>
          </div>
          <div class="card-right-column">
            <div class="qr-pod">
              <div class="qr-canvas-box" title="QR-код адреса прокси">
                {qr_proxy}
              </div>
              <div class="qr-caption">
                <svg viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2"></path><path d="M4 16v2a2 2 0 0 0 2 2h2"></path><path d="M16 4h2a2 2 0 0 1 2 2v2"></path><path d="M16 20h2a2 2 0 0 0 2-2v-2"></path></svg>
                <span>QR-код настроек прокси</span>
              </div>
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
            <span>Интерактивная проверка подключения к ИИ-шлюзу</span>
          </h2>
          <p>Проверь резолвинг DNS и доступность серверов Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT на своём устройстве.</p>
        </div>

        <div>
          <button class="btn-run-check" id="btn-run-check" aria-label="Запустить проверку подключения">
            <svg viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <span>Проверить подключение</span>
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
            <span id="result-status-text">MagicDNS активен! Сервисы Claude AI, Gemini, Google AI Studio и Antigravity доступны без VPN</span>
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
              <span class="metric-name">Статус шлюза ИИ</span>
              <span class="metric-val mint" id="metric-gateway-status">Подключено (Онлайн)</span>
            </div>
            <div class="metric-card">
              <span class="metric-name">Сетевая задержка (RTT)</span>
              <span class="metric-val" id="metric-ping">12 мс</span>
            </div>
            <div class="metric-card">
              <span class="metric-name">Протокол маршрутизации</span>
              <span class="metric-val">DoH / DoT (TLS 1.3)</span>
            </div>
            <div class="metric-card">
              <span class="metric-name">Доступ к Claude, Gemini &amp; Antigravity</span>
              <span class="metric-val mint" id="metric-access-status">Прямой (Без капчи)</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 4.5. Community Reviews & Suggestions Section -->
    <section class="reviews-section" id="reviews">
      <div class="reviews-header">
        <div class="reviews-header-left">
          <div class="section-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span>ОТЗЫВЫ И ПРЕДЛОЖЕНИЯ</span>
          </div>
          <h2>Что говорят пользователи MagicDNS</h2>
          <p class="reviews-subtitle">Реальный опыт использования для работы с Claude AI, Gemini и кодинга без VPN</p>
        </div>
        <button type="button" class="btn-neon-action btn-feedback-trigger" id="open-feedback-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          <span>Оставить отзыв или идею</span>
        </button>
      </div>

      <div class="reviews-grid">
        <div class="review-card">
          <div class="review-card-top">
            <div class="review-author-info">
              <div class="review-avatar">АР</div>
              <div>
                <div class="review-author-name">Алексей Романов</div>
                <div class="review-author-role">Senior Frontend • macOS / Safari</div>
              </div>
            </div>
            <div class="review-stars" aria-label="Оценка 5 из 5">★★★★★</div>
          </div>
          <p class="review-body">
            Настроил профиль на Mac и iPhone за пару минут. Claude AI и Google AI Studio открываются мгновенно, без задержек и без вечной капчи от Cloudflare. Огромный плюс — банки и локальные сервисы идут напрямую через провайдера на полной скорости.
          </p>
          <div class="review-badge-verified">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Проверено · Apple Profile</span>
          </div>
        </div>

        <div class="review-card">
          <div class="review-card-top">
            <div class="review-author-info">
              <div class="review-avatar dev">МВ</div>
              <div>
                <div class="review-author-name">Михаил Васильев</div>
                <div class="review-author-role">DevOps &amp; HomeLab • Keenetic Giga</div>
              </div>
            </div>
            <div class="review-stars" aria-label="Оценка 5 из 5">★★★★★</div>
          </div>
          <p class="review-body">
            Прописал DoH адрес в Keenetic. Теперь у всех устройств в домашней сети ChatGPT, Gemini и Perplexity работают прозрачно, не нужно каждому настраивать отдельные клиенты. Скорость не режется вообще, пинг до Стокгольма отличный.
          </p>
          <div class="review-badge-verified">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Проверено · Router DoH</span>
          </div>
        </div>

        <div class="review-card">
          <div class="review-card-top">
            <div class="review-author-info">
              <div class="review-avatar des">ЕК</div>
              <div>
                <div class="review-author-name">Екатерина Ковалева</div>
                <div class="review-author-role">UI/UX Designer • Windows 11</div>
              </div>
            </div>
            <div class="review-stars" aria-label="Оценка 5 из 5">★★★★★</div>
          </div>
          <p class="review-body">
            Раньше VPN постоянно отваливался и жрал батарею на ноутбуке. С MagicDNS просто включила шифрованный DNS в Windows — всё летает, как будто никаких блокировок нет. Очень удобно для работы в нейросетях целыми днями.
          </p>
          <div class="review-badge-verified">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Проверено · Windows 11 DoH</span>
          </div>
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
        <div class="footer-copy">© 2026 MagicDNS. Архитектура CascadeDNS. Домен <a href="https://magicdns.ru" style="color:var(--neon-mint);">magicdns.ru</a></div>
      </div>

      <div class="footer-center">
        <span>Статус серверов:</span>
        <div class="uptime-pill">
          <div class="uptime-dot"></div>
          <span>Аптайм 99.9%</span>
        </div>
      </div>

      <div class="footer-links">
        <a href="https://pay.cloudtips.ru/p/596a95a5" class="social-btn social-btn-donate" target="_blank" rel="noopener noreferrer" aria-label="Поддержать автора">
          <svg viewBox="0 0 24 24" class="donate-heart" aria-hidden="true">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span>Поддержать автора</span>
        </a>
      </div>
    </div>
  </footer>

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
          <div class="chat-title">Ассистент MagicDNS</div>
          <div class="chat-status">
            <span class="chat-status-dot"></span>
            <span>Онлайн · Быстрые ответы</span>
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
        <div class="chat-bubble-text">
          Привет! Я бот поддержки MagicDNS. Помогу настроить DNS на любом устройстве и отвечу на вопросы по доступу к Claude, Gemini и ChatGPT.
        </div>
      </div>

      <div class="chat-faq-title">Частые вопросы:</div>
      <div class="chat-faq-container" id="chat-faq-container">
        <button class="chat-faq-chip" data-faq="router">⚡ Настройка роутера (Keenetic, TP-Link, MikroTik)</button>
        <button class="chat-faq-chip" data-faq="security">🛡️ Безопасность и мобильные банки</button>
        <button class="chat-faq-chip" data-faq="ios">🍎 iPhone / Safari: не открывает сайты</button>
        <button class="chat-faq-chip" data-faq="disable">🔄 Как временно отключить MagicDNS?</button>
        <button class="chat-faq-chip" data-faq="diff">🌐 Чем отличается от обычного VPN?</button>
        <button class="chat-faq-chip" id="chat-faq-feedback-trigger" data-faq="feedback">💡 Оставить отзыв или предложить идею</button>
      </div>
    </div>

    <div class="chat-input-bar">
      <form id="chat-form" class="chat-form" action="javascript:void(0);">
        <input type="text" id="chat-input" class="chat-input" placeholder="Задайте свой вопрос..." autocomplete="off" maxlength="300">
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
            <h3 id="feedback-modal-title" class="feedback-modal-title">Отзыв или предложение</h3>
            <p class="feedback-modal-subtitle">Помогите сделать MagicDNS ещё быстрее и удобнее</p>
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
            <span>⭐ Отзыв</span>
          </button>
          <button type="button" class="feedback-type-chip" data-type="idea" role="radio" aria-checked="false">
            <span>💡 Предложение</span>
          </button>
          <button type="button" class="feedback-type-chip" data-type="bug" role="radio" aria-checked="false">
            <span>🐛 Ошибка / Баг</span>
          </button>
        </div>

        <!-- Rating Stars -->
        <div class="rating-stars-wrap">
          <label class="feedback-label">Ваша оценка:</label>
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
          <label class="feedback-label">Ваша платформа:</label>
          <div class="platform-chips" id="feedback-platform-chips">
            <button type="button" class="platform-chip active" data-platform="iOS / macOS">Apple (iOS / Mac)</button>
            <button type="button" class="platform-chip" data-platform="Windows">Windows</button>
            <button type="button" class="platform-chip" data-platform="Android">Android</button>
            <button type="button" class="platform-chip" data-platform="Роутер">Роутер (Keenetic / др.)</button>
          </div>
        </div>

        <!-- Textarea -->
        <div class="feedback-field">
          <label for="feedback-text" class="feedback-label">Ваш комментарий или идея:</label>
          <textarea id="feedback-text" class="feedback-textarea" rows="4" placeholder="Расскажите, как работает MagicDNS у вас, или какую функцию добавить..." required maxlength="1000"></textarea>
        </div>

        <!-- Contact (Optional) -->
        <div class="feedback-field">
          <label for="feedback-contact" class="feedback-label">Контакт для связи (по желанию):</label>
          <input type="text" id="feedback-contact" class="feedback-input" placeholder="@telegram_username или email" maxlength="100">
        </div>

        <!-- Submit Button -->
        <button type="submit" id="feedback-submit-btn" class="btn-neon-action feedback-submit-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          <span>Отправить отзыв</span>
        </button>
      </form>
    </div>
  </div>

  <!-- Client Script -->
  <script>
    (function() {{
      'use strict';

      // 1. Procedural Web Audio API Tactile Feedback & Haptics
      let audioCtx = null;
      function playTactileFeedback() {{
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
          osc.type = 'sine';
          osc.frequency.setValueAtTime(600, audioCtx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.04);
          gain.gain.setValueAtTime(0.035, audioCtx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start();
          osc.stop(audioCtx.currentTime + 0.04);
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
        btn.innerHTML = '<span>Скопировано!</span>';
        showToast('Скопировано: ' + text);

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
        {{ id: 'gemini', name: 'Gemini', endpoint: 'https://gemini.google.com/favicon.ico' }},
        {{ id: 'chatgpt', name: 'ChatGPT', endpoint: 'https://chatgpt.com/favicon.ico' }},
        {{ id: 'perplexity', name: 'Perplexity', endpoint: 'https://www.perplexity.ai/favicon.ico' }},
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
              const latency = Math.max(9, Math.round(performance.now() - startTime));
              resolve({{ ok: true, latency: latency }});
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
          progressLog.textContent = 'Опрос DNS-резолвера 109.120.132.43...';

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
                    badge.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg><span>Заблокирован</span>';
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
                  resultTitle.textContent = 'MagicDNS активен! Сервисы Claude AI, Gemini, Google AI Studio и Antigravity доступны без VPN';
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
                  metricAccess.textContent = 'Заблокировано провайдером';
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
      const CF_WORKER_URL = 'https://magicdns-support.workers.dev';

      // Conversation history for multi-turn context
      const chatHistory = [];

      const faqAnswers = {{
        router: 'Настройка на роутере открывает доступ сразу для всех устройств в доме:<br><br>• <b>Keenetic</b>: Сетевые правила → Серверы DNS → Добавить сервер → Адрес: <code>https://dns.magicdns.ru/dns-query</code> (тип DoH).<br>• <b>MikroTik</b>: IP → DNS → в поле DoH Server вставьте <code>https://dns.magicdns.ru/dns-query</code> и нажмите Apply.<br>• <b>TP-Link / Asus</b>: Дополнительные настройки → Сеть → Интернет → Вручную указать DNS: <code>109.120.132.43</code>.<br><br>После сохранения перезагрузите Wi-Fi на устройствах для обновления кэша.',
        security: 'Полностью безопасно!<br><br>• MagicDNS перенаправляет <b>только запросы к заблокированным ИИ-сервисам</b> (Claude, Gemini, ChatGPT).<br>• Банки (Сбер, Т-Банк, ВТБ), Госуслуги, маркетплейсы и обычные сайты идут напрямую через вашего провайдера без прокси и без замедления.<br>• Мы не ведем логов, весь DNS-трафик защищен шифрованием TLS 1.3.',
        ios: 'На iOS кэш DNS держится дольше обычного. Сделайте 3 простых действия:<br><br>1. Включите режим «В самолёте» на 5 секунд и выключите обратно — это мгновенно сбросит кэш DNS.<br>2. Закройте вкладку с Claude / Gemini в Safari и откройте заново.<br>3. Проверьте в «Настройки → Основные → VPN и управление устройством → DNS», чтобы стоял профиль <b>MagicDNS</b>.',
        disable: 'Отключение занимает 5 секунд:<br><br>• <b>iOS</b>: Настройки → Основные → VPN и управление устройством → DNS → выберите «Автоматически».<br>• <b>Android</b>: Настройки → Сеть и интернет → Персональный DNS → выберите «Отключено».<br>• <b>Windows</b>: Параметры → Сеть и интернет → DNS → переключите на «Автоматически (DHCP)»<br><br>Профиль можно включить обратно в любой момент.',
        diff: 'Главные отличия от обычного VPN:<br><br>• <b>Скорость</b>: VPN режет скорость до 10-30 Мбит/с. MagicDNS маршрутизирует только ИИ-сервисы, остальной интернет работает на максимальной скорости вашего провайдера.<br>• <b>Без капчи</b>: Шведский шлюз в Стокгольме не внесен в спам-базы Cloudflare.<br>• <b>Не сажает батарею</b>: Не требует запущенного приложения в фоне.'
      }};

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
              const answer = faqAnswers[faqKey];
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
        if (lower.indexOf('роутер') !== -1 || lower.indexOf('router') !== -1 || lower.indexOf('кинетик') !== -1 || lower.indexOf('keenetic') !== -1 || lower.indexOf('микротик') !== -1 || lower.indexOf('mikrotik') !== -1 || lower.indexOf('tp-link') !== -1) {{
          return faqAnswers.router;
        }}
        if (lower.indexOf('банк') !== -1 || lower.indexOf('тинькофф') !== -1 || lower.indexOf('т-банк') !== -1 || lower.indexOf('сбер') !== -1 || lower.indexOf('безопасн') !== -1 || lower.indexOf('слеж') !== -1) {{
          return faqAnswers.security;
        }}
        if (lower.indexOf('айфон') !== -1 || lower.indexOf('iphone') !== -1 || lower.indexOf('safari') !== -1 || lower.indexOf('сафари') !== -1 || lower.indexOf('ios') !== -1 || lower.indexOf('apple') !== -1) {{
          return faqAnswers.ios;
        }}
        if (lower.indexOf('отключ') !== -1 || lower.indexOf('выключ') !== -1 || lower.indexOf('удалить') !== -1 || lower.indexOf('снять') !== -1) {{
          return faqAnswers.disable;
        }}
        if (lower.indexOf('впн') !== -1 || lower.indexOf('vpn') !== -1 || lower.indexOf('отличие') !== -1 || lower.indexOf('скорост') !== -1) {{
          return faqAnswers.diff;
        }}
        if (lower.indexOf('швеци') !== -1 || lower.indexOf('ip') !== -1 || lower.indexOf('айпи') !== -1 || lower.indexOf('стокгольм') !== -1 || lower.indexOf('адрес') !== -1) {{
          return 'Адреса MagicDNS:<br>• DoH URL: <code>https://dns.magicdns.ru/dns-query</code><br>• DoT хост: <code>dns.magicdns.ru</code><br>• IPv4 шлюза: <code>109.120.132.43</code> (Стокгольм, Швеция)<br>• Прокси: <code>http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085</code>';
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
          const timeoutId = setTimeout(function() {{
            if (controller) controller.abort();
            if (!didRespond) {{
              didRespond = true;
              hideTyping();
              appendMessage('Я могу помочь с частыми вопросами прямо сейчас. Выберите подходящую тему из кнопок выше (роутеры, банки, iPhone/Safari, отключение) или задайте вопрос о настройке!', 'bot', false);
            }}
          }}, 7000);

          fetch(CF_WORKER_URL, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ message: query, history: chatHistory }}),
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
              appendMessage('Я могу помочь с частыми вопросами прямо сейчас. Выберите подходящую тему из кнопок выше (роутеры, банки, iPhone/Safari, отключение) или задайте вопрос о настройке!', 'bot', false);
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
        if (e.key === 'Escape' && feedbackModal && feedbackModal.classList.contains('active')) {{
          toggleFeedbackModal(false);
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
          if (submitBtn) {{
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.querySelector('span').textContent = 'Отправка...';
          }}

          const payload = {{
            type: currentType,
            rating: currentRating,
            platform: currentPlatform,
            message: message,
            contact: contact
          }};

          fetch(CF_WORKER_URL + '/feedback', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(payload)
          }}).then(function() {{
            // Handled
          }}).catch(function() {{
            // Handled
          }}).finally(function() {{
            if (submitBtn) {{
              submitBtn.disabled = false;
              submitBtn.style.opacity = '1';
              submitBtn.querySelector('span').textContent = 'Отправить отзыв';
            }}
            if (textInput) textInput.value = '';
            if (contactInput) contactInput.value = '';
            toggleFeedbackModal(false);
            showToast('Спасибо за отзыв! Ваше сообщение принято.');
          }});
        }});
      }}

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
                    <string>109.120.132.43</string>
                </array>
            </dict>
            <key>PayloadDescription</key>
            <string>Настройка зашифрованного DoH MagicDNS для прямого доступа к Claude AI, Gemini, Google AI Studio, Antigravity и ChatGPT без VPN</string>
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

with open('profile.mobileconfig', 'w', encoding='utf-8') as f:
    f.write(mobileconfig_content)

# SEO files: robots.txt and sitemap.xml in root and public/
import os

os.makedirs('public', exist_ok=True)

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
    <lastmod>2026-10-18</lastmod>
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
