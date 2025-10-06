#!/usr/bin/env python3
"""
Инструмент для сборки агента под конкретную модель IP-камеры
"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any


class CameraAgentBuilder:
    """Сборщик агента для конкретной камеры"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.agent_root = self.project_root / "agent"
        self.firmware_root = self.project_root / "firmware"
        
        # Конфигурации для разных камер
        self.camera_configs = {
            "dahua-2449": {
                "platform": "linux_arm",
                "architecture": "armv7",
                "libc": "uclibc",
                "rtsp_port": 554,
                "http_port": 80,
                "onvif_port": 1000,
                "stream_paths": ["/cam/realmonitor?channel=1&subtype=0"],
                "config_file": "/mnt/mtd/Config/Account1",
                "binary_path": "/usr/bin/camera_agent"
            },
            "dahua-2449s-il": {
                "platform": "linux_arm",
                "architecture": "armv7",
                "libc": "uclibc",
                "rtsp_port": 554,
                "http_port": 80,
                "onvif_port": 1000,
                "stream_paths": [
                    "/cam/realmonitor?channel=1&subtype=0",  # Основной поток
                    "/cam/realmonitor?channel=1&subtype=1"   # Подпоток
                ],
                "config_file": "/mnt/mtd/Config/Account1",
                "binary_path": "/usr/bin/camera_agent",
                "max_resolution": "2688x1520",
                "max_fps": 20,
                "codec": "H.265",
                "features": ["WDR", "3D-DNR", "HLC", "BLC", "Smart Detection"],
                "storage": "MicroSD up to 256GB",
                "power": "12V DC or PoE (802.3af)",
                "protection": "IP67"
            },
            "hikvision-ds2cd": {
                "platform": "linux_arm",
                "architecture": "armv7",
                "libc": "glibc",
                "rtsp_port": 554,
                "http_port": 80,
                "onvif_port": 1000,
                "stream_paths": ["/Streaming/Channels/101"],
                "config_file": "/davinci/account",
                "binary_path": "/usr/bin/camera_agent"
            },
            "axis-m30": {
                "platform": "linux_arm",
                "architecture": "armv7",
                "libc": "glibc",
                "rtsp_port": 554,
                "http_port": 80,
                "onvif_port": 1000,
                "stream_paths": ["/axis-media/media.amp"],
                "config_file": "/etc/persistent/camera_agent.conf",
                "binary_path": "/usr/bin/camera_agent"
            }
        }
    
    def build(self, camera_model: str, output_dir: str, config: Dict[str, Any] = None):
        """Сборка агента для конкретной камеры"""
        
        print(f"[BUILD] Сборка агента для камеры: {camera_model}")
        
        # Проверка поддержки камеры
        if camera_model not in self.camera_configs:
            print(f"[ERROR] Камера {camera_model} не поддерживается")
            print(f"Поддерживаемые модели: {list(self.camera_configs.keys())}")
            return False
        
        camera_config = self.camera_configs[camera_model]
        
        # Создание выходной директории
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Копирование базового кода агента
            print("[STEP 1] Копирование базового кода...")
            self._copy_agent_code(output_path, camera_config)
            
            # 2. Создание платформо-специфичных файлов
            print("[STEP 2] Создание платформо-специфичных файлов...")
            self._create_platform_files(output_path, camera_model, camera_config)
            
            # 3. Создание конфигурационных файлов
            print("[STEP 3] Создание конфигурации...")
            self._create_config_files(output_path, camera_model, camera_config, config)
            
            # 4. Создание скриптов установки
            print("[STEP 4] Создание скриптов установки...")
            self._create_install_scripts(output_path, camera_model, camera_config)
            
            # 5. Создание Makefile для сборки
            print("[STEP 5] Создание Makefile...")
            self._create_makefile(output_path, camera_model, camera_config)
            
            # 6. Создание файла прошивки
            print("[STEP 6] Создание файла прошивки...")
            self._create_firmware_package(output_path, camera_model)
            
            print(f"[SUCCESS] Сборка завершена успешно!")
            print(f"[RESULT] Результат: {output_path}")
            print(f"[FIRMWARE] Файл прошивки: {output_path / f'{camera_model}_firmware.tar.gz'}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка сборки: {e}")
            return False
    
    def _copy_agent_code(self, output_path: Path, camera_config: Dict[str, Any]):
        """Копирование базового кода агента"""
        
        # Создание структуры директорий
        (output_path / "agent" / "core").mkdir(parents=True, exist_ok=True)
        (output_path / "agent" / "platform").mkdir(parents=True, exist_ok=True)
        (output_path / "agent" / "streaming").mkdir(parents=True, exist_ok=True)
        (output_path / "agent" / "networking").mkdir(parents=True, exist_ok=True)
        
        # Копирование базовых файлов
        shutil.copy2(
            self.agent_root / "core" / "agent.py",
            output_path / "agent" / "core"
        )
        
        # Создание __init__.py файлов
        for init_file in [
            output_path / "agent" / "__init__.py",
            output_path / "agent" / "core" / "__init__.py",
            output_path / "agent" / "platform" / "__init__.py",
            output_path / "agent" / "streaming" / "__init__.py",
            output_path / "agent" / "networking" / "__init__.py"
        ]:
            init_file.write_text('')
    
    def _create_platform_files(self, output_path: Path, camera_model: str, 
                              camera_config: Dict[str, Any]):
        """Создание платформо-специфичных файлов"""
        
        platform_file = output_path / "agent" / "platform" / "platform_specific.py"
        
        platform_code = f'''
"""
Платформо-специфичный код для {camera_model}
"""

import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PlatformSpecific:
    """Класс для работы с конкретной платформой камеры"""
    
    def __init__(self):
        self.camera_model = "{camera_model}"
        self.config = {camera_config}
    
    async def init_camera_interface(self):
        """Инициализация интерфейса камеры"""
        logger.info(f"Инициализация интерфейса камеры {{self.camera_model}}")
        
        # Настройка RTSP сервера камеры
        await self._configure_rtsp_server()
        
        # Проверка доступности потоков
        await self._check_stream_availability()
    
    async def init_network_stack(self):
        """Инициализация сетевого стека"""
        logger.info("Инициализация сетевого стека")
        
        # Настройка сетевых интерфейсов
        await self._configure_network_interfaces()
        
        # Настройка firewall
        await self._configure_firewall()
    
    async def _configure_rtsp_server(self):
        """Настройка RTSP сервера"""
        try:
            # Команды для настройки RTSP сервера на камере
            rtsp_commands = [
                "echo 'RTSP сервер настроен'",
                # Добавить реальные команды для конкретной камеры
            ]
            
            for cmd in rtsp_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True)
                if result.returncode != 0:
                    logger.warning(f"Команда {{cmd}} завершилась с ошибкой")
                    
        except Exception as e:
            logger.error(f"Ошибка настройки RTSP сервера: {{e}}")
    
    async def _check_stream_availability(self):
        """Проверка доступности потоков"""
        stream_paths = self.config.get("stream_paths", [])
        
        for path in stream_paths:
            rtsp_url = f"rtsp://localhost{{self.config['rtsp_port']}}{{path}}"
            logger.info(f"Проверка потока: {{rtsp_url}}")
            # TODO: Реализовать проверку доступности потока
    
    async def _configure_network_interfaces(self):
        """Настройка сетевых интерфейсов"""
        # TODO: Реализовать настройку сетевых интерфейсов
        pass
    
    async def _configure_firewall(self):
        """Настройка firewall"""
        # TODO: Реализовать настройку firewall
        pass
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Получение информации о камере"""
        return {{
            "model": self.camera_model,
            "platform": self.config.get("platform"),
            "architecture": self.config.get("architecture"),
            "rtsp_port": self.config.get("rtsp_port"),
            "http_port": self.config.get("http_port")
        }}

# Глобальный экземпляр
platform_specific = PlatformSpecific()
'''
        
        platform_file.write_text(platform_code)
    
    def _create_config_files(self, output_path: Path, camera_model: str,
                           camera_config: Dict[str, Any], user_config: Dict[str, Any] = None):
        """Создание конфигурационных файлов"""
        
        # Основная конфигурация
        config_data = {
            "camera": {
                "model": camera_model,
                "platform": camera_config["platform"],
                "architecture": camera_config["architecture"]
            },
            "agent": {
                "agent_id": "",
                "cloud_server_url": "",
                "cloud_server_token": "",
                "log_level": "INFO"
            },
            "streaming": {
                "quality": "medium",
                "buffer_size": 1048576,
                "rtsp_port": camera_config["rtsp_port"],
                "stream_paths": camera_config["stream_paths"]
            },
            "network": {
                "connection_timeout": 30,
                "reconnect_interval": 10,
                "heartbeat_interval": 30
            }
        }
        
        # Объединение с пользовательской конфигурацией
        if user_config:
            config_data.update(user_config)
        
        # Сохранение конфигурации
        config_file = output_path / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Создание примера конфигурации
        example_config = config_data.copy()
        example_config["agent"]["agent_id"] = "your-agent-id"
        example_config["agent"]["cloud_server_url"] = "wss://your-cloud-server.com/agent"
        example_config["agent"]["cloud_server_token"] = "your-token-here"
        
        example_file = output_path / "config.example.json"
        example_file.write_text(json.dumps(example_config, indent=2))
    
    def _create_install_scripts(self, output_path: Path, camera_model: str,
                              camera_config: Dict[str, Any]):
        """Создание скриптов установки"""
        
        # Скрипт установки
        install_script = f'''#!/bin/sh
# Скрипт установки Camera Agent для {camera_model}

set -e

        echo "[INSTALL] Установка Camera Agent для {camera_model}..."

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
'''
        
        install_file = output_path / "install.sh"
        install_file.write_text(install_script)
        install_file.chmod(0o755)
        
        # Скрипт удаления
        uninstall_script = f'''#!/bin/sh
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
'''
        
        uninstall_file = output_path / "uninstall.sh"
        uninstall_file.write_text(uninstall_script)
        uninstall_file.chmod(0o755)
    
    def _create_makefile(self, output_path: Path, camera_model: str,
                        camera_config: Dict[str, Any]):
        """Создание Makefile для сборки"""
        
        makefile_content = f'''
# Makefile для сборки Camera Agent для {camera_model}

CC = gcc
CFLAGS = -Wall -Wextra -O2
PYTHON = python3

# Платформа
PLATFORM = {camera_config['platform']}
ARCH = {camera_config['architecture']}

# Директории
SRC_DIR = agent
BUILD_DIR = build
DIST_DIR = dist

.PHONY: all clean build package install

all: build package

build:
\t@echo "[BUILD] Сборка Camera Agent..."
\tmkdir -p $(BUILD_DIR)
\t$(PYTHON) -m py_compile $(SRC_DIR)/**/*.py
\tcp -r $(SRC_DIR) $(BUILD_DIR)/
\tcp config.json $(BUILD_DIR)/

package:
\t@echo "[PACKAGE] Создание пакета..."
\tmkdir -p $(DIST_DIR)
\ttar -czf $(DIST_DIR)/{camera_model}_firmware.tar.gz \\
\t\t$(BUILD_DIR)/* \\
\t\tinstall.sh \\
\t\tuninstall.sh

clean:
\t@echo "[CLEAN] Очистка..."
\trm -rf $(BUILD_DIR) $(DIST_DIR)

install: build package
\t@echo "[INSTALL] Установка..."
\t./install.sh

# Цель для кросс-компиляции (если нужно)
cross-compile:
\t@echo "[CROSS-COMPILE] Кросс-компиляция для $(PLATFORM)..."
\t# TODO: Добавить команды кросс-компиляции
'''
        
        makefile_file = output_path / "Makefile"
        makefile_file.write_text(makefile_content)
    
    def _create_firmware_package(self, output_path: Path, camera_model: str):
        """Создание файла прошивки"""
        
        # Создание архива прошивки
        firmware_file = output_path / f"{camera_model}_firmware.tar.gz"
        
        import tarfile
        
        with tarfile.open(firmware_file, "w:gz") as tar:
            # Добавление всех файлов в архив
            for file_path in output_path.rglob("*"):
                if file_path.is_file() and file_path.name != firmware_file.name:
                    arcname = file_path.relative_to(output_path)
                    tar.add(file_path, arcname=arcname)
        
        print(f"[PACKAGE] Создан файл прошивки: {firmware_file}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Сборщик Camera Agent для IP-камер")
    parser.add_argument("--camera", required=True, help="Модель камеры (dahua-2449, hikvision-ds2cd, axis-m30)")
    parser.add_argument("--output", required=True, help="Выходная директория")
    parser.add_argument("--config", help="JSON файл с конфигурацией")
    
    args = parser.parse_args()
    
    # Загрузка пользовательской конфигурации
    user_config = None
    if args.config:
        with open(args.config, 'r') as f:
            user_config = json.load(f)
    
    # Сборка агента
    builder = CameraAgentBuilder()
    success = builder.build(args.camera, args.output, user_config)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
