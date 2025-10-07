# Анализ прошивки Flussonic Agent для Dahua

## 📦 Что мы нашли в прошивке

### Структура прошивки Dahua с Flussonic Agent:

```
TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin (30MB)
│
├── hwid (6.8KB)                    # Идентификатор оборудования
├── Install (367B)                  # Скрипт установки
├── kernel.img (2.5MB)              # Ядро Linux
├── dhboot.bin.img (314KB)          # Загрузчик
├── dhboot-min.bin.img (1.6MB)      # Минимальный загрузчик
├── romfs-x.squashfs.img (19.7MB)   # ⭐ Основная ФС (здесь агент)
├── web-x.squashfs.img (7.4MB)      # Веб-интерфейс
├── partition-x.cramfs.img (8.6KB)  # Конфигурация
├── check.img (7.6KB)               # Контрольная сумма
└── sign.img (128B)                 # Цифровая подпись
```

### Процесс установки (из Install скрипта):

```json
{
   "Commands" : [
      "burn partition-x.cramfs.img partition",
      "burn kernel.img kernel",
      "burn romfs-x.squashfs.img rootfs",
      "burn web-x.squashfs.img web",
      "burn dhboot.bin.img bootloader",
      "burn dhboot-min.bin.img mini-boot"
   ]
}
```

## 🔍 Ключевые выводы

### 1. **Формат прошивки**
- Прошивка Dahua использует ZIP архив с сигнатурой `DH`
- Основная ФС в SquashFS формате (read-only)
- Веб-интерфейс в отдельном SquashFS

### 2. **Flussonic Agent расположение**
- Агент находится в `romfs-x.squashfs.img` (19.7MB)
- Вероятные пути:
  - `/usr/bin/flussonic-agent`
  - `/opt/flussonic/agent`
  - `/etc/init.d/flussonic-agent`

### 3. **Архитектура**
- **Платформа**: Linux ARM
- **Чипсет**: Mstar 327DE
- **Архитектура**: ARMv7
- **ФС**: SquashFS (read-only) + CRAMFS

## 🎯 Как работает Flussonic Agent (наша гипотеза)

### На основе анализа прошивки:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DAHUA КАМЕРА                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Камера ФВ     │  │ Flussonic Agent │  │   SquashFS ФС   │ │
│  │   (встроенная)  │◄─┤   (бинарник)    │─►│   (read-only)   │ │
│  │                 │  │                 │  │                 │ │
│  │ - RTSP Server   │  │ - Tunnel client │  │ - /usr/bin/     │ │
│  │ - H.264/H.265   │  │ - P2P support   │  │ - /etc/         │ │
│  │ - Local access  │  │ - Auto-start    │  │ - /opt/         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Процесс работы:

1. **При загрузке камеры:**
   ```
   Systemd/init.d → Запуск Flussonic Agent
   ```

2. **Агент инициализируется:**
   ```
   - Загрузка конфигурации из /etc/ или /mnt/mtd/
   - Определение локального RTSP потока
   - Подключение к Flussonic Watcher серверу
   ```

3. **Создание туннеля:**
   ```
   - WebSocket соединение к серверу
   - Регистрация с уникальным ID
   - Создание TCP туннеля для RTSP
   ```

4. **На сервере:**
   ```
   - Камера доступна как 127.0.0.1:8554
   - Flussonic Watcher подключается локально
   - Прозрачная работа с RTSP
   ```

## 🔧 Что нужно для полного анализа

### Инструменты Linux/WSL:

```bash
# В WSL/Linux
sudo apt-get install squashfs-tools binutils file strings

# Распаковка SquashFS
unsquashfs romfs-x.squashfs.img

# Результат в squashfs-root/
cd squashfs-root/

# Поиск Flussonic Agent
find . -name "*flussonic*" -o -name "*agent*"
find . -type f -executable | xargs file | grep ELF

# Анализ бинарника
file /path/to/agent
strings /path/to/agent | grep -i "tunnel\|websocket\|p2p"
objdump -d /path/to/agent > agent_disasm.txt
```

## 📋 Что искать в распакованной ФС

### 1. **Исполняемый файл агента:**
```bash
find . -name "*agent*" -type f -executable
```

### 2. **Конфигурационные файлы:**
```bash
find . -name "*.json" -o -name "*.conf" | grep -i flussonic
```

### 3. **Startup скрипты:**
```bash
find ./etc/init.d/ -name "*flussonic*"
find ./etc/systemd/system/ -name "*agent*"
```

### 4. **Библиотеки:**
```bash
find . -name "*.so" | grep -i "tunnel\|flussonic"
```

## 🚀 Применение находок к нашему агенту

### После распаковки и анализа:

1. **Структура бинарника:**
   - Изучить зависимости агента
   - Понять протокол соединения
   - Найти конфигурационные параметры

2. **Протокол туннеля:**
   - Понять формат сообщений
   - Изучить heartbeat протокол
   - Определить команды управления

3. **Интеграция с камерой:**
   - Как агент получает RTSP поток
   - Как определяет параметры камеры
   - Автозапуск при загрузке

4. **Обновление нашего агента:**
   - Реализовать аналогичный протокол
   - Добавить совместимость с Flussonic
   - Улучшить стабильность

## 📝 Рекомендации

### Для полного reverse engineering:

1. **Установите WSL**:
   ```powershell
   wsl --install
   ```

2. **Установите инструменты**:
   ```bash
   sudo apt-get update
   sudo apt-get install squashfs-tools binutils file
   ```

3. **Распакуйте SquashFS**:
   ```bash
   cd /mnt/c/Users/King/Desktop/Dahua/firmware_extracted/manual_extract
   unsquashfs romfs-x.squashfs.img
   ```

4. **Анализируйте**:
   ```bash
   cd squashfs-root
   find . -name "*agent*"
   strings agent_binary > analysis.txt
   ```

### Альтернатива:

Используйте онлайн инструменты или Linux LiveUSB для распаковки и анализа.

## 🎯 Следующие шаги

1. **Распаковать SquashFS** в Linux/WSL
2. **Найти исполняемый файл** Flussonic Agent
3. **Проанализировать strings** для понимания протокола
4. **Изучить конфигурацию** агента
5. **Обновить наш агент** на основе находок
6. **Создать совместимую** реализацию

---

**Примечание**: Reverse engineering должен выполняться в соответствии с лицензионными соглашениями и только для образовательных целей и совместимости.
