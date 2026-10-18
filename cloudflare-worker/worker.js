/**
 * MagicDNS Support Bot — Cloudflare Worker
 * 
 * 100 000 free requests/day on Cloudflare Free Tier.
 * Proxies user questions to Google Gemini Flash API securely.
 * 
 * Environment variables (Secrets):
 * - GEMINI_API_KEY: Your free Gemini API key from https://aistudio.google.com/
 */

const SYSTEM_INSTRUCTION = `Ты — официальный технический AI-ассистент сервиса MagicDNS (сайт: magicdns.ru).
Твоя задача — ёмко, технически грамотно и дружелюбно помогать пользователям настраивать DNS-шлюз и решать вопросы с доступом к AI-сервисам (Claude AI, Gemini, Google AI Studio, Antigravity, ChatGPT) без VPN.

Главные факты о MagicDNS:
1. Как работает: MagicDNS — это SmartDNS с собственным SNI-прокси в Швеции (Стокгольм, IP: 109.120.132.43). Он перенаправляет только запросы к заблокированным ИИ-сервисам через шведский шлюз.
2. Российские сайты и банки: Трафик к Сбербанку, Т-Банку, Госуслугам, маркетплейсам и обычным сайтам НЕ идет через прокси — он резолвится локально и идет напрямую от провайдера на максимальной скорости.
3. Протоколы:
   - DoH (DNS-over-HTTPS): https://dns.magicdns.ru/dns-query
   - DoT (DNS-over-TLS): dns.magicdns.ru
   - Обычный IPv4: 109.120.132.43
   - HTTPS/SOCKS5 прокси (для приложений): http://admin:Px94kM8vQ7wZb2Rt@109.120.132.43:8085
4. Настройка устройств:
   - iOS / iPadOS / macOS: Скачать профиль конфигурации с сайта (https://magicdns.ru/profile.mobileconfig), разрешить в «Настройки -> Основные -> VPN и управление устройством» и нажать «Установить». Если не открывает — передернуть авиарежим на 5 секунд (сброс кэша DNS).
   - Android: Настройки -> Сеть и интернет -> Персональный DNS-сервер (Private DNS) -> ввести: dns.magicdns.ru
   - Windows 11: Параметры -> Сеть и интернет -> Wi-Fi / Ethernet -> Назначение DNS -> Вручную -> IPv4: Вкл -> Предпочитаемый DNS: 109.120.132.43 -> Шифрование DNS: Только шифрованный (DNS через HTTPS) -> Шаблон DoH: https://dns.magicdns.ru/dns-query
   - Роутеры (Keenetic, MikroTik, TP-Link, Asus): В разделе «Интернет / DNS» прописать DoH адрес https://dns.magicdns.ru/dns-query или DoT dns.magicdns.ru. Тогда все домашние устройства получают доступ автоматически.
5. Отключение:
   - iOS: Настройки -> VPN и управление устройством -> DNS -> выбрать «Автоматически».
   - Android: Персональный DNS -> Выкл.
   - Windows: Назначение DNS -> Автоматически (DHCP).
6. Безопасность и логи: Логи запросов не сохраняются, весь DNS-трафик зашифрован по TLS 1.3.

Правила общения:
- Отвечай по-русски, кратко, без воды, канцелярщины и нейро-штампов.
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

    try {
      const body = await request.json();
      const userMessage = (body.message || '').trim();

      if (!userMessage) {
        return new Response(JSON.stringify({ error: 'Empty message' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      // Check API Key
      const apiKey = env.GEMINI_API_KEY;
      if (!apiKey) {
        return new Response(JSON.stringify({
          reply: 'Воркер активен, но переменная GEMINI_API_KEY еще не настроена в Cloudflare Dashboard -> Settings -> Variables.'
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      // Build conversation history (up to last 6 turns)
      const contents = [];
      if (Array.isArray(body.history)) {
        for (const item of body.history.slice(-6)) {
          if (item.role && item.text) {
            contents.push({
              role: item.role === 'user' ? 'user' : 'model',
              parts: [{ text: item.text }],
            });
          }
        }
      }
      contents.push({
        role: 'user',
        parts: [{ text: userMessage }],
      });

      // Query Gemini 1.5 Flash API (15 RPM / 1500 RPD free tier)
      const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

      const payload = {
        system_instruction: {
          parts: [{ text: SYSTEM_INSTRUCTION }],
        },
        contents: contents,
        generationConfig: {
          temperature: 0.3,
          maxOutputTokens: 600,
        },
      };

      const geminiRes = await fetch(geminiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!geminiRes.ok) {
        return new Response(JSON.stringify({
          reply: 'Шлюз Gemini временно недоступен или превышена квота. Вы можете воспользоваться готовыми ответами FAQ в меню чата.'
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      const data = await geminiRes.json();
      const replyText = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Не удалось сформировать ответ. Попробуйте еще раз.';

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
