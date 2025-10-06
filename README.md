# Camera Agent Firmware

[![GitHub](https://img.shields.io/github/license/twinleq/camera-agent)](https://github.com/twinleq/camera-agent/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20arm-lightgrey.svg)](https://en.wikipedia.org/wiki/ARM_architecture)

## 🎯 Что это такое?

**Camera Agent Firmware** - это решение для встраивания агентов в прошивку IP-камер, аналогичное [Flussonic Agent](https://flussonic.ru/doc/agent-with-watcher/). Агент создает **туннель** между камерой и сервером, делая камеру доступной как локальное устройство.

## 🔍 Проблема и решение

### ❌ Проблема (обычная схема):
```
Облачный сервер → NAT/Firewall → IP-камера (недоступна)
```

### ✅ Решение (с Camera Agent - туннельная архитектура):
```
IP-камера + Agent → NAT/Firewall → Туннельный сервер → Flussonic Watcher
                     ↓
              Камера доступна как 127.0.0.1 на сервере
```

## 🚀 Быстрый старт

### 1. Создание прошивки для камеры
```bash
# Клонирование репозитория
git clone https://github.com/twinleq/camera-agent.git
cd camera-agent

# Создание прошивки для Dahua IPC-HFW2449S-S-IL
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

### 2. Установка на камеру
```bash
# Загрузка через веб-интерфейс камеры
# System → Maintenance → Upgrade
# Файл: dahua-2449s-il_firmware.tar.gz
```

### 3. Настройка Flussonic Watcher
```bash
# В Flussonic Watcher добавить камеру:
# RTSP URL: rtsp://127.0.0.1:8554/cam/realmonitor?channel=1&subtype=0
# Username: admin
# Password: admin
```

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    IP-КАМЕРА (Edge Device)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   RTSP Server   │  │  Camera Agent   │  │   Туннель       │ │
│  │ (127.0.0.1:554) │◄─┤   (наш код)     │─►│   Клиент        │ │
│  │                 │  │                 │  │                 │ │
│  │ - H.264/H.265   │  │ - WebSocket     │  │ - TCP туннель   │ │
│  │ - Multiple      │  │ - Туннель       │  │ - Прозрачность  │ │
│  │   Streams       │  │ - Heartbeat     │  │ - NAT traversal │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ WebSocket + TCP Tunnel
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ТУННЕЛЬНЫЙ СЕРВЕР                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   WebSocket     │  │   TCP Tunnel    │  │   Local RTSP    │ │
│  │   Server        │◄─┤   Server        │─►│   Proxy         │ │
│  │                 │  │                 │  │                 │ │
│  │ - Прием агентов │  │ - TCP туннель   │  │ - 127.0.0.1:8554│ │
│  │ - Управление    │  │ - Прозрачность  │  │ - RTSP прокси   │ │
│  │ - Мониторинг    │  │ - NAT traversal │  │ - Flussonic API │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FLUSSONIC WATCHER                            │
│  - Подключение к 127.0.0.1:8554 (локально)                     │
│  - Работает как с локальной камерой                             │
│  - Полная прозрачность туннеля                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Поддерживаемые камеры

| Модель | Платформа | Архитектура | Статус |
|--------|-----------|-------------|--------|
| **Dahua** | IPC-HFW2449S-S-IL | Linux ARM | ✅ Поддерживается |
| **Hikvision** | DS-2CD2xxx | Linux ARM | 🔄 В разработке |
| **Axis** | M30xx | Linux ARM | 🔄 В разработке |

## 📖 Документация

- **[TUNNEL_ARCHITECTURE.md](TUNNEL_ARCHITECTURE.md)** - Подробная архитектура туннелей
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Полное описание проекта
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Руководство по установке
- **[DHCP_WORKFLOW.md](DHCP_WORKFLOW.md)** - Работа с DHCP
- **[QUICKSTART_SIMPLE.md](QUICKSTART_SIMPLE.md)** - Быстрый старт

## 🎯 Особенности

### ✅ Туннельная архитектура
- Агент создает туннель до туннельного сервера
- Камера становится доступна как `127.0.0.1:8554` на сервере
- Flussonic Watcher видит камеру как локальную

### ✅ NAT Traversal
- Агент инициирует исходящее соединение
- Роутер пропускает исходящий трафик
- Не нужен проброс портов

### ✅ DHCP поддержка
- Автоматическое определение IP камеры
- Работа с любым IP, полученным от DHCP
- Автоматическое переподключение при смене IP

### ✅ Безопасность
- Шифрованное соединение
- Нет открытых портов
- Токен авторизации

## 🚀 Преимущества

### По сравнению с обычным подходом:
1. **NAT Traversal** - не нужен проброс портов
2. **Стабильность** - автоматическое переподключение
3. **Буферизация** - нет потери данных при сбоях
4. **Масштабируемость** - централизованное управление
5. **Безопасность** - шифрованное соединение

### По сравнению с Flussonic Agent:
1. **Открытый код** - полная кастомизация
2. **Модульность** - легко расширять функциональность
3. **Гибкость** - поддержка разных протоколов
4. **Документация** - подробные инструкции

## 🔧 Установка

### Предварительные требования
- Python 3.8+
- Git
- IP-камера с Linux (ARM/x86)

### Быстрая установка
```bash
# Клонирование
git clone https://github.com/twinleq/camera-agent.git
cd camera-agent

# Установка зависимостей
pip install -r requirements.txt

# Создание прошивки
python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il
```

## 📊 Мониторинг

### API агента
```bash
# Статус агента
curl http://localhost:8080/agents/dahua-2449s-il-001

# Управление агентом
curl -X POST http://localhost:8080/agents/dahua-2449s-il-001/control \
  -H "Content-Type: application/json" \
  -d '{"command": "restart"}'
```

### Логи
```bash
# На камере
journalctl -u camera-agent -f

# На сервере
tail -f tunnel-server/logs/server.log
```

## 🤝 Участие в разработке

Мы приветствуем участие в разработке! Пожалуйста:

1. **Fork** репозиторий
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Откройте **Pull Request**

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.


## 🙏 Благодарности

- [Flussonic](https://flussonic.ru/) за вдохновение архитектурой Agent
- Сообщество разработчиков видеонаблюдения
- Всем участникам проекта

---

**Создано по образцу [Flussonic Agent](https://flussonic.ru/doc/agent-with-watcher/) для сообщества видеонаблюдения**

⭐ **Если проект полезен, поставьте звезду!**
