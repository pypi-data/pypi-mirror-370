## 1. Назначение

Что это:
- Connector.Telegram — компонент сбора сообщений из Telegram и публикации их в шину событий для дальнейшей обработки.

Какую проблему решает:
- Устраняет разрыв между внешним источником (Telegram) и внутренним пайплайном, обеспечивая надёжную, идемпотентную доставку событий.

---
## 2. Интерфейсы

HTTP API
- Отсутствует (нет публичного HTTP для Pre-Alpha).

Программный интерфейс (описание)
- Режимы запуска: online | import — подключение к Telegram и передача сообщений в очередь.

Message Queue Interface
- Queue: ingest.messages
- Message: IngestMessage (JSON, описательно)

Детализация интерфейсов (основная операция: публикация сообщения)
- Вход:
  - telegram_update: событие из Telegram (сообщение/медиа/метаданные)
- Выход:
  - IngestMessage: { source=telegram, source_id, timestamp (ISO 8601), content_type, payload_ref, metadata{chat_id, sender, reply_to?} }
- Правила:
  - Идемпотентность по source_id
  - Передаются ссылки/референсы на медиа, не содержимое
  - Соблюдение лимитов Telegram API (throttling)

---
## 3. Внешние зависимости
- Telegram API — получение online-сообщений и исторического набора
- Message Broker — публикация в ingest.messages (at-least-once)

---
## 4. Модели данных (описательно)
- IngestMessage — ключевые поля: source, source_id, timestamp, content_type, payload_ref, metadata{chat_id, sender, reply_to?}

---
## 5. Требования

Авторизация
- Доступ к Telegram через токен/учётные данные; внутренние интерфейсы без аутентификации (Pre-Alpha)

Мультитенантность
- Pre-Alpha: single-tenant, tenant_id не применяется

Идемпотентность
- Ключ: source_id; хранение ключей и дедупликация на уровне коннектора/очереди

Бизнес-правила
- Поддержка двух режимов: online и исторический импорт (batch)
- Ограничения по медиа передаются downstream (только ссылки)

---
## 6. Последовательности (runtime)
- Ingress: Telegram API (online/исторический импорт)
- Шаги:
  - Получить update из Telegram (message/media/metadata)
  - Сформировать IngestMessage: заполнить source, source_id, timestamp, content_type, payload_ref, metadata
  - Применить идемпотентность по source_id (пропустить дубликаты)
  - Опубликовать сообщение в брокер с политикой at-least-once
- Egress: Queue `ingest.messages` (сообщения IngestMessage)
