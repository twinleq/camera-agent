# Быстрые команды для анализа прошивки

## ⚡ Копируйте и вставляйте по порядку

### ШАГ 1: Установка инструментов
```bash
sudo apt-get update && sudo apt-get install -y squashfs-tools binutils file binwalk unzip python3 tree
```

### ШАГ 2: Создание рабочей директории
```bash
mkdir -p ~/firmware_analysis && cd ~/firmware_analysis
```

### ШАГ 3: Копирование файлов (замените пути)
```bash
# Если файлы в общей папке:
cp /mnt/shared/Dahua/*.bin .
cp /mnt/shared/Dahua/*.squashfs.bin .
ls -lh
```

### ШАГ 4: Автоматическое извлечение
```bash
binwalk -e TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin
ls -lh _TEMP*extracted/
```

### ШАГ 5: Распаковка SquashFS
```bash
cd _TEMP*extracted/
unsquashfs romfs-x.squashfs.img
cd squashfs-root/
pwd
```

### ШАГ 6: Поиск агента
```bash
find . -iname "*flussonic*" -o -iname "*agent*" | grep -v ".git"
find . -type f -executable | head -20
ls -la ./usr/bin/ | grep -i agent
ls -la ./usr/sbin/ | grep -i agent
```

### ШАГ 7: Анализ найденного файла агента
```bash
# Замените /path/to/agent на найденный путь
AGENT_PATH="/usr/bin/flussonic-agent"

file $AGENT_PATH
ls -lh $AGENT_PATH
ldd $AGENT_PATH
strings $AGENT_PATH > ~/agent_strings.txt
head -50 ~/agent_strings.txt
```

### ШАГ 8: Поиск конфигурации
```bash
find . -name "*.json" | head -20
find ./etc -name "*flussonic*" -o -name "*agent*"
cat ./etc/flussonic/config.json 2>/dev/null || echo "Не найден"
```

### ШАГ 9: Поиск startup скриптов
```bash
find ./etc/init.d -name "*agent*" -o -name "*flussonic*"
cat ./etc/init.d/*agent* 2>/dev/null
find ./etc/systemd -name "*agent*"
```

### ШАГ 10: Ключевые строки из агента
```bash
# Протоколы и URL
grep -E "ws://|wss://|http://|rtsp://" ~/agent_strings.txt | head -20

# Параметры туннеля
grep -iE "tunnel|port|server|host" ~/agent_strings.txt | head -30

# P2P строки
grep -iE "p2p|stun|turn|ice" ~/agent_strings.txt | head -20

# Конфигурация
grep -E "config|\.json|\.conf|/etc/|/mnt/" ~/agent_strings.txt | head -30

# Лог сообщения
grep -iE "start|connect|fail|error" ~/agent_strings.txt | head -30
```

---

## 📤 Отправьте мне после КАЖДОГО шага:

1. **Вывод команды**
2. **Любые ошибки**
3. **Что нашли**

## 🎯 Самые важные команды для копирования:

```bash
# ВСЕ В ОДНОМ (выполните последовательно):
cd ~/firmware_analysis
binwalk -e *.bin
cd _*extracted/
unsquashfs romfs-x.squashfs.img
cd squashfs-root/
find . -name "*agent*" -o -name "*flussonic*"
```

---

## 🔍 Что искать:

- ✅ Бинарный файл агента
- ✅ Конфигурационные файлы (.json, .conf)
- ✅ Startup скрипты (init.d, systemd)
- ✅ Библиотеки (.so)
- ✅ Логи и документация

Начинайте! 🚀
