# Создание прошивки с Camera Agent

## Обзор

Camera Agent предназначен для встраивания в прошивку IP-камер для автоматического подключения к облачному серверу видеонаблюдения. Это решает проблемы NAT traversal и обеспечивает стабильное соединение.

## 🎯 Принцип работы

### Обычная схема (проблемы):
```
Облачный сервер → NAT/Firewall → IP-камера (недоступна)
```

### С Camera Agent (решение):
```
IP-камера + Agent → NAT/Firewall → Облачный сервер (подключение инициирует камера)
```

## 🔧 Поддерживаемые камеры

### Dahua (Dahua Technology)
- **IPC-HFW2449** - 4MP купольная камера
- **IPC-HDBW4431** - 4MP купольная камера  
- **IPC-HFW4831** - 8MP купольная камера
- **IPC-HDW4831** - 8MP купольная камера

### Hikvision
- **DS-2CD2xxx** серия - 2MP камеры
- **DS-2CD7xxx** серия - 7MP камеры
- **DS-2CD4xxx** серия - 4MP камеры

### Axis Communications
- **M30** серия - сетевая камера
- **M50** серия - сетевая камера
- **P12** серия - PTZ камера

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Клонирование репозитория
git clone <repository-url>
cd camera-agent-firmware

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Создание агента для камеры

```bash
# Сборка агента для Dahua IPC-HFW2449
python tools/build_agent.py --camera dahua-2449 --output firmware/dahua-2449/

# Сборка агента для Hikvision DS-2CD2043
python tools/build_agent.py --camera hikvision-ds2cd --output firmware/hikvision/
```

### 3. Настройка конфигурации

```bash
# Редактирование конфигурации
nano firmware/dahua-2449/config.json
```

Пример конфигурации:
```json
{
  "agent": {
    "agent_id": "dahua-001",
    "cloud_server_url": "wss://your-cloud-server.com/agent",
    "cloud_server_token": "your-secret-token",
    "log_level": "INFO"
  },
  "streaming": {
    "quality": "high",
    "buffer_size": 2097152,
    "rtsp_port": 554,
    "stream_paths": ["/cam/realmonitor?channel=1&subtype=0"]
  },
  "network": {
    "connection_timeout": 30,
    "reconnect_interval": 10,
    "heartbeat_interval": 30
  }
}
```

### 4. Сборка прошивки

```bash
cd firmware/dahua-2449/
make build
```

### 5. Загрузка в камеру

#### Метод 1: Через веб-интерфейс камеры

