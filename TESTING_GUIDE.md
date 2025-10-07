# 🧪 Руководство по тестированию Camera Agent

## Что мы можем протестировать локально

Имея разархивированную прошивку Flussonic Agent, мы можем:

1. ✅ **Проанализировать файлы** - изучить структуру и конфигурацию
2. ✅ **Протестировать наш агент** - запустить в режиме симуляции
3. ✅ **Сравнить протоколы** - убедиться в совместимости
4. ⚠️ **Запустить peeklio1** - сложно (ARM архитектура, зависимости)

---

## 📂 Доступные файлы из прошивки

Из `C:\Users\King\Desktop\Dahua\firmware_extracted\`:

```
manual_extract/
├── romfs-x.squashfs.img ← Основная файловая система (19MB)
│   Содержит: peeklio1, app.sh, сертификаты
├── web-x.squashfs.img ← Web интерфейс (7.2MB)
├── kernel.img ← Ядро Linux (2.5MB)
└── другие компоненты...
```

---

## 🔍 Что мы уже узнали из анализа

### 1. Запуск peeklio1

Из `app.sh`:
```bash
./peeklio1 -c /mnt/mtd/Config/peeklio.cfg \
           -A C1.pem \
           -e peeklioroot.crt \
           -M 2956 \
           -S $deviceid
```

### 2. Параметры

| Параметр | Описание | Наша реализация |
|----------|----------|-----------------|
| `-c peeklio.cfg` | Конфигурация | `config.json` |
| `-A C1.pem` | SSL сертификат клиента | `agent.pem` |
| `-e peeklioroot.crt` | Root SSL | `root.crt` |
| `-M 2956` | Порт туннеля | `tunnel_port: 2956` |
| `-S deviceid` | Device ID | Авто из armbenv |

---

## 🚀 Тестирование нашего агента

### Вариант 1: Симуляция на Windows

```bash
# 1. Переходим в директорию проекта
cd C:\Cursor\camera-agent-firmware

# 2. Устанавливаем зависимости
pip install -r requirements.txt

# 3. Настраиваем конфигурацию
# Редактируем: firmware/dahua-2449s-il/config.json

# 4. Запускаем в режиме симуляции
python demo_windows.py
```

### Вариант 2: Тестирование на Linux VM

```bash
# 1. Клонируем репозиторий
git clone https://github.com/twinleq/camera-agent.git
cd camera-agent

# 2. Устанавливаем зависимости
pip3 install -r requirements.txt

# 3. Запускаем агента
python3 -m agent.core.agent --config firmware/dahua-2449s-il/config.json
```

### Вариант 3: Docker контейнер

```bash
# 1. Сборка образа
docker build -t camera-agent .

# 2. Запуск
docker run -d \
  --name camera-agent \
  -v ./firmware/dahua-2449s-il/config.json:/app/config.json \
  camera-agent
```

---

## 🧩 Тестирование совместимости с Flussonic

### Шаг 1: Настройка туннельного сервера

Создайте простой туннельный сервер:

```python
# tunnel_test_server.py
import asyncio
import websockets
import json

async def handle_agent(websocket, path):
    print("[SERVER] Агент подключился")
    
    # Принимаем регистрацию
    registration = await websocket.recv()
    data = json.loads(registration)
    print(f"[SERVER] Регистрация: {data}")
    
    # Подтверждаем
    response = {
        "status": "registered",
        "device_id": data.get("device_id"),
        "tunnel_port": 2956
    }
    await websocket.send(json.dumps(response))
    
    # Слушаем heartbeat
    async for message in websocket:
        msg_data = json.loads(message)
        print(f"[SERVER] Получено: {msg_data}")

async def main():
    server = await websockets.serve(handle_agent, "0.0.0.0", 8080)
    print("[SERVER] Туннельный сервер запущен на ws://0.0.0.0:8080")
    await server.wait_closed()

