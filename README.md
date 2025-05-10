# Конфигурация приложения

## Настройка конфигурационного файла

Для работы приложения требуется файл конфигурации `config.yaml` в корне проекта.

## 📌 Пример конфигурации (`config.yaml`)

```yaml
# API Settings
api:
  run:
    host: "127.0.0.1"           # Хост для запуска сервера
    port: 8080                  # Порт приложения (1024-65535)
    root_path: "/api"           # Базовый путь для API эндпоинтов
  
  JWT:
    SECRET_KEY: "secret-key"    # Обязательно 32+ символов
    ALGORITHM: "HS256"          # Алгоритм подписи (HS256/HS384/HS512)

# Database Configuration
db:
  DB_HOST: "db-host"            # Адрес сервера PostgreSQL
  DB_PORT: 5432                 # Порт БД (обычно 5432)
  DB_USER: "admin"              # Логин для подключения
  DB_PASS: "strong-password"    # Пароль (рекомендуется использовать env-переменные)
  DB_NAME: "database-name"      # Название базы данных
  
  # Connection Pool Settings
  echo: true                    # Логировать SQL запросы (debug режим)
  pool_size: 20                 # Размер пула подключений (рекомендуется 10-30)
  max_overflow: 10              # Дополнительные подключения при нагрузке