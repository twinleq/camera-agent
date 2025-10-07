# Пошаговая инструкция по анализу прошивки Flussonic Agent на Linux

## 🎯 Цель

Извлечь и проанализировать Flussonic Agent из прошивки Dahua для понимания его работы и улучшения нашего агента.

## 📋 Шаг 1: Подготовка Linux окружения

### Установите необходимые инструменты:

```bash
# Обновление системы
sudo apt-get update
sudo apt-get upgrade -y

# Установка инструментов для анализа
sudo apt-get install -y \
    squashfs-tools \
    binutils \
    file \
    binwalk \
    unzip \
    python3 \
    python3-pip \
    hexdump \
    tree \
    vim \
    git

# Проверка установки
which unsquashfs
which binwalk
which strings
```

**Отправьте мне вывод:**
```
unsquashfs -v
binwalk --help
```

---

## 📋 Шаг 2: Копирование файлов прошивки

### Перенесите файлы на Linux VM:

**Вариант A: Через общую папку VirtualBox/VMware**
```bash
# Создайте рабочую директорию
mkdir -p ~/firmware_analysis
cd ~/firmware_analysis

# Скопируйте файлы из общей папки
cp /mnt/shared/Dahua/*.bin .
cp /mnt/shared/Dahua/*.squashfs.bin .
```

**Вариант B: Через SCP**
```bash
# На Windows (если есть SSH на Linux VM)
scp C:\Users\King\Desktop\Dahua\*.bin user@linux-vm-ip:~/firmware_analysis/
```

**Вариант C: Скачать напрямую из Windows**
```bash
# Если есть HTTP сервер на Windows
wget http://windows-ip/firmware.bin
```

### Проверьте наличие файлов:

```bash
cd ~/firmware_analysis
ls -lh
```

**Отправьте мне вывод команды `ls -lh`**

---

## 📋 Шаг 3: Извлечение прошивки

### Извлеките ZIP архив из .bin файла:

```bash
# Создайте директорию для извлечения
mkdir -p extracted

# Используем binwalk для автоматического извлечения
binwalk -e TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin

# ИЛИ ручное извлечение ZIP
dd if=TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin of=firmware.zip bs=1 skip=774

# Распакуйте ZIP
unzip firmware.zip -d extracted/

# Проверьте содержимое
ls -lh extracted/
```

**Отправьте мне вывод команды `ls -lh extracted/`**

---

## 📋 Шаг 4: Распаковка SquashFS файловой системы

### Распакуйте основную ФС (romfs-x.squashfs.img):

```bash
cd ~/firmware_analysis/extracted

# Распаковка SquashFS
unsquashfs romfs-x.squashfs.img

# Результат будет в squashfs-root/
cd squashfs-root/

# Просмотр структуры директорий
tree -L 2 | head -50
```

**Отправьте мне вывод команды `tree -L 2 | head -50`**

---

## 📋 Шаг 5: Поиск Flussonic Agent

### Найдите файлы связанные с агентом:

```bash
cd ~/firmware_analysis/extracted/squashfs-root/

# Поиск по именам файлов
find . -iname "*flussonic*" -o -iname "*agent*"

# Поиск исполняемых файлов
find . -type f -executable

# Поиск в /usr/bin и /usr/sbin
ls -la ./usr/bin/ | grep -i "agent\|flussonic"
ls -la ./usr/sbin/ | grep -i "agent\|flussonic"

# Поиск в /opt
ls -la ./opt/ 2>/dev/null

# Поиск конфигурационных файлов
find ./etc -name "*.json" -o -name "*.conf" | head -20
```

**Отправьте мне полный вывод всех команд поиска**

---

## 📋 Шаг 6: Анализ найденных файлов

### Когда найдете агент (предположим /usr/bin/flussonic-agent):

```bash
# Информация о файле
file /path/to/flussonic-agent

# Размер и права
ls -lh /path/to/flussonic-agent

# Зависимости (shared libraries)
ldd /path/to/flussonic-agent

# Извлечение строк из бинарника
strings /path/to/flussonic-agent > flussonic_agent_strings.txt

# Просмотр первых 100 строк
head -100 flussonic_agent_strings.txt
```

**Отправьте мне:**
1. Вывод `file` команды
2. Вывод `ldd` команды  
3. Первые 200 строк из `strings` (содержащие tunnel, websocket, config)

---

## 📋 Шаг 7: Поиск конфигурационных файлов

### Найдите конфигурацию агента:

```bash
# Поиск JSON конфигураций
find . -name "*.json" -exec grep -l "flussonic\|agent\|tunnel" {} \;

# Поиск CONF файлов
find ./etc -name "*.conf" | xargs cat 2>/dev/null

# Поиск в /mnt/mtd/ (часто используется Dahua)
find . -path "*/mnt/mtd/*" -type f

# Содержимое всех JSON файлов
find . -name "*.json" -exec echo "=== {} ===" \; -exec cat {} \; -exec echo "" \;
```

