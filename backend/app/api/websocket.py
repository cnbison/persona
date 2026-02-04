"""
WebSocket连接管理
用于实时推送脚本生成进度
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from loguru import logger


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储所有活跃连接: {script_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, script_id: str):
        """接受新的WebSocket连接"""
        await websocket.accept()
        if script_id not in self.active_connections:
            self.active_connections[script_id] = set()
        self.active_connections[script_id].add(websocket)
        logger.info(f"✅ WebSocket连接建立: script_id={script_id}, 当前连接数={len(self.active_connections[script_id])}")

    def disconnect(self, websocket: WebSocket, script_id: str):
        """断开WebSocket连接"""
        if script_id in self.active_connections:
            self.active_connections[script_id].discard(websocket)
            # 如果该script_id没有连接了，删除key
            if not self.active_connections[script_id]:
                del self.active_connections[script_id]
            logger.info(f"❌ WebSocket连接断开: script_id={script_id}, 剩余连接数={len(self.active_connections.get(script_id, set()))}")

    async def send_progress(
        self,
        script_id: str,
        percentage: int,
        current_step: str,
        status: str = "generating",
        extra_data: dict = None
    ):
        """
        向指定script_id的所有连接发送进度更新

        参数:
            script_id: 脚本ID
            percentage: 进度百分比(0-100)
            current_step: 当前步骤描述
            status: 状态 (generating/completed/failed)
            extra_data: 额外数据
        """
        if script_id not in self.active_connections:
            logger.debug(f"⚠️  没有活跃的WebSocket连接: script_id={script_id}")
            return

        message = {
            "type": "progress_update",
            "data": {
                "script_id": script_id,
                "percentage": percentage,
                "current_step": current_step,
                "status": status
            }
        }

        if extra_data:
            message["data"].update(extra_data)

        # 向所有连接发送消息
        dead_connections = set()
        for connection in self.active_connections[script_id]:
            try:
                await connection.send_json(message)
                logger.debug(f"📤 发送进度更新: script_id={script_id}, {percentage}%")
            except Exception as e:
                logger.error(f"❌ 发送消息失败: {e}")
                dead_connections.add(connection)

        # 清理死连接
        for connection in dead_connections:
            self.disconnect(connection, script_id)

    async def broadcast_log(self, script_id: str, log_message: str):
        """
        广播日志消息
        """
        if script_id not in self.active_connections:
            return

        message = {
            "type": "log",
            "data": {
                "script_id": script_id,
                "message": log_message,
                "timestamp": asyncio.get_event_loop().time()
            }
        }

        dead_connections = set()
        for connection in self.active_connections[script_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        for connection in dead_connections:
            self.disconnect(connection, script_id)

    def get_connection_count(self, script_id: str) -> int:
        """获取指定script_id的连接数"""
        return len(self.active_connections.get(script_id, set()))


# 全局单例
manager = ConnectionManager()
