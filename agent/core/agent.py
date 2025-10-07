"""
Основной модуль Camera Agent для встраивания в IP-камеру
"""
import asyncio
import json
import time
import uuid
import socket
import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Платформо-специфичные импорты (будут разными для разных камер)
try:
    import platform_specific  # Модуль для конкретной платформы камеры
except ImportError:
    platform_specific = None


class AgentStatus(Enum):
    """Статусы агента"""
    STOPPED = "stopped"
    STARTING = "starting"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class AgentConfig:
    """Конфигурация агента"""
    # Основные настройки
    agent_id: str
    connection_mode: str = "tunnel"  # tunnel, p2p, hybrid
    device_id: str = ""  # Device ID камеры (получается автоматически)
    
    # Туннельные настройки (как у Flussonic/peeklio)
    tunnel_server_url: str = ""  # URL туннельного сервера
    tunnel_server_token: str = ""
    tunnel_port: int = 2956  # Порт для туннеля (как в peeklio: -M 2956)
    
    # P2P настройки
    p2p_enabled: bool = False
    stun_servers: list = None  # Список STUN серверов
    turn_servers: list = None  # Список TURN серверов
    p2p_registry_url: str = ""  # URL P2P реестра
    
    # Настройки камеры
    camera_ip: str = "127.0.0.1"  # IP камеры (обычно локальный)
    camera_rtsp_port: int = 554   # RTSP порт камеры
    camera_username: str = "admin"
    camera_password: str = "admin"
    
    # Сетевые настройки
    connection_timeout: int = 30
    reconnect_interval: int = 10
    heartbeat_interval: int = 30
    
    # Настройки стриминга
    stream_quality: str = "medium"  # low/medium/high
    buffer_size: int = 1024 * 1024  # 1MB буфер
    
    # Безопасность (как у peeklio)
    encryption_enabled: bool = True
    ssl_verify: bool = True
    ssl_cert_file: str = "/etc/camera_agent/agent.pem"  # Как -A в peeklio
    ssl_root_cert: str = "/etc/camera_agent/root.crt"   # Как -e в peeklio
    
    # Конфигурация (как у peeklio)
    config_path: str = "/mnt/mtd/Config/camera_agent.cfg"  # Как -c в peeklio
    
    # Логирование
    log_level: str = "INFO"
    log_file: Optional[str] = "/var/log/camera_agent.log"


