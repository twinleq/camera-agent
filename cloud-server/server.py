"""
Облачный сервер для приема Camera Agents
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn


@dataclass
class AgentInfo:
    """Информация об агенте"""
    agent_id: str
    camera_model: str
    status: str
    connected_at: datetime
    last_heartbeat: datetime
    ip_address: str
    stats: Dict[str, Any]


@dataclass
class StreamInfo:
    """Информация о потоке"""
    agent_id: str
    stream_url: str
    quality: str
    active: bool
    viewers_count: int


class CloudServer:
    """Облачный сервер для приема агентов"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Camera Agent Cloud Server")
        
        # Хранилище данных
        self.agents: Dict[str, AgentInfo] = {}
        self.streams: Dict[str, StreamInfo] = {}
        self.connections: Dict[str, WebSocket] = {}
        
        # Настройка CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Настройка маршрутов
        self._setup_routes()
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _setup_routes(self):
        """Настройка маршрутов API"""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "Camera Agent Cloud Server",
                "version": "1.0.0",
                "agents_count": len(self.agents),
                "streams_count": len(self.streams)
            }
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "agents": len(self.agents),
                "streams": len(self.streams)
            }
        
        @self.app.get("/agents")
        async def get_agents():
            """Получение списка агентов"""
            return [asdict(agent) for agent in self.agents.values()]
        
        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Получение информации об агенте"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            return asdict(self.agents[agent_id])
        
        @self.app.get("/agents/{agent_id}/stream")
        async def get_agent_stream(agent_id: str):
            """Получение потока агента"""
            if agent_id not in self.streams:
                raise HTTPException(status_code=404, detail="Stream not found")
            return asdict(self.streams[agent_id])
        
        @self.app.post("/agents/{agent_id}/control")
        async def control_agent(agent_id: str, command: Dict[str, Any]):
            """Управление агентом"""
            if agent_id not in self.connections:
                raise HTTPException(status_code=404, detail="Agent not connected")
            
            # Отправка команды агенту
            await self.connections[agent_id].send_text(json.dumps({
                "type": "command",
                "data": command
            }))
            
            return {"status": "command_sent"}
        
        @self.app.get("/streams")
        async def get_streams():
            """Получение списка потоков"""
            return [asdict(stream) for stream in self.streams.values()]
        
        @self.app.websocket("/agent/{agent_id}")
        async def agent_websocket(websocket: WebSocket, agent_id: str):
            """WebSocket подключение агента"""
            await websocket.accept()
            self.connections[agent_id] = websocket
            
            self.logger.info(f"Agent {agent_id} connected")
            
            try:
                while True:
                    # Получение данных от агента
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    await self._handle_agent_message(agent_id, message)
                    
            except WebSocketDisconnect:
                self.logger.info(f"Agent {agent_id} disconnected")
                await self._handle_agent_disconnect(agent_id)
    
    async def _handle_agent_message(self, agent_id: str, message: Dict[str, Any]):
        """Обработка сообщения от агента"""
        message_type = message.get("type")
        
        if message_type == "register":
            await self._handle_agent_registration(agent_id, message.get("data", {}))
        
        elif message_type == "heartbeat":
            await self._handle_agent_heartbeat(agent_id, message.get("data", {}))
        
        elif message_type == "stream_data":
            await self._handle_stream_data(agent_id, message.get("data"))
        
        elif message_type == "status_update":
            await self._handle_status_update(agent_id, message.get("data", {}))
        
        else:
            self.logger.warning(f"Unknown message type from agent {agent_id}: {message_type}")
    
    async def _handle_agent_registration(self, agent_id: str, data: Dict[str, Any]):
        """Обработка регистрации агента"""
        try:
            agent_info = AgentInfo(
                agent_id=agent_id,
                camera_model=data.get("camera_model", "unknown"),
                status="connected",
                connected_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
                ip_address=data.get("ip_address", ""),
                stats=data.get("stats", {})
            )
            
            self.agents[agent_id] = agent_info
            
            # Создание записи о потоке
            stream_info = StreamInfo(
                agent_id=agent_id,
                stream_url=f"rtsp://{self.host}:8554/{agent_id}",
                quality=data.get("quality", "medium"),
                active=True,
                viewers_count=0
            )
            
            self.streams[agent_id] = stream_info
            
            self.logger.info(f"Agent {agent_id} registered successfully")
            
            # Отправка подтверждения агенту
            await self.connections[agent_id].send_text(json.dumps({
                "type": "registration_confirmed",
                "data": {
                    "agent_id": agent_id,
                    "stream_url": stream_info.stream_url,
                    "server_time": datetime.utcnow().isoformat()
                }
            }))
            
        except Exception as e:
            self.logger.error(f"Error handling agent registration: {e}")
    
    async def _handle_agent_heartbeat(self, agent_id: str, data: Dict[str, Any]):
        """Обработка heartbeat от агента"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.utcnow()
            self.agents[agent_id].stats = data.get("stats", {})
            
            self.logger.debug(f"Heartbeat from agent {agent_id}")
    
    async def _handle_stream_data(self, agent_id: str, data: bytes):
        """Обработка данных потока от агента"""
        # TODO: Реализовать обработку и ретрансляцию потока
        # Здесь можно интегрировать с RTSP сервером или другим стриминг решением
        
        if agent_id in self.streams:
            self.streams[agent_id].viewers_count += 1  # Простая логика подсчета зрителей
        
        self.logger.debug(f"Received stream data from agent {agent_id}: {len(data)} bytes")
    
    async def _handle_status_update(self, agent_id: str, data: Dict[str, Any]):
        """Обработка обновления статуса агента"""
        if agent_id in self.agents:
            self.agents[agent_id].status = data.get("status", "unknown")
            self.agents[agent_id].stats.update(data.get("stats", {}))
            
            self.logger.info(f"Status update from agent {agent_id}: {data.get('status')}")
    
    async def _handle_agent_disconnect(self, agent_id: str):
        """Обработка отключения агента"""
        if agent_id in self.agents:
            self.agents[agent_id].status = "disconnected"
        
        if agent_id in self.streams:
            self.streams[agent_id].active = False
        
        if agent_id in self.connections:
            del self.connections[agent_id]
        
        self.logger.info(f"Agent {agent_id} disconnected")
    
    async def start(self):
        """Запуск сервера"""
        self.logger.info(f"Starting Cloud Server on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики сервера"""
        connected_agents = sum(1 for agent in self.agents.values() if agent.status == "connected")
        active_streams = sum(1 for stream in self.streams.values() if stream.active)
        
        return {
            "total_agents": len(self.agents),
            "connected_agents": connected_agents,
            "total_streams": len(self.streams),
            "active_streams": active_streams,
            "total_viewers": sum(stream.viewers_count for stream in self.streams.values())
        }


async def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Camera Agent Cloud Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--config", help="Configuration file")
    
    args = parser.parse_args()
    
    # Создание и запуск сервера
    server = CloudServer(host=args.host, port=args.port)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main())