1. Откройте веб-интерфейс камеры (обычно http://192.168.1.100)
2. Войдите в систему (admin/admin по умолчанию)
3. Перейдите в раздел "System" → "Maintenance" → "Upgrade"
4. Загрузите файл `dahua-2449_firmware.tar.gz`
5. Нажмите "Upgrade"

#### Метод 2: Через TFTP

```bash
# Настройка TFTP сервера
sudo apt-get install tftpd-hpa
sudo cp dahua-2449_firmware.tar.gz /srv/tftp/

# Загрузка через TFTP на камере
tftp -g -r dahua-2449_firmware.tar.gz 192.168.1.10
```

#### Метод 3: Через SSH (если доступен)

```bash
# Копирование файла на камеру
scp dahua-2449_firmware.tar.gz admin@192.168.1.100:/tmp/

# Подключение к камере
ssh admin@192.168.1.100

# Установка агента
cd /tmp
tar -xzf dahua-2449_firmware.tar.gz
./install.sh
```

## 🔧 Детальная настройка

### Конфигурация агента

#### Основные параметры:

```json
{
  "agent": {
    "agent_id": "unique-agent-id",           // Уникальный ID агента
    "cloud_server_url": "wss://server.com",  // URL облачного сервера
    "cloud_server_token": "secret-token",    // Токен авторизации
    "log_level": "INFO"                      // Уровень логирования
  }
}
```

#### Настройки стриминга:

```json
{
  "streaming": {
    "quality": "high",                       // Качество: low/medium/high
    "buffer_size": 2097152,                  // Размер буфера (байты)
    "rtsp_port": 554,                        // Порт RTSP сервера камеры
    "stream_paths": [                        // Пути к потокам
      "/cam/realmonitor?channel=1&subtype=0"
    ]
  }
}
```

#### Сетевые настройки:

```json
{
  "network": {
    "connection_timeout": 30,                // Таймаут подключения (сек)
    "reconnect_interval": 10,                // Интервал переподключения (сек)
    "heartbeat_interval": 30,                // Интервал heartbeat (сек)
    "max_retries": 5                         // Максимум попыток переподключения
  }
}
```

### Платформо-специфичные настройки

#### Dahua камеры:

```json
{
  "camera": {
    "model": "dahua-2449",
    "platform": "linux_arm",
    "architecture": "armv7",
    "rtsp_port": 554,
    "http_port": 80,
    "config_file": "/mnt/mtd/Config/Account1"
  }
}
```

#### Hikvision камеры:

```json
{
  "camera": {
    "model": "hikvision-ds2cd",
    "platform": "linux_arm", 
    "architecture": "armv7",
    "rtsp_port": 554,
    "http_port": 80,
    "config_file": "/davinci/account"
  }
}
```

## 🛠️ Разработка

### Создание агента для новой камеры

1. **Исследование платформы камеры:**

```bash
# Подключение к камере по SSH (если доступен)
ssh admin@192.168.1.100

# Проверка архитектуры
uname -a
cat /proc/cpuinfo

# Проверка доступных портов
netstat -tlnp

# Проверка RTSP потоков
ffmpeg -i rtsp://192.168.1.100:554/stream1 -t 5 -f null -
```

2. **Создание конфигурации:**

```bash
# Создание конфигурации для новой камеры
python tools/create_camera_config.py --camera new-model --output configs/
```

3. **Добавление в сборщик:**

```python
# Добавление в camera_configs в build_agent.py
"new-model": {
    "platform": "linux_arm",
    "architecture": "armv7", 
    "libc": "uclibc",
    "rtsp_port": 554,
    "http_port": 80,
    "stream_paths": ["/your/stream/path"],
    "config_file": "/path/to/config",
    "binary_path": "/usr/bin/camera_agent"
}
```

### Тестирование агента

#### Локальное тестирование:

```bash
# Запуск агента в тестовом режиме
python agent/core/agent.py --config test-config.json --test-mode

# Проверка подключения к облачному серверу
curl http://localhost:8080/agents
```

#### Тестирование на реальной камере:

```bash
# Загрузка тестовой версии
scp test-agent.tar.gz admin@192.168.1.100:/tmp/

# Установка на камере
ssh admin@192.168.1.100
cd /tmp && tar -xzf test-agent.tar.gz
./install.sh

# Проверка работы
systemctl status camera-agent
journalctl -u camera-agent -f
```

## 🔍 Отладка

### Логи агента

```bash
# Просмотр логов systemd
journalctl -u camera-agent -f

# Просмотр файлов логов
tail -f /var/log/camera_agent/agent.log

# Уровни логирования
DEBUG - детальная отладочная информация
INFO - общая информация о работе
WARNING - предупреждения
ERROR - ошибки
```

### Проверка соединения

```bash
# Проверка подключения к облачному серверу
ping your-cloud-server.com
telnet your-cloud-server.com 8080

# Проверка WebSocket соединения
wscat -c wss://your-cloud-server.com/agent/test-agent-id
```

### Мониторинг ресурсов

```bash
# Использование CPU и памяти
top -p $(pgrep camera_agent)

# Использование сети
iftop -i eth0

# Использование диска
df -h
du -sh /var/log/camera_agent/
```

## 🚨 Устранение неполадок

### Агент не подключается к серверу

1. **Проверьте конфигурацию:**
   ```bash
   cat /etc/camera_agent/config.json
   ```

2. **Проверьте сетевую доступность:**
   ```bash
   ping your-cloud-server.com
   ```

3. **Проверьте логи:**
   ```bash
   journalctl -u camera-agent --since "1 hour ago"
   ```

### Поток не передается

1. **Проверьте RTSP потоки камеры:**
   ```bash
   ffmpeg -i rtsp://localhost:554/stream1 -t 5 -f null -
   ```

2. **Проверьте права доступа:**
   ```bash
   ls -la /usr/bin/camera_agent
   ```

### Высокое использование ресурсов

1. **Уменьшите качество потока:**
   ```json
   {
     "streaming": {
       "quality": "medium"  // вместо "high"
     }
   }
   ```

2. **Уменьшите размер буфера:**
   ```json
   {
     "streaming": {
       "buffer_size": 1048576  // 1MB вместо 2MB
     }
   }
   ```

## 📚 Дополнительные ресурсы

- [API документация](api.md)
- [Облачный сервер](cloud-server.md)
- [Примеры интеграции](integration.md)
- [FAQ](faq.md)


