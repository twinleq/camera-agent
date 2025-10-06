#!/usr/bin/env python3
"""
Демонстрация Camera Agent для IP-камер
"""
import asyncio
import json
import time
from typing import Dict, Any
import argparse

from pathlib import Path
import sys

# Добавление пути к агенту
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agent.core.agent import CameraAgent, AgentConfig
except ImportError:
    # Альтернативный импорт для тестирования
    print("Модуль agent не найден, используем заглушку для демонстрации")
    CameraAgent = None
    AgentConfig = None


class CameraAgentDemo:
    """Демонстрация работы Camera Agent"""
    
    def __init__(self):
        self.agents = []
        self.running = False
    
    def create_demo_config(self, camera_model: str) -> AgentConfig:
        """Создание демонстрационной конфигурации"""
        
        configs = {
            "dahua-2449": AgentConfig(
                agent_id=f"dahua-2449-{int(time.time())}",
                cloud_server_url="ws://localhost:8080/agent",
                cloud_server_token="demo-token",
                camera_rtsp_url="rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.amp",
                camera_username="demo",
                camera_password="demo",
                connection_timeout=30,
                reconnect_interval=10,
                heartbeat_interval=30,
                stream_quality="medium",
                buffer_size=1024 * 1024,
                encryption_enabled=False,  # Отключаем для демо
                ssl_verify=False,
                log_level="INFO",
                log_file=None
            ),
            "hikvision-ds2cd": AgentConfig(
                agent_id=f"hikvision-ds2cd-{int(time.time())}",
                cloud_server_url="ws://localhost:8080/agent",
                cloud_server_token="demo-token",
                camera_rtsp_url="rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.amp",
                camera_username="demo",
                camera_password="demo",
                connection_timeout=30,
                reconnect_interval=10,
                heartbeat_interval=30,
                stream_quality="high",
                buffer_size=2 * 1024 * 1024,
                encryption_enabled=False,
                ssl_verify=False,
                log_level="DEBUG",
                log_file="demo_hikvision.log"
            ),
            "axis-m30": AgentConfig(
                agent_id=f"axis-m30-{int(time.time())}",
                cloud_server_url="ws://localhost:8080/agent",
                cloud_server_token="demo-token",
                camera_rtsp_url="rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.amp",
                camera_username="demo",
                camera_password="demo",
                connection_timeout=30,
                reconnect_interval=10,
                heartbeat_interval=30,
                stream_quality="medium",
                buffer_size=1024 * 1024,
                encryption_enabled=False,
                ssl_verify=False,
                log_level="INFO",
                log_file="demo_axis.log"
            )
        }
        
        return configs.get(camera_model, configs["dahua-2449"])
    
    async def start_agent(self, camera_model: str):
        """Запуск агента для конкретной камеры"""
        
        print(f"🚀 Запуск Camera Agent для {camera_model}")
        
        # Создание конфигурации
        config = self.create_demo_config(camera_model)
        
        # Создание и запуск агента
        agent = CameraAgent(config)
        
        try:
            await agent.start()
            self.agents.append(agent)
            
            print(f"✅ Agent {config.agent_id} запущен успешно")
            print(f"📡 Подключение к: {config.cloud_server_url}")
            print(f"🎥 RTSP поток: {config.camera_rtsp_url}")
            
            return agent
            
        except Exception as e:
            print(f"❌ Ошибка запуска агента {camera_model}: {e}")
            return None
    
    async def run_demo(self, camera_models: list):
        """Запуск демонстрации с несколькими агентами"""
        
        print("🎥 Демонстрация Camera Agent для IP-камер")
        print("=" * 50)
        
        self.running = True
        
        # Запуск агентов
        for model in camera_models:
            agent = await self.start_agent(model)
            if agent:
                print(f"✅ {model} подключен")
            else:
                print(f"❌ {model} не удалось подключить")
            
            await asyncio.sleep(2)  # Пауза между запусками
        
        print(f"\n📊 Статус агентов:")
        print("-" * 30)
        
        # Мониторинг агентов
        try:
            while self.running:
                for i, agent in enumerate(self.agents):
                    if agent:
                        status = agent.get_status()
                        print(f"Agent {i+1}: {status['agent_id'][:12]}... | "
                              f"Status: {status['status']} | "
                              f"Uptime: {status['uptime']:.1f}s | "
                              f"Buffer: {status['buffer_size']}")
                
                print("-" * 30)
                await asyncio.sleep(10)  # Обновление каждые 10 секунд
                
        except KeyboardInterrupt:
            print("\n🛑 Остановка демонстрации...")
            self.running = False
        
        # Остановка агентов
        print("\n🛑 Остановка агентов...")
        for agent in self.agents:
            if agent:
                await agent.stop()
        
        print("✅ Демонстрация завершена")
    
    async def test_single_agent(self, camera_model: str, duration: int = 60):
        """Тестирование одного агента"""
        
        print(f"🧪 Тестирование агента {camera_model} в течение {duration} секунд")
        
        agent = await self.start_agent(camera_model)
        if not agent:
            return False
        
        try:
            # Мониторинг в течение указанного времени
            start_time = time.time()
            while time.time() - start_time < duration:
                status = agent.get_status()
                stats = status['stats']
                
                print(f"⏱️  {time.time() - start_time:.1f}s | "
                      f"Status: {status['status']} | "
                      f"Sent: {stats['bytes_sent']} bytes | "
                      f"Lost: {stats['packets_lost']} | "
                      f"Reconnects: {stats['reconnections']}")
                
                await asyncio.sleep(5)
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Тест прерван пользователем")
            return False
        
        finally:
            await agent.stop()
    
    def show_supported_cameras(self):
        """Показать поддерживаемые камеры"""
        
        cameras = {
            "dahua-2449": {
                "name": "Dahua IPC-HFW2449",
                "type": "4MP купольная камера",
                "platform": "Linux ARM",
                "rtsp_port": 554,
                "features": ["4MP", "Night Vision", "Motion Detection"]
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
        
        print("📷 Поддерживаемые камеры:")
        print("=" * 60)
        
        for model, info in cameras.items():
            print(f"🔹 {model}")
            print(f"   Название: {info['name']}")
            print(f"   Тип: {info['type']}")
            print(f"   Платформа: {info['platform']}")
            print(f"   RTSP порт: {info['rtsp_port']}")
            print(f"   Особенности: {', '.join(info['features'])}")
            print()


async def main():
    """Главная функция демонстрации"""
    
    parser = argparse.ArgumentParser(description="Демонстрация Camera Agent")
    parser.add_argument("--camera", help="Модель камеры для тестирования")
    parser.add_argument("--duration", type=int, default=60, help="Длительность теста (секунды)")
    parser.add_argument("--list", action="store_true", help="Показать поддерживаемые камеры")
    parser.add_argument("--demo", action="store_true", help="Запустить демо с несколькими камерами")
    
    args = parser.parse_args()
    
    demo = CameraAgentDemo()
    
    if args.list:
        demo.show_supported_cameras()
        return
    
    if args.demo:
        # Демо с несколькими камерами
        cameras = ["dahua-2449", "hikvision-ds2cd", "axis-m30"]
        await demo.run_demo(cameras)
        return
    
    if args.camera:
        # Тестирование одной камеры
        await demo.test_single_agent(args.camera, args.duration)
        return
    
    # Интерактивный режим
    print("🎥 Camera Agent Demo")
    print("Выберите режим:")
    print("1. Показать поддерживаемые камеры")
    print("2. Тестирование одной камеры")
    print("3. Демо с несколькими камерами")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            demo.show_supported_cameras()
        
        elif choice == "2":
            camera = input("Введите модель камеры (dahua-2449, hikvision-ds2cd, axis-m30): ").strip()
            duration = int(input("Длительность теста в секундах (по умолчанию 60): ") or "60")
            await demo.test_single_agent(camera, duration)
        
        elif choice == "3":
            await demo.run_demo(["dahua-2449", "hikvision-ds2cd", "axis-m30"])
        
        else:
            print("❌ Неверный выбор")
    
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
