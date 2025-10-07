# Образцы прошивок для анализа

## 📦 Файлы прошивки Dahua с Flussonic Agent

### Файлы в этой директории:

1. **TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin** (30MB)
   - Полная прошивка Dahua с Flussonic Agent
   - Модель: IPC-HX2XXX серия
   - Чипсет: Mstar 327DE
   - Дата: 28.09.2021

2. **web-x.squashfs.bin** (7.4MB)
   - Веб-интерфейс камеры
   - SquashFS файловая система

3. **README.txt**
   - Список поддерживаемых устройств

## 🚀 Анализ на Linux

### Скачайте файлы на Linux VM:

```bash
# Клонируйте репозиторий
git clone https://github.com/twinleq/camera-agent.git
cd camera-agent

# Переключитесь на ветку анализа
git checkout firmware-analysis

# Перейдите в директорию с прошивками
cd firmware-samples

# Проверьте файлы
ls -lh
```

### Быстрый старт анализа:

```bash
# Извлечение прошивки
binwalk -e TEMP_DH_IPC-HX2XXX-Molec_MultiLang_PN_V2.820.1015003.0.T.210928.bin

# Распаковка SquashFS
cd _*extracted/
unsquashfs romfs-x.squashfs.img

# Поиск агента
cd squashfs-root/
find . -name "*agent*" -o -name "*flussonic*"
```

## 📋 Детальная инструкция

См. **[LINUX_ANALYSIS_GUIDE.md](../LINUX_ANALYSIS_GUIDE.md)** для полной пошаговой инструкции.

См. **[QUICK_COMMANDS.md](../QUICK_COMMANDS.md)** для быстрых команд.

## 🎯 Цель анализа

1. Найти исполняемый файл Flussonic Agent
2. Изучить протокол туннеля
3. Понять формат конфигурации
4. Улучшить наш агент на основе находок

## ⚠️ Важно

Эти файлы используются только для:
- Образовательных целей
- Изучения протокола
- Обеспечения совместимости
- Reverse engineering в рамках fair use

Не распространяйте прошивку без разрешения Dahua/Flussonic.
