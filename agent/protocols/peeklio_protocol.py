"""
Протокол Peeklio (Flussonic Agent) для совместимости
На основе анализа app.sh и параметров запуска peeklio1
"""
import asyncio
import json
import ssl
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PeeklioConfig:
    """Конфигурация в формате peeklio"""
    server_url: str
    device_id: str
    tunnel_port: int = 2956
    ssl_cert: Optional[str] = None
    ssl_root: Optional[str] = None
    config_file: str = "/mnt/mtd/Config/peeklio.cfg"


class PeeklioProtocol:
    """
    Протокол Peeklio для совместимости с Flussonic Watcher
    
    Основано на анализе команды запуска:
    ./peeklio1 -c /mnt/mtd/Config/peeklio.cfg -A C1.pem -e peeklioroot.crt -M 2956 -S $deviceid
    
    Параметры:
    -c : путь к конфигурации
    -A : SSL сертификат клиента  
    -e : SSL root сертификат
    -M : порт туннеля (2956)
    -S : device ID камеры
    """
    
    def __init__(self, config: PeeklioConfig):
        self.config = config
        self.connected = False
        self.websocket = None
        self.ssl_context = None
        self.logger = logging.getLogger("peeklio_protocol")
        
        # Инициализация SSL если сертификаты указаны
        if config.ssl_cert and config.ssl_root:
            self._init_ssl()
    
    def _init_ssl(self):
        """Инициализация SSL контекста"""
        try:
            self.ssl_context = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH,
                cafile=self.config.ssl_root
            )
            
            if self.config.ssl_cert:
                self.ssl_context.load_cert_chain(self.config.ssl_cert)
            
            self.logger.info("[PEEKLIO] SSL контекст инициализирован")
            
        except Exception as e:
            self.logger.error(f"[PEEKLIO] Ошибка инициализации SSL: {e}")
    
    async def connect(self) -> bool:
        """
        Подключение к Flussonic Watcher серверу
        Использует WebSocket с SSL
        """
        try:
            self.logger.info(f"[PEEKLIO] Подключение к {self.config.server_url}")
            
            # Формируем URL с device_id
            url = f"{self.config.server_url}?device_id={self.config.device_id}"
            
            # Подключаемся через WebSocket
            import websockets
            
            if self.ssl_context:
                self.websocket = await websockets.connect(
                    url,
                    ssl=self.ssl_context
                )
            else:
                self.websocket = await websockets.connect(url)
            
            # Отправляем регистрацию
            await self._register()
            
            self.connected = True
            self.logger.info("[PEEKLIO] Подключение установлено")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[PEEKLIO] Ошибка подключения: {e}")
            return False
    
    async def _register(self):
        """Регистрация агента на сервере"""
        registration = {
            "type": "register",
            "device_id": self.config.device_id,
            "tunnel_port": self.config.tunnel_port,
            "capabilities": ["rtsp", "tunnel", "h264", "h265"],
            "version": "1.0.0"
        }
        
        await self.websocket.send(json.dumps(registration))
        
        # Ожидаем ответ
        response = await self.websocket.recv()
        response_data = json.loads(response)
        
        self.logger.info(f"[PEEKLIO] Регистрация: {response_data}")
    
    async def establish_tunnel(self, camera_ip: str, camera_port: int) -> bool:
        """
        Создание туннеля от сервера до локальной камеры
        
        Принцип (как в peeklio):
        1. Агент подключается к серверу через WebSocket
        2. Сервер получает device_id и создает туннель
        3. Камера становится доступна как 127.0.0.1:2956 на сервере
        4. Flussonic Watcher подключается к 127.0.0.1:2956
        """
        try:
            tunnel_request = {
                "type": "create_tunnel",
                "device_id": self.config.device_id,
                "camera_ip": camera_ip,
                "camera_port": camera_port,
                "tunnel_port": self.config.tunnel_port
            }
            
            await self.websocket.send(json.dumps(tunnel_request))
            
            # Ожидаем подтверждения
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("status") == "tunnel_created":
                self.logger.info(f"[PEEKLIO] Туннель создан: 127.0.0.1:{self.config.tunnel_port}")
                return True
            else:
                self.logger.error(f"[PEEKLIO] Ошибка создания туннеля: {response_data}")
                return False
                
        except Exception as e:
            self.logger.error(f"[PEEKLIO] Ошибка создания туннеля: {e}")
            return False
    
    async def send_heartbeat(self):
        """
        Отправка heartbeat на сервер
        Периодически отправляется для поддержания соединения
        """
        try:
            heartbeat = {
                "type": "heartbeat",
                "device_id": self.config.device_id,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "active"
            }
            
            await self.websocket.send(json.dumps(heartbeat))
            self.logger.debug("[PEEKLIO] Heartbeat отправлен")
            
        except Exception as e:
            self.logger.error(f"[PEEKLIO] Ошибка отправки heartbeat: {e}")
    
    async def receive_commands(self):
        """
        Прием команд от сервера
        Обработка управляющих команд от Flussonic Watcher
        """
        try:
            while self.connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                command_type = data.get("type")
                
                if command_type == "restart":
                    self.logger.info("[PEEKLIO] Команда: перезапуск")
                    # TODO: Реализовать перезапуск
                
                elif command_type == "update_config":
                    self.logger.info("[PEEKLIO] Команда: обновление конфигурации")
                    # TODO: Реализовать обновление конфигурации
                
                elif command_type == "get_status":
                    await self._send_status()
                
                else:
                    self.logger.warning(f"[PEEKLIO] Неизвестная команда: {command_type}")
                    
        except Exception as e:
            self.logger.error(f"[PEEKLIO] Ошибка приема команд: {e}")
    
    async def _send_status(self):
        """Отправка статуса агента"""
        status = {
            "type": "status",
            "device_id": self.config.device_id,
            "connected": self.connected,
            "tunnel_active": True,
            "uptime": 0  # TODO: Реальное время работы
        }
        
        await self.websocket.send(json.dumps(status))
    
    async def close(self):
        """Закрытие соединения"""
        self.connected = False
        if self.websocket:
            await self.websocket.close()
        
        self.logger.info("[PEEKLIO] Соединение закрыто")
    
    def is_connected(self) -> bool:
        """Проверка соединения"""
        return self.connected and self.websocket and not self.websocket.closed
