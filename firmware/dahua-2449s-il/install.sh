#!/bin/sh
# ������ ��������� Camera Agent ��� dahua-2449s-il

set -e

        echo "[INSTALL] ��������� Camera Agent ��� dahua-2449s-il..."

# �������� ����������
mkdir -p /usr/bin
mkdir -p /etc/camera_agent
mkdir -p /var/log/camera_agent

# ����������� ������
cp camera_agent /usr/bin/
cp config.json /etc/camera_agent/
cp agent/* /usr/bin/ -r

# ��������� ����
chmod +x /usr/bin/camera_agent
chmod 644 /etc/camera_agent/config.json

# �������� systemd �������
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

# ��������� �������
systemctl daemon-reload
systemctl enable camera-agent

echo "[SUCCESS] Camera Agent ���������� �������!"
echo "[INFO] �������������� /etc/camera_agent/config.json ����� ��������"
echo "[START] ������: systemctl start camera-agent"
