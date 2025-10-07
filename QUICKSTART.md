# Быстрый старт - Camera Agent Firmware

## 🎯 Что это такое?

Camera Agent - это программа, которая встраивается в прошивку IP-камеры и позволяет ей автоматически подключаться к облачному серверу видеонаблюдения. Это решает проблемы с NAT и обеспечивает стабильное соединение.

## 🔍 Проблема и решение

### ❌ Проблема (обычная схема):
```
Облачный сервер → NAT/Firewall → IP-камера (недоступна)
```

### ✅ Решение (с Camera Agent):
```
IP-камера + Agent → NAT/Firewall → Облачный сервер (подключение инициирует камера)
```

## 🚀 Быстрый старт за 5 минут

### 1. Подготовка

```bash
# Клонирование репозитория
git clone <repository-url>
cd camera-agent-firmware

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Создание агента для вашей камеры

```bash
# Для Dahua IPC-HFW2449
python tools/build_agent.py --camera dahua-2449 --output firmware/dahua/

# Для Hikvision DS-2CD2043  
python tools/build_agent.py --camera hikvision-ds2cd --output firmware/hikvision/

# Для Axis M3046-V
python tools/build_agent.py --camera axis-m30 --output firmware/axis/
```

### 3. Настройка конфигурации

```bash
# Редактирование конфигурации
nano firmware/dahua/config.json
```

Замените значения в конфигурации:
```json
{
  "agent": {
    "agent_id": "my-camera-001",
    "cloud_server_url": "wss://your-server.com/agent",
    "cloud_server_token": "your-secret-token"
  }
}
```

### 4. Сборка прошивки

```bash
cd firmware/dahua/
make build
```

### 5. Загрузка в камеру

#### Способ 1: Через веб-интерфейс
1. Откройте веб-интерфейс камеры (http://192.168.1.100)
2. Войдите в систему
3. Перейдите в System → Maintenance → Upgrade
4. Загрузите файл `dahua-2449_firmware.tar.gz`

#### Способ 2: Через SSH
```bash
# Копирование файла
scp dahua-2449_firmware.tar.gz admin@192.168.1.100:/tmp/

# Установка на камере
ssh admin@192.168.1.100
cd /tmp && tar -xzf dahua-2449_firmware.tar.gz
./install.sh
```

### 6. Запуск облачного сервера

```bash
# Запуск сервера для приема агентов
cd cloud-server
python server.py --host 0.0.0.0 --port 8080
```

### 7. Проверка работы

```bash
# Проверка подключенных агентов
curl http://localhost:8080/agents

# Проверка статуса агента на камере
ssh admin@192.168.1.100
systemctl status camera-agent
```

## 🧪 Тестирование

### Демонстрация

```bash
# Запуск демо с несколькими камерами
python example/demo.py --demo

# Тестирование конкретной камеры
python example/demo.py --camera dahua-2449 --duration 60

# Просмотр поддерживаемых камер
python example/demo.py --list
```

### Проверка соединения

```bash
# Проверка WebSocket соединения
wscat -c ws://localhost:8080/agent/test-agent-id

# Проверка RTSP потока
ffmpeg -i rtsp://192.168.1.100:554/stream1 -t 10 -f null -
```

## 📊 Мониторинг

### Логи агента на камере

```bash
# Просмотр логов systemd
journalctl -u camera-agent -f

# Просмотр файлов логов
tail -f /var/log/camera_agent/agent.log
```

### API облачного сервера

```bash
# Список агентов
curl http://localhost:8080/agents

# Статус конкретного агента
curl http://localhost:8080/agents/my-camera-001

# Список потоков
curl http://localhost:8080/streams

# Управление агентом
curl -X POST http://localhost:8080/agents/my-camera-001/control \
  -H "Content-Type: application/json" \
  -d '{"command": "restart"}'
```

## 🔧 Поддерживаемые камеры

| Производитель | Модель | Платформа | RTSP порт | Статус |
|---------------|--------|-----------|-----------|--------|
| **Dahua** | IPC-HFW2449 | Linux ARM | 554 | ✅ Поддерживается |
| **Dahua** | IPC-HDBW4431 | Linux ARM | 554 | ✅ Поддерживается |
| **Hikvision** | DS-2CD2043 | Linux ARM | 554 | ✅ Поддерживается |
| **Hikvision** | DS-2CD7xxx | Linux ARM | 554 | ✅ Поддерживается |
| **Axis** | M3046-V | Linux ARM | 554 | ✅ Поддерживается |
| **Axis** | M5035 | Linux ARM | 554 | ✅ Поддерживается |

## 🛠️ Устранение неполадок

### Агент не подключается

1. **Проверьте конфигурацию:**
   ```bash
   cat /etc/camera_agent/config.json
   ```

2. **Проверьте сеть:**
   ```bash
   ping your-server.com
   telnet your-server.com 8080
   ```

3. **Проверьте логи:**
   ```bash
   journalctl -u camera-agent --since "1 hour ago"
   ```

### Поток не передается

1. **Проверьте RTSP камеры:**
   ```bash
   ffmpeg -i rtsp://192.168.1.100:554/stream1 -t 5 -f null -
   ```

2. **Проверьте права:**
   ```bash
   ls -la /usr/bin/camera_agent
   ```

### Высокое использование ресурсов

1. **Уменьшите качество:**
   ```json
   {
     "streaming": {
       "quality": "medium"  // вместо "high"
     }
   }
   ```

2. **Уменьшите буфер:**
   ```json
   {
     "streaming": {
       "buffer_size": 1048576  // 1MB вместо 2MB
     }
   }
   ```

## 📚 Дополнительная документация

- **[Создание прошивки](docs/firmware.md)** - Подробное руководство
- **[API документация](docs/api.md)** - API облачного сервера
- **[Облачный сервер](docs/cloud-server.md)** - Настройка сервера
- **[Примеры интеграции](docs/integration.md)** - Интеграция с Flussonic Watcher

## 🆘 Поддержка

- **GitHub Issues** - Баги и предложения
- **Email** - support@camera-agent.com
- **Telegram** - @camera_agent_support

## 📄 Лицензия

MIT License - свободное использование и модификация

---

**Создано по образцу [Flussonic Agent](https://flussonic.ru/doc/agent-with-watcher/) для сообщества видеонаблюдения**


