# Руководство по установке Camera Agent Firmware

## 📋 Оглавление

1. [Предварительные требования](#предварительные-требования)
2. [Установка зависимостей](#установка-зависимостей)
3. [Настройка облачного сервера](#настройка-облачного-сервера)
4. [Создание прошивки](#создание-прошивки)
5. [Установка на камеру](#установка-на-камеру)
6. [Настройка агента](#настройка-агента)
7. [Запуск и проверка](#запуск-и-проверка)
8. [Устранение неполадок](#устранение-неполадок)

## 🔧 Предварительные требования

### Системные требования

**Для разработки и сборки:**
- Python 3.8+
- Git
- Tar/Gzip
- Текстовый редактор

**Для облачного сервера:**
- Linux/Windows/macOS
- Python 3.8+
- 2GB RAM
- 10GB свободного места
- Сетевой доступ

**Для камеры:**
- IP-камера с Linux (ARM/x86)
- SSH доступ или веб-интерфейс
- 100MB свободного места
- Сетевой доступ

### Поддерживаемые камеры

| Модель | Платформа | Архитектура | Статус |
|--------|-----------|-------------|--------|
| Dahua IPC-HFW2449S-S-IL | Linux | ARMv7 | ✅ Поддерживается |
| Hikvision DS-2CD2xxx | Linux | ARMv7 | 🔄 В разработке |
| Axis M30xx | Linux | ARMv7 | 🔄 В разработке |

## 📦 Установка зависимостей

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/camera-agent-firmware.git
cd camera-agent-firmware
```

### 2. Установка Python зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация окружения
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Проверка установки

```bash
# Проверка версии Python
python --version

# Проверка зависимостей
python -c "import fastapi, uvicorn, websockets; print('Все зависимости установлены')"
```

## 🌐 Настройка облачного сервера

### 1. Создание конфигурации

```bash
# Создание файла конфигурации
cp cloud-server/config.example.json cloud-server/config.json
```

### 2. Редактирование конфигурации

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "ssl": false,
    "cert_file": null,
    "key_file": null
  },
  "agents": {
    "max_agents": 1000,
    "heartbeat_timeout": 60,
    "registration_timeout": 30
  },
  "security": {
    "secret_token": "your-very-secret-token-here",
    "allowed_origins": ["*"]
  },
  "logging": {
    "level": "INFO",
    "file": "logs/server.log"
  }
}
```

### 3. Запуск сервера

```bash
cd cloud-server

# Запуск в режиме разработки
python server.py --host 0.0.0.0 --port 8080

# Запуск в продакшене
python server.py --config config.json --daemon
```

### 4. Проверка работы сервера

```bash
# Проверка здоровья сервера
curl http://localhost:8080/health

# Ожидаемый ответ:
{
  "status": "healthy",
  "uptime": 3600,
  "agents_connected": 0,
  "version": "1.0.0"
}
```

## 🔨 Создание прошивки

### 1. Создание прошивки для Dahua IPC-HFW2449S-S-IL

```bash
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

### 2. Проверка созданной прошивки

```bash
ls -la firmware/dahua-2449s-il/
# Должны быть файлы:
# - dahua-2449s-il_firmware.tar.gz
# - config.json
# - install.sh
# - INSTALL.md
```

### 3. Содержимое прошивки

```bash
# Просмотр содержимого архива
tar -tzf firmware/dahua-2449s-il/dahua-2449s-il_firmware.tar.gz

# Распаковка для проверки
mkdir temp_extract
cd temp_extract
tar -xzf ../firmware/dahua-2449s-il/dahua-2449s-il_firmware.tar.gz
ls -la
```

## 📷 Установка на камеру

### Метод 1: Через веб-интерфейс (рекомендуется)

1. **Открыть веб-интерфейс камеры**
   ```
   http://IP-адрес-камеры
   ```

2. **Войти в систему**
   - Логин: `admin`
   - Пароль: `admin` (или ваш пароль)

3. **Перейти в раздел обновления**
   ```
   System → Maintenance → Upgrade
   ```

4. **Загрузить прошивку**
   - Выбрать файл: `dahua-2449s-il_firmware.tar.gz`
   - Нажать "Upgrade"
   - Дождаться завершения

5. **Перезагрузка камеры**
   - Камера автоматически перезагрузится
   - Дождаться полной загрузки

### Метод 2: Через SSH

```bash
# Копирование файла на камеру
scp dahua-2449s-il_firmware.tar.gz admin@192.168.1.100:/tmp/

# Подключение к камере
ssh admin@192.168.1.100

# На камере - распаковка и установка
cd /tmp
tar -xzf dahua-2449s-il_firmware.tar.gz
chmod +x install.sh
./install.sh
```

### Метод 3: Через TFTP (для продвинутых пользователей)

```bash
# Настройка TFTP сервера
sudo apt-get install tftpd-hpa
sudo systemctl start tftpd-hpa

# Размещение файла
sudo cp dahua-2449s-il_firmware.tar.gz /srv/tftp/

# Загрузка через веб-интерфейс камеры
# System → Maintenance → TFTP Upgrade
# Server: IP-адрес-вашего-PC
# File: dahua-2449s-il_firmware.tar.gz
```

## ⚙️ Настройка агента

### 1. Редактирование конфигурации

```bash
# На камере
nano /etc/camera_agent/config.json
```

### 2. Основные настройки

```json
{
  "agent": {
    "agent_id": "dahua-2449s-il-001",
    "cloud_server_url": "ws://YOUR-SERVER-IP:8080/agent",
    "cloud_server_token": "your-very-secret-token-here",
    "log_level": "INFO"
  },
  "streaming": {
    "quality": "high",
    "buffer_size": 2097152,
    "rtsp_port": 554,
    "stream_paths": [
      "/cam/realmonitor?channel=1&subtype=0",
      "/cam/realmonitor?channel=1&subtype=1"
    ]
  },
  "network": {
    "connection_timeout": 30,
    "reconnect_interval": 10,
    "heartbeat_interval": 30
  }
}
```

### 3. Настройка RTSP

```bash
# Проверка доступных RTSP потоков
ffprobe rtsp://admin:admin@192.168.1.100/cam/realmonitor?channel=1&subtype=0

# Настройка RTSP параметров в конфигурации
{
  "streaming": {
    "rtsp_username": "admin",
    "rtsp_password": "admin",
    "rtsp_timeout": 10
  }
}
```

## 🚀 Запуск и проверка

### 1. Запуск агента

```bash
# На камере
systemctl start camera-agent

# Проверка статуса
systemctl status camera-agent

# Включение автозапуска
systemctl enable camera-agent
```

### 2. Проверка логов

```bash
# Просмотр логов в реальном времени
journalctl -u camera-agent -f

# Просмотр файла логов
tail -f /var/log/camera_agent/agent.log
```

### 3. Проверка подключения к серверу

```bash
# На сервере - проверка подключенных агентов
curl http://localhost:8080/agents

# Ожидаемый ответ:
{
  "agents": [
    {
      "agent_id": "dahua-2449s-il-001",
      "status": "connected",
      "camera_model": "dahua-2449s-il",
      "last_heartbeat": "2024-01-15T10:30:00Z",
      "streams": 2
    }
  ]
}
```

### 4. Проверка потоков

```bash
# Проверка доступных потоков
curl http://localhost:8080/streams

# Ожидаемый ответ:
{
  "streams": [
    {
      "agent_id": "dahua-2449s-il-001",
      "stream_id": "main",
      "url": "rtsp://localhost:8554/dahua-2449s-il-001/main",
      "status": "active"
    },
    {
      "agent_id": "dahua-2449s-il-001",
      "stream_id": "sub",
      "url": "rtsp://localhost:8554/dahua-2449s-il-001/sub",
      "status": "active"
    }
  ]
}
```

## 🔧 Устранение неполадок

### Проблема: Агент не подключается к серверу

**Симптомы:**
- В логах: "Connection failed"
- На сервере агент не появляется в списке

**Решения:**
1. **Проверить сетевую связность**
   ```bash
   # На камере
   ping YOUR-SERVER-IP
   telnet YOUR-SERVER-IP 8080
   ```

2. **Проверить конфигурацию**
   ```bash
   # Проверить URL сервера
   cat /etc/camera_agent/config.json | grep cloud_server_url
   ```

3. **Проверить токен**
   ```bash
   # Убедиться, что токены совпадают
   # В config.json агента и на сервере
   ```

### Проблема: RTSP потоки недоступны

**Симптомы:**
- В логах: "RTSP stream not available"
- Нет данных в потоках

**Решения:**
1. **Проверить RTSP доступность**
   ```bash
   # На камере
   ffprobe rtsp://admin:admin@localhost/cam/realmonitor?channel=1&subtype=0
   ```

2. **Проверить учетные данные**
   ```bash
   # Убедиться, что логин/пароль правильные
   # В конфигурации агента
   ```

3. **Проверить пути потоков**
   ```bash
   # Для разных моделей камер пути могут отличаться
   # Проверить документацию камеры
   ```

### Проблема: Высокое потребление CPU

**Симптомы:**
- Медленная работа камеры
- Высокая нагрузка на процессор

**Решения:**
1. **Уменьшить качество потока**
   ```json
   {
     "streaming": {
       "quality": "medium"  // вместо "high"
     }
   }
   ```

2. **Увеличить интервалы**
   ```json
   {
     "network": {
       "heartbeat_interval": 60  // вместо 30
     }
   }
   ```

### Проблема: Нестабильное соединение

**Симптомы:**
- Частые переподключения
- Потеря данных

**Решения:**
1. **Увеличить буфер**
   ```json
   {
     "streaming": {
       "buffer_size": 4194304  // 4MB вместо 2MB
     }
   }
   ```

2. **Настроить таймауты**
   ```json
   {
     "network": {
       "connection_timeout": 60,
       "reconnect_interval": 5
     }
   }
   ```

## 📊 Мониторинг

### 1. Системные метрики

```bash
# На камере
# Использование CPU
top -p $(pgrep camera-agent)

# Использование памяти
ps aux | grep camera-agent

# Сетевой трафик
iftop -i eth0
```

### 2. Логи агента

```bash
# Критические ошибки
journalctl -u camera-agent -p err

# Все логи за последний час
journalctl -u camera-agent --since "1 hour ago"
```

### 3. Статистика сервера

```bash
# На сервере
curl http://localhost:8080/stats

# Детальная информация об агенте
curl http://localhost:8080/agents/dahua-2449s-il-001/stats
```

## 🔄 Обновление

### 1. Обновление агента

```bash
# Создание новой прошивки
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il-v2

# Остановка агента
systemctl stop camera-agent

# Загрузка новой прошивки (через веб-интерфейс или SSH)
# Установка
./install.sh

# Запуск
systemctl start camera-agent
```

### 2. Обновление сервера

```bash
# Остановка сервера
pkill -f server.py

# Обновление кода
git pull origin main

# Перезапуск
python server.py --config config.json --daemon
```

## 📞 Поддержка

### Полезные команды

```bash
# Полная диагностика
systemctl status camera-agent
journalctl -u camera-agent --no-pager
cat /etc/camera_agent/config.json
ping YOUR-SERVER-IP

# Сброс конфигурации
cp /etc/camera_agent/config.json.default /etc/camera_agent/config.json

# Перезапуск агента
systemctl restart camera-agent
```

### Логи для поддержки

```bash
# Сбор логов для отправки в поддержку
mkdir logs_collection
cp /var/log/camera_agent/agent.log logs_collection/
journalctl -u camera-agent --no-pager > logs_collection/systemd.log
cat /etc/camera_agent/config.json > logs_collection/config.json
tar -czf support_logs.tar.gz logs_collection/
```

---

**Поздравляем!** Вы успешно установили и настроили Camera Agent Firmware. Агент теперь подключается к облачному серверу и передает видеопотоки с вашей IP-камеры.

