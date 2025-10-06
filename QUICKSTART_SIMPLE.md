# Camera Agent Firmware - Быстрый старт

## 🎯 Что это такое?

**Camera Agent Firmware** - это агент, который встраивается в прошивку IP-камеры и автоматически подключается к облачному серверу, решая проблемы NAT traversal и обеспечивая стабильную передачу видео.

## ⚡ Быстрый запуск (5 минут)

### Шаг 1: Запуск облачного сервера

```bash
# Переход в директорию проекта
cd camera-agent-firmware

# Запуск облачного сервера
cd cloud-server
python server.py --host 0.0.0.0 --port 8080
```

**Результат:** Сервер запущен на `http://localhost:8080`

### Шаг 2: Создание прошивки для камеры

```bash
# В новом терминале
cd camera-agent-firmware

# Создание прошивки для Dahua IPC-HFW2449S-S-IL
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

**Результат:** Создан файл `firmware/dahua-2449s-il/dahua-2449s-il_firmware.tar.gz`

### Шаг 3: Установка на камеру

1. **Откройте веб-интерфейс камеры:**
   ```
   http://IP-адрес-камеры
   ```

2. **Войдите в систему:**
   - Логин: `admin`
   - Пароль: `admin`

3. **Перейдите в раздел обновления:**
   ```
   System → Maintenance → Upgrade
   ```

4. **Загрузите прошивку:**
   - Выберите файл: `dahua-2449s-il_firmware.tar.gz`
   - Нажмите "Upgrade"
   - Дождитесь перезагрузки

### Шаг 4: Проверка работы

```bash
# Проверка подключенных агентов
curl http://localhost:8080/agents

# Проверка потоков
curl http://localhost:8080/streams
```

**Ожидаемый результат:**
```json
{
  "agents": [
    {
      "agent_id": "dahua-2449s-il-001",
      "status": "connected",
      "camera_model": "dahua-2449s-il",
      "last_heartbeat": "2024-01-15T10:30:00Z"
    }
  ],
  "streams": [
    {
      "agent_id": "dahua-2449s-il-001",
      "stream_id": "main",
      "url": "rtsp://localhost:8554/dahua-2449s-il-001/main",
      "status": "active"
    }
  ]
}
```

## 🔧 Настройка (опционально)

### Изменение настроек агента

```bash
# На камере (через SSH)
nano /etc/camera_agent/config.json
```

**Основные параметры:**
```json
{
  "agent": {
    "agent_id": "dahua-2449s-il-001",
    "cloud_server_url": "ws://YOUR-SERVER-IP:8080/agent",
    "cloud_server_token": "your-secret-token"
  },
  "streaming": {
    "quality": "high",
    "buffer_size": 2097152
  }
}
```

### Перезапуск агента

```bash
# На камере
systemctl restart camera-agent

# Проверка статуса
systemctl status camera-agent
```

## 📊 Мониторинг

### Просмотр логов

```bash
# На камере
journalctl -u camera-agent -f

# На сервере
tail -f cloud-server/logs/server.log
```

### API для управления

```bash
# Получение статуса агента
curl http://localhost:8080/agents/dahua-2449s-il-001

# Отправка команды агенту
curl -X POST http://localhost:8080/agents/dahua-2449s-il-001/control \
  -H "Content-Type: application/json" \
  -d '{"command": "restart"}'
```

## 🆘 Устранение неполадок

### Агент не подключается

1. **Проверьте сетевую связность:**
   ```bash
   # На камере
   ping YOUR-SERVER-IP
   ```

2. **Проверьте конфигурацию:**
   ```bash
   cat /etc/camera_agent/config.json
   ```

3. **Проверьте логи:**
   ```bash
   journalctl -u camera-agent -n 50
   ```

### RTSP потоки недоступны

1. **Проверьте RTSP доступность:**
   ```bash
   ffprobe rtsp://admin:admin@192.168.1.100/cam/realmonitor?channel=1&subtype=0
   ```

2. **Проверьте учетные данные в конфигурации**

## 📖 Подробная документация

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Полное описание архитектуры и возможностей
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Подробное руководство по установке
- **[docs/firmware.md](docs/firmware.md)** - Документация по прошивке

## 🎉 Готово!

Теперь ваша IP-камера автоматически подключается к облачному серверу и передает видеопотоки. Агент решает проблемы NAT traversal и обеспечивает стабильную связь.