asyncio.run(main())
```

Запуск:
```bash
python tunnel_test_server.py
```

### Шаг 2: Настройка агента

Отредактируйте `firmware/dahua-2449s-il/config.json`:

```json
{
  "agent": {
    "connection_mode": "tunnel"
  },
  "tunnel": {
    "enabled": true,
    "server_url": "ws://localhost:8080",
    "server_token": "test-token",
    "tunnel_port": 2956
  }
}
```

### Шаг 3: Запуск агента

```bash
python demo_windows.py
```

### Ожидаемый результат:

```
[AGENT] Запуск Camera Agent (Device ID: test-device-001)
[TUNNEL] Режим туннеля активирован
[TUNNEL] Подключение к ws://localhost:8080
[TUNNEL] Регистрация успешна
[TUNNEL] Туннель создан: 127.0.0.1:2956
[AGENT] Camera Agent запущен успешно
```

На сервере:
```
[SERVER] Агент подключился
[SERVER] Регистрация: {"device_id": "test-device-001", ...}
[SERVER] Получено: {"type": "heartbeat", ...}
```

---

## 🔬 Извлечение дополнительной информации из прошивки

### Поиск конфигурационных файлов

В Linux VM:
```bash
# Распаковываем romfs-x.squashfs.img
cd ~/firmware_analysis
dumpimage -T standalone -p 0 romfs-x.squashfs.img -o romfs-payload.gz
gunzip romfs-payload.gz
unsquashfs romfs-payload

# Ищем конфигурацию
cd squashfs-root/
find . -name "*.cfg" -o -name "*.conf" -o -name "*.pem" -o -name "*.crt"
```

### Анализ peeklio1

```bash
# Информация о бинарнике
file squashfs-root/mnt/app/peeklio1

# Зависимости (если есть ldd)
ldd squashfs-root/mnt/app/peeklio1

# Строки внутри (ищем URL, параметры)
strings squashfs-root/mnt/app/peeklio1 | grep -i "http\|wss\|rtsp\|server\|device"
```

---

## 📊 Мониторинг и отладка

### Логи агента

```bash
# Просмотр логов
tail -f logs/agent.log

# Поиск ошибок
grep -i "error\|failed" logs/agent.log
```

### Метрики (Prometheus)

Агент экспортирует метрики на `http://localhost:9090/metrics`:

```bash
# Проверка метрик
curl http://localhost:9090/metrics

# Ключевые метрики:
# - agent_status (0=stopped, 1=starting, 2=connected, 3=streaming, 4=error)
# - agent_uptime_seconds
# - tunnel_connected (0/1)
# - p2p_connected (0/1)
```

---

## 🐛 Troubleshooting

### Проблема: Агент не подключается к серверу

**Решение:**
1. Проверьте `server_url` в конфигурации
2. Убедитесь что сервер запущен: `netstat -an | findstr 8080`
3. Проверьте firewall: `netsh advfirewall show currentprofile`

### Проблема: SSL ошибка

**Решение:**
1. Проверьте наличие сертификатов: `agent.pem`, `root.crt`
2. Для тестирования отключите SSL: `"ssl_enabled": false`

### Проблема: Камера не обнаружена

**Решение:**
1. Проверьте IP камеры: `ping 192.168.1.10`
2. Проверьте RTSP: `ffprobe rtsp://192.168.1.10:554/...`
3. Включите авто-определение: `"auto_detect_ip": true`

---

## 📋 Чеклист тестирования

- [ ] ✅ Агент запускается без ошибок
- [ ] ✅ Подключение к туннельному серверу
- [ ] ✅ Регистрация с device_id
- [ ] ✅ Heartbeat отправляется каждые 30 секунд
- [ ] ✅ Туннель создан на порту 2956
- [ ] ✅ SSL аутентификация работает
- [ ] ✅ Метрики экспортируются
- [ ] ⚠️ P2P режим (требует STUN/TURN сервера)
- [ ] ⚠️ Hybrid режим с fallback
- [ ] ⚠️ Прямое тестирование на камере

---

## 🎯 Следующие шаги

1. **Локальное тестирование** ← Мы здесь
   - Запустить агента на Windows/Linux
   - Протестировать туннель
   - Проверить совместимость протокола

2. **Тестирование на реальной камере**
   - Собрать прошивку для Dahua
   - Заменить peeklio1 на наш агент
   - Протестировать с реальным RTSP потоком

3. **Интеграция с Flussonic Watcher**
   - Настроить реальный Flussonic сервер
   - Подключить агента
   - Проверить видео потоки

---

## 📚 Дополнительные материалы

- [FLUSSONIC_ANALYSIS.md](FLUSSONIC_ANALYSIS.md) - Полный анализ peeklio1
- [QUICK_COMMANDS.md](QUICK_COMMANDS.md) - Быстрые команды для Linux
- [LINUX_ANALYSIS_GUIDE.md](LINUX_ANALYSIS_GUIDE.md) - Анализ прошивки на Linux VM

---

**Обновлено**: 7 октября 2025  
**Статус**: 🟢 Готово к локальному тестированию
