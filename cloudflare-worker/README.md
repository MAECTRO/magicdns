# MagicDNS Support Bot — Cloudflare Worker

Бесплатный serverless-бэкенд для чата поддержки `magicdns.ru`. Работает на Cloudflare Workers (100 000 бесплатных запросов каждый день) и пересылает вопросы пользователей в Google Gemini Flash API с системной базой знаний о MagicDNS.

---

## Быстрый деплой за 2 минуты (через браузер)

1. Открой [Cloudflare Dashboard](https://dash.cloudflare.com/) и перейди в **Workers & Pages** → **Create application** → **Create Worker**.
2. Укажи имя воркера (например, `magicdns-support`) и нажми **Deploy**.
3. Нажми **Edit code**, удали шаблонный код и вставь весь код из файла [`worker.js`](worker.js).
4. Нажми **Deploy** (в правом верхнем углу).
5. Перейди во вкладку **Settings** воркера → **Variables and Secrets** → **Add**:
   - Имя переменной: `GEMINI_API_KEY`
   - Тип: **Secret**
   - Значение: твой бесплатный ключ из [Google AI Studio](https://aistudio.google.com/)
   - Нажми **Save and deploy**.
6. Скопируй адрес воркера (например, `https://magicdns-support.твой-аккаунт.workers.dev`).
7. В файле `build_page.py` в константе `CF_WORKER_URL` укажи этот адрес и запусти `python build_page.py`.

---

## Деплой через Wrangler CLI (по желанию)

```bash
cd cloudflare-worker
npx wrangler login
npx wrangler secret put GEMINI_API_KEY
npx wrangler deploy
```