**Отправьте мне все найденные конфигурационные файлы**

---

## 📋 Шаг 8: Анализ startup скриптов

### Найдите скрипты автозапуска:

```bash
# Init.d скрипты
ls -la ./etc/init.d/ | grep -i "agent\|flussonic"
cat ./etc/init.d/flussonic* 2>/dev/null

# Systemd сервисы
find ./etc/systemd -name "*agent*" -o -name "*flussonic*"
cat ./etc/systemd/system/*agent* 2>/dev/null

# RC скрипты
find ./etc/rc* -name "*agent*" -o -name "*flussonic*"
```

**Отправьте мне содержимое всех startup скриптов**

---

## 📋 Шаг 9: Детальный анализ строк

### Найдите ключевые строки в агенте:

```bash
cd ~/firmware_analysis/extracted/squashfs-root/

# Сохраните все строки агента
strings /path/to/flussonic-agent > agent_all_strings.txt

# Поиск URL и протоколов
grep -E "ws://|wss://|http://|https://|tcp://|rtsp://" agent_all_strings.txt

# Поиск параметров туннеля
grep -iE "tunnel|websocket|socket|port|server|host" agent_all_strings.txt | head -50

# Поиск P2P строк
grep -iE "p2p|stun|turn|ice|webrtc" agent_all_strings.txt

# Поиск конфигурационных путей
grep -E "/etc/|/mnt/|/opt/|/var/|\.json|\.conf" agent_all_strings.txt | head -30

# Поиск лог сообщений
grep -iE "starting|started|connected|failed|error|warning|info" agent_all_strings.txt | head -30
```

**Отправьте мне результаты всех grep команд**

---

## 📋 Шаг 10: Сохранение результатов

### Создайте архив с результатами:

```bash
cd ~/firmware_analysis

# Создайте директорию для результатов
mkdir -p analysis_results

# Скопируйте найденные файлы
cp extracted/squashfs-root/path/to/flussonic-agent analysis_results/ 2>/dev/null
cp extracted/Install analysis_results/

# Скопируйте конфигурации
find extracted/squashfs-root -name "*.json" -exec cp {} analysis_results/ \;
find extracted/squashfs-root/etc -name "*.conf" -exec cp {} analysis_results/ \;

# Скопируйте startup скрипты
find extracted/squashfs-root/etc/init.d -name "*agent*" -exec cp {} analysis_results/ \;

# Создайте текстовые отчеты
tree extracted/squashfs-root -L 3 > analysis_results/directory_structure.txt
ls -lR extracted/squashfs-root/usr/bin > analysis_results/binaries_list.txt
ls -lR extracted/squashfs-root/etc > analysis_results/etc_files.txt

# Создайте архив
tar -czf analysis_results.tar.gz analysis_results/

# Размер архива
ls -lh analysis_results.tar.gz
```

**Скопируйте архив обратно на Windows для анализа**

---

## 🔍 Что особенно важно найти:

### Критические компоненты:

1. **Исполняемый файл агента** (`/usr/bin/flussonic-agent`)
2. **Конфигурация** (`/etc/flussonic/config.json`)
3. **Startup скрипт** (`/etc/init.d/flussonic-agent`)
4. **Библиотеки** (`.so` файлы)

### Ключевая информация:

- **Протокол туннеля** - как устанавливается соединение
- **Формат сообщений** - структура данных
- **Heartbeat** - как агент отправляет статус
- **Конфигурационные параметры** - какие настройки есть

---

## 📞 Как отправлять результаты

### Формат отчета:

```
=== ШАГ X: Название шага ===

Команда:
$ команда которую выполнили

Результат:
[вывод команды]

Находки:
- Что нашли
- Важные детали
```

### Что отправлять после каждого шага:

1. **Шаг 1**: Версии установленных инструментов
2. **Шаг 2**: Список скопированных файлов
3. **Шаг 3**: Содержимое extracted/
4. **Шаг 4**: Структура squashfs-root/
5. **Шаг 5**: Все найденные файлы с "agent" или "flussonic"
6. **Шаг 6**: Информация о бинарнике и strings
7. **Шаг 7**: Все конфигурационные файлы
8. **Шаг 8**: Все startup скрипты
9. **Шаг 9**: Ключевые строки из агента
10. **Шаг 10**: Архив с результатами

---

## 🚀 Начинайте с Шага 1!

Подключитесь к Linux VM и выполните команды из **Шага 1**. Отправьте мне результаты, и мы продолжим анализ!
