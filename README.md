# MagicDNS — Высокоскоростной Smart DNS для ИИ и нейросетей

<p align="center">
  <a href="https://magicdns.ru/"><img src="https://magicdns.ru/og-image.png" alt="MagicDNS Banner" width="700"/></a>
</p>

<p align="center">
  <a href="https://magicdns.ru/"><img src="https://img.shields.io/badge/Official_Site-magicdns.ru-6366f1?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Official Website"/></a>
  <img src="https://img.shields.io/badge/Status-Online_%7C_25--35ms-10b981?style=for-the-badge" alt="Status Online"/>
  <img src="https://img.shields.io/badge/Protocols-DoH_%7C_DoT_%7C_IPv4-06b6d4?style=for-the-badge" alt="Protocols"/>
  <img src="https://img.shields.io/badge/Zero--Logs-Strict-8b5cf6?style=for-the-badge" alt="Zero Logs"/>
</p>

> **MagicDNS** — публичный защищенный Smart DNS-шлюз для устранения региональных ограничений и стабильного прямого доступа к зарубежным нейросетям (**Google Gemini**, **Google AI Studio**, **ChatGPT / OpenAI**, **Claude / Anthropic**, **Perplexity**, **Midjourney**) без использования VPN, без падения скорости и без потери доступа к российским сервисам (банки, Госуслуги).

---

## 🌐 Официальный веб-сайт и чекер

Веб-интерфейс с автодиагностикой сети, генератором профилей и интерактивным чекером доступности:  
👉 **[https://magicdns.ru](https://magicdns.ru)**

---

## ⚡ Ключевые преимущества перед VPN

| Параметр | Обычный VPN | MagicDNS (Smart DNS) |
| :--- | :--- | :--- |
| **Реальная скорость** | Падение на 40–80% из-за шифрования | **100% скорости вашего тарифа** |
| **Пинг в API / чатах** | 120–300 ms (сервер-посредник) | **25–35 ms** (напрямую) |
| **Батарея смартфона** | Быстрый разряд фоновым процессом | **0% расхода аккумулятора** (нативно в ОС) |
| **Банки и Госуслуги** | Блокируют зарубежные IP | **Работают стабильно** (трафик РФ идёт напрямую) |
| **Установка софта** | Требуются сторонние клиенты | **Встроенные системные настройки** |

---

## 📋 Сетевые параметры для подключения

| Параметр | Значение | Описание |
| :--- | :--- | :--- |
| **Основной IPv4** | `109.120.132.43` | Для роутеров, Windows, Linux, консолей |
| **Резервный IPv4** | `94.249.177.102` | Запасной шлюз высокой доступности |
| **DoH (DNS-over-HTTPS)** | `https://magicdns.ru` | Браузеры, Windows 11, iOS, Keenetic, OpenWrt |
| **DoT (Персональный DNS)** | `dns.magicdns.ru` | Android («Персональный DNS-сервер») |
| **iOS Профиль** | [Скачать .mobileconfig](https://magicdns.ru/profile.mobileconfig) | Официальный профиль конфигурации Apple |

---

## 🚀 Быстрая настройка по платформам

### 1. Android (Смартфоны и планшеты)
1. Откройте **Настройки** → **Подключения** (или **Сеть и интернет**).
2. Найдите пункт **Персональный DNS-сервер** (Private DNS).
3. Выберите **Имя хоста поставщика персонального DNS** и введите:
   ```text
   dns.magicdns.ru
   ```
4. Нажмите **Сохранить**. Готово!

---

### 2. iOS / iPhone / iPad / macOS
1. Откройте Safari и скачайте официальный профиль:  
   👉 **[https://magicdns.ru/profile.mobileconfig](https://magicdns.ru/profile.mobileconfig)**
2. Перейдите в **Настройки** → **Профиль загружен** (или **Основные** → **VPN и управление устройством**).
3. Нажмите **Установить** и подтвердите ввод код-пароля.

---

### 3. Windows 11 / 10
1. Откройте **Параметры** → **Сеть и Интернет** → выберите ваше подключение (**Wi-Fi** или **Ethernet**).
2. В строке **Назначение DNS-сервера** нажмите **Изменить** → переключите на **Вручную** (IPv4).
3. Введите:
   - **Предпочтительный DNS**: `109.120.132.43`
   - **Шифрование DNS**: *Только через HTTPS (DoH)* → шаблон: `https://magicdns.ru`
   - **Дополнительный DNS**: `94.249.177.102`

---

### 4. Роутеры (Keenetic, OpenWrt, MikroTik, ASUS)
Настроив DNS на роутере, вы автоматически обеспечите доступ к нейросетям для всех домашних устройств (ПК, телефоны, Smart TV, консоли):
- **Основной DNS**: `109.120.132.43`
- **Дополнительный DNS**: `94.249.177.102`
- В Keenetic для работы по протоколу DoH добавьте адрес: `https://magicdns.ru`

---

### 5. Для разработчиков (Linux / Python / Curl)
Настройка `systemd-resolved` в `/etc/systemd/resolved.conf`:
```ini
[Resolve]
DNS=109.120.132.43 94.249.177.102
FallbackDNS=1.1.1.1 8.8.8.8
DNSOverTLS=yes
DNSOverHTTPS=https://magicdns.ru
```

---

## 🎯 Поддерживаемые нейросети и платформы

- **Google Gemini & Google AI Studio** — устранение ошибки *"Gemini is not available in your country"*.
- **ChatGPT & OpenAI API** — устранение геолокационных сбоев авторизации и сессий.
- **Claude (Anthropic)** — доступ к веб-чату и API без задержек.
- **Perplexity AI** — мгновенный поиск и генерация ответов.
- **Midjourney** — стабильная работа интерфейса и веб-галереи.
- **Microsoft Copilot** — прямой коннект без посредников.

---

## 🔒 Конфиденциальность и Zero-Logs

- Сервис работает строго по принципу **Zero-Logs**: история DNS-запросов, логи посещений и IP-адреса пользователей не сохраняются.
- MagicDNS обрабатывает исключительно DNS-резолв и не имеет доступа к вашему трафику, паролям или сессионным данным.

---

## 📄 Лицензия и обратная связь

- Проект распространяется по лицензии [MIT](LICENSE).
- Обратная связь и техническая поддержка: [support@magicdns.ru](mailto:support@magicdns.ru)
- Официальный сайт: **[magicdns.ru](https://magicdns.ru)**
