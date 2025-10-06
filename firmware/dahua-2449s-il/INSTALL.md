# Установка Camera Agent для Dahua IPC-HFW2449S-S-IL

## Технические характеристики камеры

- **Модель**: Dahua IPC-HFW2449S-S-IL
- **Разрешение**: 4MP (2688×1520)
- **Кодек**: H.265
- **Платформа**: Linux ARM
- **RTSP порт**: 554
- **HTTP порт**: 80
- **Потоки**: 
  - Основной: `/cam/realmonitor?channel=1&subtype=0`
  - Подпоток: `/cam/realmonitor?channel=1&subtype=1`

## Предварительные требования

1. **Доступ к камере**:
   - IP адрес камеры в сети
   - Логин и пароль администратора
   - Доступ по SSH (если включен)

2. **Сетевые настройки**:
   - Камера должна иметь доступ к интернету
   - Порты 8080 (облачный сервер) должны быть доступны

## Способы установки

### Способ 1: Через веб-интерфейс (Рекомендуемый)

1. **Откройте веб-интерфейс камеры**:
   ```
   http://192.168.1.100 (замените на IP вашей камеры)
   ```

2. **Войдите в систему**:
   - Логин: `admin` (по умолчанию)
   - Пароль: `admin` (по умолчанию)

3. **Перейдите в раздел обновления**:
   - `System` → `Maintenance` → `Upgrade`

4. **Загрузите прошивку**:
   - Выберите файл `dahua-2449s-il_firmware.tar.gz`
   - Нажмите `Upgrade`

5. **Дождитесь перезагрузки камеры**

### Способ 2: Через SSH (если доступен)

1. **Подключитесь к камере по SSH**:
   ```bash
   ssh admin@192.168.1.100
   ```

2. **Скопируйте файл прошивки**:
   ```bash
   scp dahua-2449s-il_firmware.tar.gz admin@192.168.1.100:/tmp/
   ```

3. **Установите агент**:
   ```bash
   cd /tmp
   tar -xzf dahua-2449s-il_firmware.tar.gz
   chmod +x install.sh
   ./install.sh
   ```

### Способ 3: Через TFTP

1. **Настройте TFTP сервер**:
   ```bash
   sudo apt-get install tftpd-hpa
   sudo cp dahua-2449s-il_firmware.tar.gz /srv/tftp/
   ```

2. **Загрузите через TFTP на камере**:
   ```bash
   tftp -g -r dahua-2449s-il_firmware.tar.gz 192.168.1.10
   ```

## Настройка конфигурации

1. **Отредактируйте конфигурацию**:
   ```bash
   nano /etc/camera_agent/config.json
   ```

2. **Укажите параметры**:
   ```json
   {
     "agent": {
       "agent_id": "dahua-2449s-il-001",
       "cloud_server_url": "ws://your-server.com:8080/agent",
       "cloud_server_token": "your-secret-token"
     }
   }
   ```

3. **Настройте потоки** (опционально):
   ```json
   {
     "streaming": {
       "quality": "high",
       "max_resolution": "2688x1520",
       "max_fps": 20
     }
   }
   ```

## Запуск агента

1. **Запустите сервис**:
   ```bash
   systemctl start camera-agent
   ```

2. **Включите автозапуск**:
   ```bash
   systemctl enable camera-agent
   ```

3. **Проверьте статус**:
   ```bash
   systemctl status camera-agent
   ```

## Проверка работы

1. **Проверьте логи**:
   ```bash
   journalctl -u camera-agent -f
   ```

2. **Проверьте подключение к облачному серверу**:
   ```bash
   curl http://your-server.com:8080/agents
   ```

3. **Проверьте RTSP потоки**:
   ```bash
   ffmpeg -i rtsp://192.168.1.100:554/cam/realmonitor?channel=1&subtype=0 -t 5 -f null -
   ```

## Управление агентом

### Команды systemctl:
```bash
# Запуск
systemctl start camera-agent

# Остановка
systemctl stop camera-agent

# Перезапуск
systemctl restart camera-agent

# Статус
systemctl status camera-agent

# Логи
journalctl -u camera-agent -f
```

### Через облачный сервер:
```bash
# Получение статуса агента
curl http://your-server.com:8080/agents/dahua-2449s-il-001

# Отправка команды агенту
curl -X POST http://your-server.com:8080/agents/dahua-2449s-il-001/control \
  -H "Content-Type: application/json" \
  -d '{"command": "restart"}'
```

## Устранение неполадок

### Агент не запускается

1. **Проверьте конфигурацию**:
   ```bash
   cat /etc/camera_agent/config.json | python -m json.tool
   ```

2. **Проверьте права доступа**:
   ```bash
   ls -la /usr/bin/camera_agent
   chmod +x /usr/bin/camera_agent
   ```

3. **Проверьте логи**:
   ```bash
   journalctl -u camera-agent --since "1 hour ago"
   ```

### Агент не подключается к серверу

1. **Проверьте сетевую доступность**:
   ```bash
   ping your-server.com
   telnet your-server.com 8080
   ```

2. **Проверьте URL сервера в конфигурации**:
   ```bash
   grep cloud_server_url /etc/camera_agent/config.json
   ```

3. **Проверьте токен**:
   ```bash
   grep cloud_server_token /etc/camera_agent/config.json
   ```

### Потоки не передаются

1. **Проверьте RTSP сервер камеры**:
   ```bash
   netstat -tlnp | grep 554
   ```

2. **Проверьте потоки вручную**:
   ```bash
   ffmpeg -i rtsp://localhost:554/cam/realmonitor?channel=1&subtype=0 -t 5 -f null -
   ```

3. **Проверьте настройки потоков в конфигурации**:
   ```bash
   grep stream_paths /etc/camera_agent/config.json
   ```

## Удаление агента

```bash
# Остановка сервиса
systemctl stop camera-agent
systemctl disable camera-agent

# Удаление файлов
./uninstall.sh

# Или вручную:
rm -f /usr/bin/camera_agent
rm -rf /etc/camera_agent
rm -rf /var/log/camera_agent
rm -f /etc/systemd/system/camera-agent.service
systemctl daemon-reload
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `journalctl -u camera-agent -f`
2. Проверьте конфигурацию: `/etc/camera_agent/config.json`
3. Проверьте сетевую доступность
4. Обратитесь в службу поддержки с логами

