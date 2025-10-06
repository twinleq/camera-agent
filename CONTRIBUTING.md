# Руководство по участию в разработке

Спасибо за интерес к проекту Camera Agent Firmware! Мы приветствуем участие в разработке от всех желающих.

## 🎯 Как принять участие

### 1. Сообщить о проблеме
- Используйте [GitHub Issues](https://github.com/twinleq/camera-agent/issues)
- Опишите проблему подробно
- Приложите логи и скриншоты если возможно

### 2. Предложить новую функцию
- Создайте [Issue](https://github.com/twinleq/camera-agent/issues) с тегом "enhancement"
- Опишите предложение подробно
- Обсудите с командой перед началом разработки

### 3. Внести изменения в код
- Fork репозиторий
- Создайте feature branch
- Внесите изменения
- Создайте Pull Request

## 🔧 Процесс разработки

### Установка для разработки

```bash
# Клонирование репозитория
git clone https://github.com/twinleq/camera-agent.git
cd camera-agent

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки
pip install -r requirements-dev.txt
```

### Структура проекта

```
camera-agent/
├── agent/                 # Код агента для встраивания
│   ├── core/             # Основная логика
│   ├── platform/         # Платформо-специфичный код
│   ├── streaming/        # Обработка потоков
│   └── networking/       # Сетевое взаимодействие
├── tools/                # Инструменты сборки
├── firmware/             # Созданные прошивки
├── docs/                 # Документация
├── example/              # Примеры использования
└── tests/                # Тесты
```

### Создание Pull Request

1. **Fork** репозиторий на GitHub
2. **Clone** ваш fork локально
3. Создайте **feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. Внесите изменения и **commit**:
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```
5. **Push** в ваш fork:
   ```bash
   git push origin feature/amazing-feature
   ```
6. Создайте **Pull Request** на GitHub

### Требования к коду

- **Python 3.8+** - основной язык
- **PEP 8** - стиль кодирования
- **Type hints** - типизация
- **Docstrings** - документация функций
- **Тесты** - покрытие тестами

### Тестирование

```bash
# Запуск всех тестов
python -m pytest

# Запуск с покрытием
python -m pytest --cov=agent

# Запуск конкретного теста
python -m pytest tests/test_agent.py::test_agent_start
```

## 📋 Стандарты кодирования

### Python

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Пример функции с документацией.
    
    Args:
        param1: Описание параметра
        param2: Описание параметра с значением по умолчанию
        
    Returns:
        Описание возвращаемого значения
        
    Raises:
        ValueError: Когда что-то не так
    """
    if not param1:
        raise ValueError("param1 не может быть пустым")
    
    return True
```

### Commit сообщения

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: добавлена поддержка новой модели камеры
fix: исправлена ошибка подключения к туннелю
docs: обновлена документация по установке
test: добавлены тесты для StreamProcessor
refactor: рефакторинг TunnelConnection
```

### Типы commit'ов:
- `feat` - новая функция
- `fix` - исправление ошибки
- `docs` - изменения в документации
- `style` - форматирование кода
- `refactor` - рефакторинг
- `test` - добавление тестов
- `chore` - обновление зависимостей

## 🎯 Области для участия

### Приоритетные задачи

1. **Поддержка новых камер**
   - Hikvision DS-2CD2xxx
   - Axis M30xx
   - Другие модели

2. **Улучшение туннельной архитектуры**
   - Оптимизация производительности
   - Улучшение стабильности
   - Поддержка множественных туннелей

3. **Документация**
   - Перевод на английский
   - Видео-туториалы
   - Примеры интеграции

4. **Тестирование**
   - Unit тесты
   - Integration тесты
   - Тесты на реальном оборудовании

### Начинающим разработчикам

1. **Исправление документации**
   - Опечатки в README
   - Улучшение примеров
   - Добавление комментариев

2. **Простая функциональность**
   - Логирование
   - Конфигурация
   - Валидация

3. **Тестирование**
   - Написание тестов
   - Отчеты об ошибках
   - Предложения по улучшению

## 🔧 Инструменты разработки

### Рекомендуемые IDE
- **VS Code** с Python расширением
- **PyCharm** Community/Professional
- **Vim/Neovim** с Python плагинами

### Полезные расширения VS Code
- Python
- Python Docstring Generator
- GitLens
- Python Test Explorer

### Линтеры и форматтеры
```bash
# Установка
pip install black flake8 mypy

# Форматирование кода
black agent/ tools/

# Проверка стиля
flake8 agent/ tools/

# Проверка типов
mypy agent/ tools/
```

## 📞 Связь с командой

### GitHub
- **Issues** - [Сообщить о проблеме](https://github.com/twinleq/camera-agent/issues)
- **Discussions** - [Обсуждения](https://github.com/twinleq/camera-agent/discussions)
- **Pull Requests** - [Предложить изменения](https://github.com/twinleq/camera-agent/pulls)

### Процесс обзора кода

1. **Автоматические проверки** - CI/CD
2. **Ревью кода** - минимум 1 одобрение
3. **Тестирование** - все тесты должны проходить
4. **Документация** - обновить при необходимости

### Время ответа
- **Issues** - в течение 48 часов
- **Pull Requests** - в течение 72 часов
- **Вопросы** - в течение 24 часов

## 🎉 Признание участников

Все участники будут упомянуты в:
- **README.md** - раздел Contributors
- **Release notes** - при релизах
- **GitHub** - автоматически в Insights

## 📄 Лицензия

Участвуя в проекте, вы соглашаетесь с [MIT License](LICENSE).

---

**Спасибо за участие в разработке Camera Agent Firmware! 🚀**
