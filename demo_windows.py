#!/usr/bin/env python3
"""
Простая демонстрация Camera Agent Firmware (Windows версия)
"""
import json
import time
from pathlib import Path


def show_supported_cameras():
    """Показать поддерживаемые камеры"""
    
    cameras = {
        "dahua-2449": {
            "name": "Dahua IPC-HFW2449",
            "type": "4MP купольная камера",
            "platform": "Linux ARM",
            "rtsp_port": 554,
            "features": ["4MP", "Night Vision", "Motion Detection"]
        },
        "dahua-2449s-il": {
            "name": "Dahua IPC-HFW2449S-S-IL",
            "type": "4MP цилиндрическая камера",
            "platform": "Linux ARM",
            "rtsp_port": 554,
            "features": ["4MP", "H.265", "WDR", "Smart Detection", "IP67"]
        },
        "hikvision-ds2cd": {
            "name": "Hikvision DS-2CD2043",
            "type": "4MP купольная камера", 
            "platform": "Linux ARM",
            "rtsp_port": 554,
            "features": ["4MP", "WDR", "ONVIF"]
        },
        "axis-m30": {
            "name": "Axis M3046-V",
            "type": "4MP сетевая камера",
            "platform": "Linux ARM",
            "rtsp_port": 554,
            "features": ["4MP", "H.264", "Edge Storage"]
        }
    }
    
    print("[CAMERAS] Поддерживаемые камеры:")
    print("=" * 60)
    
    for model, info in cameras.items():
        print(f"* {model}")
        print(f"  Название: {info['name']}")
        print(f"  Тип: {info['type']}")
        print(f"  Платформа: {info['platform']}")
        print(f"  RTSP порт: {info['rtsp_port']}")
        print(f"  Особенности: {', '.join(info['features'])}")
        print()


def show_firmware_info():
    """Показать информацию о созданных прошивках"""
    
    firmware_dir = Path("firmware")
    
    if not firmware_dir.exists():
        print("[ERROR] Директория firmware не найдена")
        return
    
    print("[FIRMWARE] Созданные прошивки:")
    print("=" * 50)
    
    for camera_dir in firmware_dir.iterdir():
        if camera_dir.is_dir():
            print(f"* {camera_dir.name}")
            
            # Проверяем наличие файлов
            firmware_file = camera_dir / f"{camera_dir.name}_firmware.tar.gz"
            config_file = camera_dir / "config.json"
            install_file = camera_dir / "install.sh"
            
            print(f"  Прошивка: {'[OK]' if firmware_file.exists() else '[MISSING]'} {firmware_file.name}")
            print(f"  Конфигурация: {'[OK]' if config_file.exists() else '[MISSING]'}")
            print(f"  Скрипт установки: {'[OK]' if install_file.exists() else '[MISSING]'}")
            
            # Показываем размер прошивки
            if firmware_file.exists():
                size_mb = firmware_file.stat().st_size / (1024 * 1024)
                print(f"  Размер: {size_mb:.1f} MB")
            
            print()


def show_cloud_server_status():
    """Показать статус облачного сервера"""
    
    try:
        import requests
        
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[CLOUD] Облачный сервер:")
            print("=" * 30)
            print(f"[OK] Статус: {data['status']}")
            print(f"[INFO] Агентов: {data.get('cameras_count', 0)}")
            print(f"[TIME] Время: {data.get('timestamp', 'N/A')}")
            
            # Получаем список агентов
            agents_response = requests.get("http://localhost:8080/agents", timeout=5)
            if agents_response.status_code == 200:
                agents = agents_response.json()
                if agents:
                    print(f"\n[AGENTS] Подключенные агенты:")
                    for agent in agents:
                        print(f"  - {agent.get('agent_id', 'Unknown')} ({agent.get('camera_model', 'Unknown')})")
                else:
                    print(f"\n[INFO] Нет подключенных агентов")
            
        else:
            print("[ERROR] Облачный сервер недоступен")
            
    except ImportError:
        print("[ERROR] Модуль requests не установлен")
    except Exception as e:
        print(f"[ERROR] Облачный сервер не запущен: {e}")
        print("[INFO] Запустите сервер: cd cloud-server && python server.py")


def show_build_commands():
    """Показать команды для сборки прошивок"""
    
    print("[BUILD] Команды для сборки прошивок:")
    print("=" * 40)
    
    commands = [
        ("Dahua IPC-HFW2449S-S-IL", "python tools/build_agent.py --camera dahua-2449s-il --output firmware/dahua-2449s-il"),
        ("Dahua IPC-HFW2449", "python tools/build_agent.py --camera dahua-2449 --output firmware/dahua-2449"),
        ("Hikvision DS-2CD2043", "python tools/build_agent.py --camera hikvision-ds2cd --output firmware/hikvision"),
        ("Axis M3046-V", "python tools/build_agent.py --camera axis-m30 --output firmware/axis"),
    ]
    
    for camera, command in commands:
        print(f"* {camera}:")
        print(f"  {command}")
        print()


def show_installation_guide():
    """Показать инструкцию по установке"""
    
    print("[INSTALL] Инструкция по установке:")
    print("=" * 35)
    
    steps = [
        "1. Создайте прошивку для вашей камеры",
        "2. Откройте веб-интерфейс камеры (http://IP-адрес)",
        "3. Перейдите в System -> Maintenance -> Upgrade",
        "4. Загрузите файл прошивки (.tar.gz)",
        "5. Дождитесь перезагрузки камеры",
        "6. Отредактируйте /etc/camera_agent/config.json",
        "7. Запустите агент: systemctl start camera-agent"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print()
    print("[INFO] Подробная инструкция в файле INSTALL.md")


def main():
    """Главная функция демонстрации"""
    
    print("[CAMERA AGENT] Camera Agent Firmware - Демонстрация")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Показать поддерживаемые камеры")
        print("2. Показать созданные прошивки")
        print("3. Проверить статус облачного сервера")
        print("4. Показать команды сборки")
        print("5. Показать инструкцию по установке")
        print("0. Выход")
        
        try:
            choice = input("\nВведите номер (0-5): ").strip()
            
            if choice == "0":
                print("[EXIT] До свидания!")
                break
            elif choice == "1":
                show_supported_cameras()
            elif choice == "2":
                show_firmware_info()
            elif choice == "3":
                show_cloud_server_status()
            elif choice == "4":
                show_build_commands()
            elif choice == "5":
                show_installation_guide()
            else:
                print("[ERROR] Неверный выбор")
                
        except KeyboardInterrupt:
            print("\n[EXIT] До свидания!")
            break
        except Exception as e:
            print(f"[ERROR] Ошибка: {e}")


if __name__ == "__main__":
    main()

