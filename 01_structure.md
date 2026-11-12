# АРХИТЕКТУРА И СПЕЦИФИКАЦИЯ ПРОЕКТА: CYBERGLOW

> **Проект:** CyberGlow — Студия дизайнерских LED-неоновых вывесок  
> **Клиент / Заказчик:** CyberGlow Neon Studio (Москва / Токио)  
> **Чек проекта:** 280,000 ₽ | **Срок:** 14 дней (Дедлайн: 2026-11-25)  
> **Дедлайн MVP (80%):** 2026-11-22  
> **Тип договора:** Договор СМЗ с ИП (Чек «Мой Налог»)

---

## 🛠 Технологический стек
- **Frontend / UI:** HTML5 / CSS3 / JavaScript (Vanilla SPA), Tokyo Midnight Dark Aesthetic, CSS Multi-layer Glow Engine, Canvas Wall Textures
- **Backend & Logic:** Python 3.12, FastAPI, Uvicorn, SQLite3, Pydantic v2
- **Telegram Bot:** Aiogram 3.x (Asyncio, FSM, Inline Keyboards, Photo Intake)
- **Уведомления и лиды:** Автоматическая отправка структурированных заявок в @Idrisov_prod

---

## 🏛 Архитектурная схема
```
[ Клиент в Браузере ] ──► [ Интерактивный Ne-on Конструктор ] ──► [ REST API /api/quote ] ──┐
                                                                                           ▼
[ Пользователь в Telegram ] ──► [ Aiogram 3.x Бот (@CyberGlowBot) ] ─────────────────► [ SQLite DB ]
                                                                                           │
                                                                                           ▼
                                                                                 [ Алерты @Idrisov_prod ]
```

---

## 🔐 Переменные окружения (.env.example)
```env
BOT_TOKEN=8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc
TELEGRAM_OWNER_ID=1387913438
TELEGRAM_OWNER_USERNAME=@Idrisov_prod
PORT=3011
API_PORT=8011
PROXY_URL=socks5://dsZwtR:PTJNnz@72.57.96.136:8000
DATABASE_PATH=cyberglow.db
```

---

## 🔗 Ресурсы и ссылки
- **Порт Web UI / API:** `http://localhost:3011` / `http://localhost:8011`
- **Telegram Bot:** `@CyberGlowStudioBot`
- **Канал уведомлений:** `@Idrisov_prod`
