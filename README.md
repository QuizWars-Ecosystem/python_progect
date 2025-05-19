# Конфигурация приложения

## Настройка конфигурационного файла

Для работы приложения требуется файл конфигурации `config.yaml` в корне проекта.

## 📌 Пример конфигурации (`config.yaml`)

```yaml
# API Settings
api:
  host: "127.0.0.1"           # Хост для запуска сервера (по умолчанию: 127.0.0.1)
  port: 8080                  # Порт приложения (по умолчанию: 8080)
  root_path: "/api"           # Базовый путь для API эндпоинтов (по умолчанию: "/api")
  
  # JWT Authentication
  jwt:
    secret_key: "your-secret-key-32+chars"  # Обязательно 32+ символа
    algorithm: "HS256"                      # Алгоритм подписи (по умолчанию: HS256)

# Jobs Configuration
jobs:
  - name: "trivia-api"        # Уникальное имя job
    url: "https://opentdb.com/api.php"  # URL для получения данных
    mode: "CRON"              # Режим работы: CRON или TIMER (по умолчанию: CRON)
    schedule: "*/5 * * * *"   # Расписание в формате cron (для mode=CRON)
    interval: null            # Интервал в секундах (для mode=TIMER)
    state: "WORKING"          # Состояние: WORKING, PAUSED или STOPPED

# Send Configuration
send:
  batch_size: 5               # Размер пачки для отправки (min: 1)
  check_interval: 30          # Интервал проверки в минутах (min: 1)
  min_questions: 200          # Минимальное количество вопросов для отправки (min: 1)
  cron_schedule: "0 */6 * * *" # Расписание отправки в формате cron
  api_key: "your-api-key"     # API ключ для аутентификации на основном сервере
  main_server_url: "https://main-server.example.com/api/questions"  # URL для отправки вопросов

# Database Configuration
db:
  DB_HOST: "localhost"        # Адрес сервера PostgreSQL
  DB_PORT: 5432               # Порт БД (обычно 5432)
  DB_USER: "postgres"         # Логин для подключения
  DB_PASS: "password"         # Пароль (рекомендуется использовать env-переменные)
  DB_NAME: "postgres"         # Название базы данных
  
  # Connection Pool Settings
  echo: true                  # Логировать SQL запросы (debug режим, по умолчанию: false)
  pool_size: 20               # Размер пула подключений (рекомендуется 10-30, min:1, max:100)
  max_overflow: 10            # Дополнительные подключения при нагрузке (min: 0)е подключения при нагрузке