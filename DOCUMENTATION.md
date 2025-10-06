# Camera Agent Firmware - Подробная документация

## 🎯 Обзор проекта

**Camera Agent Firmware** - это решение для встраивания агентов в прошивку IP-камер, аналогичное [Flussonic Agent](https://flussonic.ru/doc/agent-with-watcher/). Агент решает ключевые проблемы доступа к IP-камерам через NAT и обеспечивает стабильную передачу видео на облачные серверы.

## 🏗️ Архитектура решения

### Проблема, которую решает агент

**Обычная схема (проблемы):**
```
Облачный сервер → NAT/Firewall → IP-камера (недоступна)
```
- Камера недоступна извне из-за NAT
- Необходим проброс портов
- Нестабильное соединение
- Нет буферизации при потере пакетов

**Решение с Camera Agent (туннельная архитектура):**
```
IP-камера + Agent → NAT/Firewall → Туннельный сервер → Flussonic Watcher
                     ↓
              Камера доступна как 127.0.0.1 на сервере
```
- Агент создает туннель до туннельного сервера
- На сервере камера становится доступна как `127.0.0.1:8554`
- Flussonic Watcher подключается к камере как к локальному устройству
- Полная прозрачность для Flussonic Watcher

### Детальная архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    IP-КАМЕРА (Edge Device)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   RTSP Server   │  │  Camera Agent   │  │   File System   │ │
│  │   (встроенный)  │◄─┤   (наш код)     │─►│   (прошивка)    │ │
│  │                 │  │                 │  │                 │ │
│  │ - H.264/H.265   │  │ - WebSocket     │  │ - Конфигурация  │ │
│  │ - Multiple      │  │ - Буферизация   │  │ - Логи          │ │
│  │   Streams       │  │ - NAT Traversal │  │ - Записи        │ │
│  └─────────────────┘  │ - Переподключение│  └─────────────────┘ │
│                       │ - Heartbeat     │                      │
│                       └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ WebSocket + RTSP Stream
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNET + NAT/FIREWALL                     │
│  - Автоматический NAT Traversal                                │
│  - Шифрованное соединение                                      │
│  - Буферизация потерянных пакетов                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ОБЛАЧНЫЙ СЕРВЕР                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   WebSocket     │  │   Stream Relay  │  │   Management    │ │
│  │   Server        │◄─┤   Server        │─►│   API           │ │
│  │                 │  │                 │  │                 │ │
│  │ - Прием агентов │  │ - RTSP Relay    │  │ - REST API      │ │
│  │ - Heartbeat     │  │ - Load Balance  │  │ - Мониторинг    │ │
│  │ - Команды       │  │ - Recording     │  │ - Аналитика     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС                  │
│  - Веб-портал управления                                        │
│  - Мобильные приложения                                         │
│  - API для интеграции                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Компоненты системы

### 1. Camera Agent (Код агента)

**Расположение:** `agent/core/agent.py`

**Основные функции:**
- Подключение к облачному серверу через WebSocket
- Получение RTSP потоков с камеры
- Буферизация и переотправка потерянных пакетов
- Автоматическое переподключение при сбоях
- Отправка heartbeat и статистики
- Обработка команд от сервера

**Ключевые классы:**
```python
class CameraAgent:
    """Основной класс агента"""
    - start()           # Запуск агента
    - stop()            # Остановка агента
    - _connect_to_cloud()  # Подключение к серверу
    - _start_streaming()   # Запуск стриминга
    - _monitoring_loop()   # Мониторинг состояния

class CloudConnection:
    """Соединение с облачным сервером"""
    - register()        # Регистрация на сервере
    - send_stream_data() # Отправка потока
    - send_heartbeat()  # Отправка heartbeat

class StreamProcessor:
    """Обработка потоков камеры"""
    - start()           # Запуск обработки
    - get_stream_data() # Получение данных потока
    - stop()            # Остановка обработки
```

### 2. Инструмент сборки прошивки

**Расположение:** `tools/build_agent.py`

**Функции:**
- Создание прошивки для конкретной модели камеры
- Генерация платформо-специфичного кода
- Создание конфигурационных файлов
- Создание скриптов установки
- Создание архива прошивки

**Поддерживаемые камеры:**
```python
camera_configs = {
    "dahua-2449s-il": {
        "platform": "linux_arm",
        "architecture": "armv7",
        "rtsp_port": 554,
        "stream_paths": [
            "/cam/realmonitor?channel=1&subtype=0",  # Основной поток
            "/cam/realmonitor?channel=1&subtype=1"   # Подпоток
        ],
        "max_resolution": "2688x1520",
        "max_fps": 20,
        "codec": "H.265"
    }
}
```

### 3. Облачный сервер

**Расположение:** `cloud-server/server.py`

**Функции:**
- Прием WebSocket подключений от агентов
- Регистрация агентов
- Получение heartbeat и статистики
- Управление агентами через команды
- API для веб-интерфейса

**API эндпоинты:**
```
GET  /health              - Проверка здоровья сервера
GET  /agents              - Список агентов
GET  /agents/{id}         - Информация об агенте
POST /agents/{id}/control - Управление агентом
GET  /streams             - Список потоков
WS   /agent/{id}          - WebSocket для агента
```

## 🚀 Процесс работы

### 1. Создание прошивки

```bash
# Создание прошивки для Dahua IPC-HFW2449S-S-IL
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

**Что происходит:**
1. Копирование базового кода агента
2. Создание платформо-специфичных файлов
3. Генерация конфигурации для камеры
4. Создание скриптов установки
5. Создание архива прошивки (.tar.gz)

### 2. Установка на камеру

```bash
# Через веб-интерфейс камеры
# 1. Открыть http://IP-камеры
# 2. System → Maintenance → Upgrade
# 3. Загрузить dahua-2449s-il_firmware.tar.gz
# 4. Дождаться перезагрузки
```

**Что происходит:**
1. Распаковка архива прошивки
2. Копирование файлов агента в систему
3. Создание systemd сервиса
4. Включение автозапуска

### 3. Запуск агента

```bash
# На камере
systemctl start camera-agent
systemctl enable camera-agent
```

**Что происходит:**
1. Загрузка конфигурации из `/etc/camera_agent/config.json`
2. Подключение к облачному серверу через WebSocket
3. Регистрация агента на сервере
4. Запуск получения RTSP потоков
5. Начало отправки данных на сервер

### 4. Работа агента

**Цикл работы:**
1. **Подключение к серверу** - WebSocket соединение
2. **Регистрация** - отправка информации о камере
3. **Получение потоков** - чтение RTSP с камеры
4. **Отправка данных** - передача на сервер с буферизацией
5. **Heartbeat** - периодическая отправка статуса
6. **Мониторинг** - проверка соединения и переподключение

## 📁 Структура проекта

```
camera-agent-firmware/
├── agent/                          # Код агента для встраивания
│   ├── core/
│   │   └── agent.py               # Основной класс агента
│   ├── platform/
│   │   └── platform_specific.py   # Платформо-специфичный код
│   ├── streaming/
│   │   └── stream_handler.py      # Обработка потоков
│   └── networking/
│       └── cloud_connection.py    # Соединение с облаком
├── cloud-server/                   # Облачный сервер
│   └── server.py                  # FastAPI сервер
├── tools/                          # Инструменты
│   └── build_agent.py             # Сборщик прошивки
├── firmware/                       # Созданные прошивки
│   └── dahua-2449s-il/
│       ├── dahua-2449s-il_firmware.tar.gz
│       ├── config.json
│       ├── install.sh
│       └── INSTALL.md
├── docs/                           # Документация
├── example/                        # Примеры
└── requirements.txt               # Зависимости
```

## 🔧 Технические детали

### NAT Traversal

**Проблема:** Камера за NAT недоступна извне
**Решение:** Агент инициирует исходящее соединение

```python
# Агент подключается к серверу
websocket = await websockets.connect("wss://cloud-server.com/agent/agent-id")

# Сервер получает подключение и может отправлять команды
await websocket.send(json.dumps({
    "type": "command",
    "data": {"action": "restart"}
}))
```

### Буферизация

**Проблема:** Потеря пакетов при нестабильном соединении
**Решение:** Локальный буфер с повторной отправкой

```python
class CameraAgent:
    def __init__(self):
        self.buffer = []  # Буфер для потерянных пакетов
    
    async def _send_to_cloud(self, data: bytes):
        success = await self.connection.send_stream_data(data)
        if not success:
            # Добавление в буфер для повторной отправки
            self.buffer.append(data)
            await self._retry_buffered_data()
```

### Автоматическое переподключение

```python
async def _monitoring_loop(self):
    while self._running:
        try:
            await self._send_heartbeat()
            await self._check_connection()
        except Exception as e:
            await self._handle_connection_error()
            # Автоматическое переподключение
            await self._reconnect()
```

### Поддерживаемые протоколы

**RTSP потоки:**
- Основной поток: `/cam/realmonitor?channel=1&subtype=0`
- Подпоток: `/cam/realmonitor?channel=1&subtype=1`
- Аудио: `/cam/realmonitor?channel=1&subtype=2`

**WebSocket соединение:**
- Регистрация агента
- Передача потоков
- Heartbeat и статистика
- Команды управления

## 🛠️ Конфигурация

### Основная конфигурация агента

```json
{
  "agent": {
    "agent_id": "dahua-2449s-il-001",
    "cloud_server_url": "ws://your-server.com:8080/agent",
    "cloud_server_token": "your-secret-token",
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

### Конфигурация для конкретной камеры

```json
{
  "camera": {
    "model": "dahua-2449s-il",
    "max_resolution": "2688x1520",
    "max_fps": 20,
    "codec": "H.265",
    "features": ["WDR", "3D-DNR", "Smart Detection"]
  }
}
```

## 📊 Мониторинг и управление

### Статистика агента

```python
stats = {
    "bytes_sent": 1024000,      # Отправлено байт
    "bytes_received": 512000,   # Получено байт
    "packets_lost": 5,          # Потеряно пакетов
    "reconnections": 2,         # Переподключений
    "uptime": 3600,             # Время работы (сек)
    "buffer_size": 1024         # Размер буфера
}
```

### API управления

```bash
# Получение статуса агента
curl http://localhost:8080/agents/dahua-2449s-il-001

# Отправка команды агенту
curl -X POST http://localhost:8080/agents/dahua-2449s-il-001/control \
  -H "Content-Type: application/json" \
  -d '{"command": "restart"}'

# Получение списка потоков
curl http://localhost:8080/streams
```

### Логирование

```bash
# Просмотр логов агента на камере
journalctl -u camera-agent -f

# Файлы логов
tail -f /var/log/camera_agent/agent.log
```

## 🔒 Безопасность

### Шифрование соединения

```python
# WebSocket с SSL
websocket_url = "wss://secure-server.com/agent"

# Токен авторизации
headers = {
    "Authorization": f"Bearer {agent_token}"
}
```

### Аутентификация агентов

```python
# Регистрация с токеном
registration_data = {
    "agent_id": agent_id,
    "token": cloud_server_token,
    "camera_model": "dahua-2449s-il",
    "capabilities": ["rtsp", "recording", "motion_detection"]
}
```

## 🚀 Развертывание

### 1. Запуск облачного сервера

```bash
cd cloud-server
python server.py --host 0.0.0.0 --port 8080
```

### 2. Создание прошивки

```bash
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

### 3. Установка на камеру

```bash
# Загрузка через веб-интерфейс
# Или через SSH:
scp dahua-2449s-il_firmware.tar.gz admin@192.168.1.100:/tmp/
ssh admin@192.168.1.100 "cd /tmp && tar -xzf dahua-2449s-il_firmware.tar.gz && ./install.sh"
```

### 4. Настройка и запуск

```bash
# На камере
nano /etc/camera_agent/config.json  # Настройка
systemctl start camera-agent        # Запуск
systemctl enable camera-agent       # Автозапуск
```

## 📈 Преимущества решения

### По сравнению с обычным подходом:

1. **NAT Traversal** - не нужен проброс портов
2. **Стабильность** - автоматическое переподключение
3. **Буферизация** - нет потери данных при сбоях
4. **Масштабируемость** - централизованное управление
5. **Безопасность** - шифрованное соединение
6. **Мониторинг** - полная видимость состояния

### По сравнению с Flussonic Agent:

1. **Открытый код** - полная кастомизация
2. **Модульность** - легко расширять функциональность
3. **Гибкость** - поддержка разных протоколов
4. **Документация** - подробные инструкции

## 🔮 Возможности расширения

### Планируемые функции:

1. **AI детекция** - интеграция с TensorFlow/PyTorch
2. **Edge storage** - локальное хранение записей
3. **Multiple servers** - подключение к нескольким серверам
4. **Load balancing** - распределение нагрузки
5. **Mobile apps** - мобильные приложения управления
6. **Analytics** - аналитика использования

### Интеграции:

1. **Flussonic Watcher** - совместимость с Flussonic
2. **ONVIF** - стандартная совместимость
3. **REST API** - интеграция с внешними системами
4. **Webhooks** - уведомления о событиях

---

**Camera Agent Firmware** - это полноценное решение для встраивания агентов в IP-камеры, обеспечивающее надежную и масштабируемую передачу видео на облачные платформы видеонаблюдения.

