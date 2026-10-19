/**
 * MagicDNS Support Bot & Feedback Gateway — Cloudflare Workers AI
 * 
 * - Chat: Powered natively by Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct-fast).
 * - Feedback: Handles user reviews, suggestions & bug reports.
 *   Optionally relays to Telegram if TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID are set.
 * 
 * 10,000 Neurons/day free.
 * ZERO API keys required for LLM inference!
 */

const SYSTEM_INSTRUCTION = `Ты — официальный технический AI-ассистент сервиса MagicDNS (сайт: magicdns.ru).
Твоя задача — ёмко, технически грамотно и дружелюбно помогать пользователям настраивать DNS-шлюз и решать вопросы с доступом к AI-сервисам (Claude AI, Gemini, Google AI Studio, Antigravity, ChatGPT) без VPN.

Главные факты о MagicDNS:
1. Как работает: MagicDNS — это двухшлюзовый SmartDNS с SNI-прокси (IP: 109.120.132.43 и 94.249.177.102). Они работают параллельно с балансировкой и отказоустойчивостью. Шлюз перенаправляет только запросы к заблокированным ИИ-сервисам через европейские узлы.
2. Российские сайты и банки: Трафик к Сбербанку, Т-Банку, Госуслугам, маркетплейсам и обычным сайтам НЕ идет через прокси — он резолвится локально и идет напрямую от провайдера на максимальной скорости.
3. Протоколы и адреса:
   - DoH (DNS-over-HTTPS): https://dns.magicdns.ru/dns-query (или https://de.magicdns.ru/dns-query)
   - DoT (DNS-over-TLS): dns.magicdns.ru (или de.magicdns.ru)
   - Обычный IPv4 DNS (для роутеров и ПК без DoH/DoT):
     * Основной DNS: 109.120.132.43
     * Резервный DNS: 94.249.177.102
   - Профиль iOS / macOS (.mobileconfig): https://dns.magicdns.ru/profile.mobileconfig (или https://de.magicdns.ru/api/profile.mobileconfig)
   - Персональный HTTP/SOCKS5 прокси (порт 8085):
     * 109.120.132.43: http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085
     * 94.249.177.102: http://admin:Px94kM8vQ7wZb2Rt@94.249.177.102:8085
4. Настройка устройств:
   - iOS / iPadOS / macOS: Скачать профиль с сайта (https://dns.magicdns.ru/profile.mobileconfig), разрешить в «Настройки -> Основные -> VPN и управление устройством» и нажать «Установить». Если не открывает — передернуть авиарежим на 5 секунд (сброс кэша DNS).
   - Android: Настройки -> Сеть и интернет -> Персональный DNS-сервер (Private DNS) -> ввести: dns.magicdns.ru (или de.magicdns.ru).
   - Windows 11: Параметры -> Сеть и интернет -> Wi-Fi / Ethernet -> Назначение DNS -> Вручную -> IPv4: Вкл -> Предпочитаемый DNS: 109.120.132.43 (или 94.249.177.102) -> Шифрование DNS: Только шифрованный (DNS через HTTPS) -> Шаблон DoH: https://dns.magicdns.ru/dns-query
   - Роутеры без DoH (Keenetic, TP-Link, D-Link, Asus, MikroTik, Tenda, Zyxel): В веб-интерфейсе роутера в настройках WAN/DHCP прописать Основной DNS: 109.120.132.43, Резервный DNS: 94.249.177.102. Все устройства в домашней сети Wi-Fi автоматически получат доступ к ИИ.
5. Отключение:
   - iOS: Настройки -> VPN и управление устройством -> DNS -> выбрать «Автоматически».
   - Android: Персональный DNS -> Выкл.
   - Windows: Назначение DNS -> Автоматически (DHCP).
6. Безопасность и логи: Логи запросов не сохраняются, весь DNS-трафик зашифрован по TLS 1.3.

Правила общения:
- Отвечай на том же языке, на котором пишет пользователь (русский, английский, китайский или турецкий), кратко, без воды, канцелярщины и нейро-штампов.
- Сразу давай конкретные адреса и шаги.
- Если вопрос не относится к MagicDNS, сети, DNS или AI-сервисам, вежливо верни разговор к теме MagicDNS.`;

export default {
  async fetch(request, env, ctx) {
    // 1. Handle CORS Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // 2. Only allow POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }

    const url = new URL(request.url);

    // 3. Handle Feedback & Review Submissions
    if (url.pathname === '/feedback') {
      try {
        const body = await request.json();
        const typeNames = { review: '⭐ Отзыв', idea: '💡 Предложение', bug: '🐛 Ошибка / Баг' };
        const typeTitle = typeNames[body.type] || body.type || 'Отзыв';
        const ratingStars = '⭐'.repeat(Math.max(1, Math.min(5, Number(body.rating) || 5)));

        // If Telegram bot is configured, relay notification
        if (env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID) {
          const tgText = `🔔 <b>Новое сообщение с MagicDNS!</b>\n\n` +
            `<b>Категория:</b> ${typeTitle}\n` +
            `<b>Оценка:</b> ${ratingStars}\n` +
            `<b>Платформа:</b> ${body.platform || 'Не указана'}\n` +
            `<b>Контакт:</b> ${body.contact || 'Анонимно'}\n\n` +
            `<b>Текст:</b>\n${body.message || '—'}`;

          await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: env.TELEGRAM_CHAT_ID,
              text: tgText,
              parse_mode: 'HTML',
            }),
          }).catch(() => {});
        }

        return new Response(JSON.stringify({ ok: true, message: 'Отзыв успешно принят' }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message || 'Error processing feedback' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
    }

    // 4. Handle Chat AI Questions (Default Endpoint)
    try {
      const body = await request.json();
      const userMessage = (body.message || '').trim();

      if (!userMessage) {
        return new Response(JSON.stringify({ error: 'Empty message' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      // Build conversation messages for Cloudflare Workers AI
      const messages = [
        { role: 'system', content: SYSTEM_INSTRUCTION }
      ];

      if (Array.isArray(body.history)) {
        for (const item of body.history.slice(-6)) {
          if (item.role && item.text) {
            messages.push({
              role: item.role === 'user' ? 'user' : 'assistant',
              content: item.text,
            });
          }
        }
      }

      messages.push({ role: 'user', content: userMessage });

      // Run Cloudflare Workers AI natively
      let aiResponse;
      try {
        aiResponse = await env.AI.run('@cf/meta/llama-3.1-8b-instruct-fast', {
          messages: messages,
          max_tokens: 500,
          temperature: 0.3,
        });
      } catch (errFast) {
        aiResponse = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
          messages: messages,
          max_tokens: 500,
          temperature: 0.3,
        });
      }

      const replyText = aiResponse?.response || 'Не удалось сформировать ответ. Попробуйте еще раз.';

      return new Response(JSON.stringify({ reply: replyText }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message || 'Internal server error' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }
  },
};
