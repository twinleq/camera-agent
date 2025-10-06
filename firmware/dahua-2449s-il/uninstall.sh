#!/bin/sh
# Скрипт удаления Camera Agent

        echo "[UNINSTALL] Удаление Camera Agent..."

# Остановка сервиса
systemctl stop camera-agent 2>/dev/null || true
systemctl disable camera-agent 2>/dev/null || true

# Удаление файлов
rm -f /usr/bin/camera_agent
rm -rf /etc/camera_agent
rm -rf /var/log/camera_agent
rm -f /etc/systemd/system/camera-agent.service

# Перезагрузка systemd
systemctl daemon-reload

echo "[SUCCESS] Camera Agent удален"