class CameraAgent:
    """Основной класс агента для IP-камеры"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.STOPPED
        self.start_time = None
        self.last_heartbeat = None
        self.connection = None
        self.stream_processor = None
        self.buffer = []
        
        # Device ID (как в peeklio получается из armbenv)
        self.device_id = self._get_device_id()
        
        # Настройка логирования
        self._setup_logging()
        
        # Статистика
        self.stats = {
            "bytes_sent": 0,
            "bytes_received": 0,
            "packets_lost": 0,
            "reconnections": 0,
            "uptime": 0
        }
        
        self.logger.info(f"Camera Agent {config.agent_id} инициализирован")
    
    def _get_device_id(self) -> str:
        """
        Получение Device ID камеры
        В peeklio это: armbenv -r | grep 'ID =' | grep -v : | sed 's/.\\{5\\}//'
        """
        if self.config.device_id:
            return self.config.device_id
        
        try:
            # Попытка получить из armbenv (Dahua)
            result = subprocess.run(
                ['armbenv', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'ID =' in line and ':' not in line:
                        # Извлекаем ID (пропускаем первые 5 символов)
                        device_id = line[5:].strip()
                        logging.info(f"[AGENT] Device ID получен из armbenv: {device_id}")
                        return device_id
        except Exception as e:
            logging.warning(f"[AGENT] Не удалось получить Device ID из armbenv: {e}")
        
        # Fallback - используем MAC адрес или генерируем
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,2*6,2)][::-1])
            device_id = mac.replace(':', '')
            logging.info(f"[AGENT] Device ID сгенерирован из MAC: {device_id}")
            return device_id
        except:
            # Последний fallback
            device_id = str(uuid.uuid4())[:8]
            logging.info(f"[AGENT] Device ID сгенерирован случайно: {device_id}")
            return device_id
    
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config.log_file
        )
        self.logger = logging.getLogger(f"camera_agent_{self.config.agent_id}")
    
    async def start(self):
        """Запуск агента"""
        try:
            self.logger.info(f"Запуск Camera Agent (Device ID: {self.device_id})...")
            self.status = AgentStatus.STARTING
            self.start_time = time.time()
            
            # Инициализация платформо-специфичных компонентов
            await self._init_platform()
            
            # Выбор режима подключения
            if self.config.connection_mode == "tunnel":
                await self._connect_tunnel_mode()
            elif self.config.connection_mode == "p2p":
                await self._connect_p2p_mode()
            else:  # hybrid
                await self._connect_hybrid_mode()
            
            # Запуск стриминга
            await self._start_streaming()
            
            # Запуск мониторинга
            asyncio.create_task(self._monitoring_loop())
            
            self.status = AgentStatus.CONNECTED
            self.logger.info("Camera Agent запущен успешно")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Ошибка запуска агента: {e}")
            raise
    
    async def stop(self):
        """Остановка агента"""
        try:
            self.logger.info("Остановка Camera Agent...")
            self.status = AgentStatus.STOPPED
            
            # Остановка стриминга
            if self.stream_processor:
                await self.stream_processor.stop()
            
            # Отключение от облачного сервера
            if self.connection:
                await self.connection.close()
            
            self.logger.info("Camera Agent остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки агента: {e}")
    
    async def _init_platform(self):
        """Инициализация платформо-специфичных компонентов"""
        if platform_specific:
            # Инициализация для конкретной платформы камеры
            await platform_specific.init_camera_interface()
            await platform_specific.init_network_stack()
        else:
            # Общая инициализация
            self.logger.warning("Платформо-специфичные компоненты не найдены")
    
    async def _connect_tunnel_mode(self):
        """Подключение в режиме туннеля (как peeklio)"""
        self.logger.info("[TUNNEL] Режим туннеля активирован")
        
        # Создание туннельного соединения
        self.connection = TunnelConnection(
            url=self.config.tunnel_server_url,
            token=self.config.tunnel_server_token,
            agent_id=self.config.agent_id
        )
        
        # Регистрация и создание туннеля
        await self.connection.register()
        await self.connection.establish_tunnel()
    
    async def _connect_p2p_mode(self):
        """Подключение в режиме P2P"""
        self.logger.info("[P2P] Режим P2P активирован")
        
        # Создание P2P соединения
        self.connection = P2PConnection(
            agent_id=self.config.agent_id,
            stun_servers=self.config.stun_servers or [],
            turn_servers=self.config.turn_servers or []
        )
        
        # Регистрация в P2P реестре
        await self.connection.register_with_p2p_registry(self.config.p2p_registry_url)
    
    async def _connect_hybrid_mode(self):
        """Гибридный режим - пытаемся P2P, fallback на туннель"""
        self.logger.info("[HYBRID] Гибридный режим активирован")
        
        # Сначала пытаемся P2P
        if self.config.p2p_enabled:
            try:
                await self._connect_p2p_mode()
                self.logger.info("[HYBRID] P2P соединение установлено")
                return
            except Exception as e:
                self.logger.warning(f"[HYBRID] P2P не удалось: {e}")
        
        # Fallback на туннель
        await self._connect_tunnel_mode()
        self.logger.info("[HYBRID] Используется туннельное соединение")
    
    async def _connect_to_cloud(self):
        """Подключение к облачному серверу"""
        try:
            self.logger.info(f"Подключение к облачному серверу: {self.config.cloud_server_url}")
            self.status = AgentStatus.CONNECTING
            
            # Создание соединения с облачным сервером
            self.connection = CloudConnection(
                url=self.config.cloud_server_url,
                token=self.config.cloud_server_token,
                agent_id=self.config.agent_id
            )
            
            # Регистрация агента на сервере
            await self.connection.register()
            
            self.logger.info("Подключение к облачному серверу установлено")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Ошибка подключения к облачному серверу: {e}")
            raise
    
    async def _start_streaming(self):
        """Запуск стриминга с камеры"""
        try:
            self.logger.info("Запуск стриминга с камеры...")
            
            # Создание процессора потока
            self.stream_processor = StreamProcessor(
                camera_url=self.config.camera_rtsp_url,
                camera_username=self.config.camera_username,
                camera_password=self.config.camera_password,
                quality=self.config.stream_quality,
                buffer_size=self.config.buffer_size
            )
            
            # Запуск обработки потока
            await self.stream_processor.start()
            
            # Запуск отправки потока на сервер
            asyncio.create_task(self._stream_to_cloud())
            
            self.logger.info("Стриминг запущен")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска стриминга: {e}")
            raise
    
    async def _stream_to_cloud(self):
        """Отправка потока на облачный сервер"""
        try:
            while self.status == AgentStatus.CONNECTED:
                # Получение данных потока
                stream_data = await self.stream_processor.get_stream_data()
                
                if stream_data:
                    # Отправка на облачный сервер с буферизацией
                    await self._send_to_cloud(stream_data)
                
                await asyncio.sleep(0.04)  # 25 FPS
                
        except Exception as e:
            self.logger.error(f"Ошибка отправки потока: {e}")
            await self._handle_connection_error()
    
    async def _send_to_cloud(self, data: bytes):
        """Отправка данных на облачный сервер с буферизацией"""
        try:
            # Отправка через соединение
            success = await self.connection.send_stream_data(data)
            
            if success:
                self.stats["bytes_sent"] += len(data)
            else:
                # Добавление в буфер для повторной отправки
                self.buffer.append(data)
                self.stats["packets_lost"] += 1
                
                # Попытка повторной отправки буфера
                await self._retry_buffered_data()
                
        except Exception as e:
            self.logger.error(f"Ошибка отправки данных: {e}")
            self.buffer.append(data)
    
    async def _retry_buffered_data(self):
        """Повторная отправка данных из буфера"""
        while self.buffer and self.status == AgentStatus.CONNECTED:
            data = self.buffer.pop(0)
            try:
                success = await self.connection.send_stream_data(data)
                if success:
                    self.stats["bytes_sent"] += len(data)
                else:
                    # Возврат в буфер если не удалось отправить
                    self.buffer.insert(0, data)
                    break
            except Exception as e:
                self.logger.error(f"Ошибка повторной отправки: {e}")
                self.buffer.insert(0, data)
                break
    
    async def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.status in [AgentStatus.CONNECTED, AgentStatus.RECONNECTING]:
            try:
                # Отправка heartbeat
                await self._send_heartbeat()
                
                # Проверка соединения
                await self._check_connection()
                
                # Обновление статистики
                self._update_stats()
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                await self._handle_connection_error()
    
    async def _send_heartbeat(self):
        """Отправка heartbeat на сервер"""
        try:
            heartbeat_data = {
                "agent_id": self.config.agent_id,
                "status": self.status.value,
                "timestamp": time.time(),
                "stats": self.stats
            }
            
            await self.connection.send_heartbeat(heartbeat_data)
            self.last_heartbeat = time.time()
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки heartbeat: {e}")
            raise
    
    async def _check_connection(self):
        """Проверка состояния соединения"""
        if not self.connection or not self.connection.is_connected():
            await self._handle_connection_error()
    
    async def _handle_connection_error(self):
        """Обработка ошибок соединения"""
        self.logger.warning("Ошибка соединения, переподключение...")
        self.status = AgentStatus.RECONNECTING
        self.stats["reconnections"] += 1
        
        # Ожидание перед переподключением
        await asyncio.sleep(self.config.reconnect_interval)
        
        try:
            # Переподключение к облачному серверу
            await self._connect_to_cloud()
            self.status = AgentStatus.CONNECTED
            self.logger.info("Переподключение успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка переподключения: {e}")
            self.status = AgentStatus.ERROR
    
    def _update_stats(self):
        """Обновление статистики"""
        if self.start_time:
            self.stats["uptime"] = time.time() - self.start_time
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        return {
            "agent_id": self.config.agent_id,
            "status": self.status.value,
            "uptime": self.stats["uptime"],
            "stats": self.stats,
            "last_heartbeat": self.last_heartbeat,
            "buffer_size": len(self.buffer)
        }


class P2PConnection:
    """Класс для P2P соединения"""
    
    def __init__(self, agent_id: str, stun_servers: list, turn_servers: list):
        self.agent_id = agent_id
        self.stun_servers = stun_servers or []
        self.turn_servers = turn_servers or []
        self.connected = False
        self.peer_connections = {}  # Активные P2P соединения
        self.ice_connection = None
        self.stats = {
            "p2p_connections": 0,
            "direct_connections": 0,
            "relay_connections": 0,
            "bytes_sent": 0,
            "bytes_received": 0
        }
    
    async def register_with_p2p_registry(self, registry_url: str):
        """Регистрация в P2P реестре"""
        # TODO: Реализация регистрации в P2P реестре
        self.connected = True
    
    async def establish_p2p_connection(self, peer_id: str):
        """Установка P2P соединения с клиентом"""
        # TODO: Реализация ICE/STUN/TURN для P2P
        return True
    
    async def send_stream_via_p2p(self, data: bytes, peer_id: str):
        """Отправка потока через P2P соединение"""
        # TODO: Реализация отправки данных через P2P
        return True


class TunnelConnection:
    """Класс для создания туннеля с сервером"""
    
    def __init__(self, url: str, token: str, agent_id: str):
        self.url = url
        self.token = token
        self.agent_id = agent_id
        self.connected = False
        self.websocket = None
        self.tunnel_port = None  # Порт туннеля на сервере
    
    async def register(self):
        """Регистрация агента и создание туннеля"""
        # Подключение к туннельному серверу
        # Запрос на создание туннеля
        # Получение порта туннеля от сервера
        self.connected = True
        self.tunnel_port = 8554  # Получаем от сервера
    
    async def establish_tunnel(self) -> bool:
        """Создание туннеля до камеры"""
        # Создание TCP туннеля от сервера до локальной камеры
        # Камера становится доступна как 127.0.0.1:tunnel_port на сервере
        return True
    
    async def send_heartbeat(self, data: Dict[str, Any]):
        """Отправка heartbeat через туннель"""
        # Отправка статуса через туннельное соединение
        pass
    
    def is_connected(self) -> bool:
        """Проверка соединения"""
        return self.connected
    
    async def close(self):
        """Закрытие соединения"""
        self.connected = False


class StreamProcessor:
    """Класс для обработки потока с камеры"""
    
    def __init__(self, camera_url: str, camera_username: str, 
                 camera_password: str, quality: str, buffer_size: int):
        self.camera_url = camera_url
        self.camera_username = camera_username
        self.camera_password = camera_password
        self.quality = quality
        self.buffer_size = buffer_size
        self.running = False
        self.camera_ip = self._detect_camera_ip()
    
    def _detect_camera_ip(self) -> str:
        """Автоматическое определение IP камеры"""
        try:
            # Получение IP через socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                logging.info(f"[STREAM] Обнаружен IP камеры: {local_ip}")
                return local_ip
        except Exception as e:
            logging.warning(f"[STREAM] Ошибка определения IP: {e}")
            return "127.0.0.1"
    
    async def start(self):
        """Запуск обработки потока"""
        self.running = True
        # TODO: Реализация подключения к камере и получения потока
    
    async def get_stream_data(self) -> Optional[bytes]:
        """Получение данных потока"""
        # TODO: Реализация получения данных от камеры
        return None
    
    async def stop(self):
        """Остановка обработки потока"""
        self.running = False
        # TODO: Реализация остановки потока


# Точка входа для агента
async def main():
    """Главная функция агента"""
    
    # Загрузка конфигурации
    config = AgentConfig(
        agent_id=str(uuid.uuid4()),
        cloud_server_url="wss://cloud.example.com/agent",
        cloud_server_token="your_token_here",
        camera_rtsp_url="rtsp://localhost:554/stream1",
        camera_username="admin",
        camera_password="password"
    )
    
    # Создание и запуск агента
    agent = CameraAgent(config)
    
    try:
        await agent.start()
        
        # Ожидание завершения
        while agent.status != AgentStatus.STOPPED:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Получен сигнал прерывания")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())

