/**
 * MagicDNS Support Bot — Cloudflare Workers AI
 * 
 * Powered natively by Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct-fast).
 * 10,000 Neurons/day free.
 * ZERO API keys required — no external services or secrets!
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

      // Run Cloudflare Workers AI natively (no API keys required!)
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
