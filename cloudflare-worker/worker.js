/**
 * MagicDNS 24/7 Smart Support Bot & Feedback Gateway — Cloudflare Workers AI
 * 
 * - Model: Meta Llama 3.3 70B Instruct (FP8 Fast) with auto-fallback to Llama 3.1 8B.
 * - Dialogue Engine: Dynamic context-aware tech support engineer.
 * - Feedback Gateway: Secure review/bug/wishlist moderation pipeline into Telegram.
 * 
 * 100% Free on Cloudflare Workers AI (10,000 daily neurons free tier).
 */

const SYSTEM_INSTRUCTION = `Ты — живой, технически грамотный и вежливый инженер поддержки сервиса MagicDNS (сайт: magicdns.ru).
Твоя цель — реально вникнуть в ситуацию пользователя и помочь ему настроить доступ или решить проблему, а не отделываться шаблонными копипастами.

КЛЮЧЕВЫЕ ПРИНЦИПЫ ОБЩЕНИЯ (СТРОГО):
1. ВНИМАТЕЛЬНО СЛЕДИ ЗА КОНТЕКСТОМ ДИАЛОГА. Читай предыдущие сообщения. Если пользователь спорит, переспрашивает («а почему?», «а на роутере?», «а если наоборот?») — отвечай логично и последовательно, опираясь на то, о чем уже шла речь. Никогда не противоречь своим прошлым словам.
2. ДИАГНОСТИРУЙ, А НЕ СПАМЬ. Если человек пишет «не работает» или «ошибка» — не вываливай всю инструкцию заново. Назови 1-2 самые вероятные причины (сброс кэша DNS через авиарежим/перезагрузку Wi-Fi, опечатка в IP, блокировка провайдером) или задай один короткий уточняющий вопрос.
3. ЧЕЛОВЕЧЕСКИЙ ТОН. Пиши простым языком, емко и по делу. Без навязчивого спискобесия, без роботизированных приветствий («Конечно! Рад помочь!») и без канцелярщины. Отвечай на чистом русском языке без иностранных слов-паразитов.
4. ЯЗЫК: Отвечай на языке пользователя (русский, английский и др.).

ЗНАНИЯ О СЕРВИСЕ MAGICDNS:
- Что это: Умный SmartDNS-шлюз для доступа к зарубежным нейросетям (ChatGPT, Claude AI, Gemini, Google AI Studio, Midjourney, Canva, Antigravity) без VPN.
- Цена: Сервис 100% бесплатный. Никаких платных подписок или скрытых тарифов, проект живет на добровольные донаты сообщества (CloudTips).
- Законность и РКН: Сервис работает строго по закону РФ. Он перенаправляет запросы исключительно к зарубежным ИИ, которые сами ограничили доступ пользователям из РФ. Сервис НЕ используется и не предназначен для открытия сайтов, запрещенных в РФ.
- Безопасность и банки: Трафик к Сбербанку, Т-Банку, Госуслугам, маркетплейсам и обычным сайтам НЕ идет через шлюз — он резолвится напрямую провайдером без задержек. Логи не ведутся.

АКТУАЛЬНЫЕ НАСТРОЙКИ (СЕРВЕРЫ В ГЕРМАНИИ И ФИНЛЯНДИИ):
- DoH (DNS-over-HTTPS, скрытый стелс-эндпоинт): https://api.magicdns.ru/sync
  (Также поддерживается стандартный путь: https://api.magicdns.ru/dns-query)
- DoT (DNS-over-TLS, для Android): api.magicdns.ru
- Обычный IPv4 DNS (для Windows, ТВ и роутеров):
  * Основной (Primary): 109.120.177.170 (Франкфурт, Германия)
  * Резервный (Secondary): 94.249.177.102 (Финляндия / Германия)
- Профиль iOS / macOS: https://magicdns.ru/profile.mobileconfig

ТИПОВЫЕ РЕШЕНИЯ ПРОБЛЕМ:
- iOS / Safari: Чаще всего дело в старом кэше DNS. Решение: включить авиарежим на 5 секунд и выключить, либо закрыть Safari из многозадачности. Проверить в «Настройки -> Основные -> VPN и управление устройством -> DNS», что выбран MagicDNS.
- Android: «Настройки -> Сеть и интернет -> Персональный DNS-сервер» -> вбить: api.magicdns.ru. Если пишет «нет подключения» — провайдер фильтрует порт 853, тогда лучше настроить DoH в браузере Chrome/Яндекс.
- Windows 10/11: В свойствах сетевого адаптера IPv4 прописать Основной: 109.120.177.170, Резервный: 94.249.177.102. Если нужен DoH в браузере: Настройки браузера -> Безопасность -> Использовать безопасный DNS -> Свой -> https://api.magicdns.ru/sync.
- Роутеры (Keenetic, TP-Link, MikroTik, Asus): В настройках WAN/DHCP прописать Основной: 109.120.177.170, Резервный: 94.249.177.102. Перезагрузить роутер или переподключить Wi-Fi.
- Как отключить: на iOS переключить DNS на «Автоматически», на Android выключить «Персональный DNS», на Windows вернуть получение DNS по DHCP.

КОНФЛИКТЫ СО СТОРОННИМИ АНЛОКЕРАМИ, ZAPRET, GOODBYEDPI, ПРОКСИ И VPN:
Если у пользователя раньше стояли другие утилиты для обхода или расширения, они часто ломают сетевые настройки Windows. Алгоритм первой помощи:
1. Очистка файла hosts: Нажать Win + R -> ввести notepad C:\\Windows\\System32\\drivers\\etc\\hosts (запустить от имени Администратора). Удалить любые строки с адресами openai, chatgpt, claude, cloudflare, anthropic. Сохранить файл.
2. Отключение системного прокси: Нажать Win + R -> ввести inetcpl.cpl -> вкладка «Подключения» -> «Настройка сети» -> снять галочку «Использовать прокси-сервер». В Параметрах Windows: «Сеть и Интернет» -> «Прокси-сервер» -> отключить ручной прокси и автоматические сценарии (PAC-скрипты).
3. Сброс кэша DNS: В командной строке выполнить команду: ipconfig /flushdns
4. Браузер: Отключить старые прокси-расширения и VPN-плагины, которые перехватывают трафик.`;

function escapeTgHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

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

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    const url = new URL(request.url);

    // 2. Handle Feedback / Review / Bug report endpoint
    if (url.pathname === '/feedback') {
      try {
        const body = await request.json();
        const type = body.type || 'feedback';
        const message = (body.message || '').trim();
        const author = (body.author || '').trim();
        const contact = (body.contact || '').trim();
        const rating = parseInt(body.rating, 10) || 5;
        const platform = body.platform || 'Не указана';

        if (env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID) {
          let tgText = '';

          if (type === 'review') {
            const stars = '⭐'.repeat(Math.min(5, Math.max(1, rating)));
            tgText = `🌟 <b>НОВЫЙ ОТЗЫВ С САЙТА!</b>\n\n` +
              `👤 <b>Автор:</b> ${escapeTgHtml(author || 'Аноним')}\n` +
              `⭐ <b>Оценка:</b> ${stars} (${rating}/5)\n` +
              `💻 <b>Платформа:</b> ${escapeTgHtml(platform)}\n` +
              `📱 <b>Контакт:</b> ${contact ? `<code>${escapeTgHtml(contact)}</code>` : 'Не указан'}\n\n` +
              `💬 <b>Текст:</b>\n${escapeTgHtml(message)}`;
          } else if (type === 'bug') {
            tgText = `🐞 <b>СООБЩЕНИЕ ОБ ОШИБКЕ С САЙТА!</b> #БАГ\n\n` +
              `💻 <b>Платформа:</b> ${escapeTgHtml(platform)}\n` +
              `👤 <b>Контакт:</b> ${contact ? `<code>${escapeTgHtml(contact)}</code>` : 'Анонимно'}\n\n` +
              `💬 <b>Описание проблемы:</b>\n${escapeTgHtml(message)}`;
          } else if (type === 'idea') {
            tgText = `💡 <b>НОВОЕ ПРЕДЛОЖЕНИЕ С САЙТА!</b> #ИДЕЯ\n\n` +
              `💻 <b>Платформа:</b> ${escapeTgHtml(platform)}\n` +
              `👤 <b>Контакт:</b> ${contact ? `<code>${escapeTgHtml(contact)}</code>` : 'Анонимно'}\n\n` +
              `💬 <b>Суть идеи:</b>\n${escapeTgHtml(message)}`;
          } else if (type === 'wishlist') {
            const serviceTitle = body.service_title || 'Новый сервис';
            const category = body.category || 'Игра / Сервис';
            const domain = body.domain || 'Не указан';
            tgText = `💡 <b>НОВАЯ ЗАЯВКА В ВИШЛИСТ С САЙТА! #ВИШЛИСТ</b>\n\n` +
              `🎮 <b>Сервис / Игра:</b> ${escapeTgHtml(serviceTitle)}\n` +
              `📁 <b>Категория:</b> ${escapeTgHtml(category)}\n` +
              `🌐 <b>Домен:</b> <code>${escapeTgHtml(domain)}</code>\n` +
              `👤 <b>Контакт:</b> ${contact ? `<code>${escapeTgHtml(contact)}</code>` : 'Анонимно'}\n\n` +
              `💬 <b>Описание проблемы:</b>\n${escapeTgHtml(message)}\n\n` +
              `🛡️ <i>Требуется проверка на РКН (149-ФЗ) и модерация перед публикацией для голосования.</i>`;
          } else {
            tgText = `🔔 <b>Новое сообщение с MagicDNS!</b>\n\n💬 ${escapeTgHtml(message)}`;
          }

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

    // 3. Handle Intelligent AI Chat
    try {
      const body = await request.json();
      const userMessage = (body.message || '').trim();

      if (!userMessage) {
        return new Response(JSON.stringify({ error: 'Empty message' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      // Build conversation messages for Workers AI
      const messages = [
        { role: 'system', content: SYSTEM_INSTRUCTION }
      ];

      // Keep up to 8 conversation history turns for strong multi-turn reasoning
      if (Array.isArray(body.history)) {
        for (const item of body.history.slice(-8)) {
          if (item.role && item.text) {
            messages.push({
              role: item.role === 'user' ? 'user' : 'assistant',
              content: item.text,
            });
          }
        }
      }

      messages.push({ role: 'user', content: userMessage });

      // Run Cloudflare Workers AI: Llama 3.3 70B (Primary) -> Llama 3.1 8B (Fallback)
      let aiResponse;
      try {
        aiResponse = await env.AI.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
          messages: messages,
          max_tokens: 600,
          temperature: 0.6,
          top_p: 0.9,
        });
      } catch (err70B) {
        console.warn('Fallback to 8B due to:', err70B);
        aiResponse = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
          messages: messages,
          max_tokens: 500,
          temperature: 0.6,
          top_p: 0.9,
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
