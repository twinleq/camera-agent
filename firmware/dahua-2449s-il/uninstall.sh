#!/bin/sh
# ������ �������� Camera Agent

        echo "[UNINSTALL] �������� Camera Agent..."

# ��������� �������
systemctl stop camera-agent 2>/dev/null || true
systemctl disable camera-agent 2>/dev/null || true

# �������� ������
rm -f /usr/bin/camera_agent
rm -rf /etc/camera_agent
rm -rf /var/log/camera_agent
rm -f /etc/systemd/system/camera-agent.service

# ������������ systemd
systemctl daemon-reload

echo "[SUCCESS] Camera Agent ������"
