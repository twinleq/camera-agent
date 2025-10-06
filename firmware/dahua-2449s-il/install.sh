#!/bin/sh
# Скрипт установки Camera Agent для dahua-2449s-il

set -e

        echo "[INSTALL] Установка Camera Agent для dahua-2449s-il..."

# Создание директорий
mkdir -p /usr/bin
mkdir -p /etc/camera_agent
mkdir -p /var/log/camera_agent

# Копирование файлов
cp camera_agent /usr/bin/
cp config.json /etc/camera_agent/
cp agent/* /usr/bin/ -r

# Установка прав
chmod +x /usr/bin/camera_agent
chmod 644 /etc/camera_agent/config.json

# Создание systemd сервиса
cat > /etc/systemd/system/camera-agent.service << EOF
[Unit]
Description=Camera Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/camera_agent
Restart=always
RestartSec=10
WorkingDirectory=/usr/bin
Environment=PYTHONPATH=/usr/bin

[Install]
WantedBy=multi-user.target
EOF

# Включение сервиса
systemctl daemon-reload
systemctl enable camera-agent

echo "[SUCCESS] Camera Agent установлен успешно!"
echo "[INFO] Отредактируйте /etc/camera_agent/config.json перед запуском"
echo "[START] Запуск: systemctl start camera-agent"
