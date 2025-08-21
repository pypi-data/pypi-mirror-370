"""
ネットワーク通信モジュール

EntangleKeyの分散インスタンス間でのネットワーク通信を管理します。
WebSocketベースの双方向通信とメッセージルーティングを提供します。
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Callable, Optional, Any, Set
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.client import WebSocketClientProtocol

from .exceptions import NetworkError, ConnectionError
from .config import NetworkConfig

logger = logging.getLogger(__name__)


class NetworkManager:
    """
    分散インスタンス間のネットワーク通信を管理するクラス
    """

    def __init__(self, instance_id: str, port: int = 8888, config: Optional['NetworkConfig'] = None):
        """
        NetworkManagerを初期化します。

        Args:
            instance_id: このインスタンスの一意識別子
            port: 待受ポート番号
            config: ネットワーク設定
        """
        if config is None:
            from .config import NetworkConfig
            config = NetworkConfig(port=port)
        
        self.config = config
        self.instance_id = instance_id
        self.port = port
        self.server = None
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.clients: Dict[str, WebSocketClientProtocol] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.connection_handlers: List[Callable] = []
        self.disconnection_handlers: List[Callable] = []
        self.is_running = False
        self.pending_connections: Set[str] = set()

    async def start(self):
        """
        ネットワークサーバーを開始します。
        """
        if self.is_running:
            return

        try:
            self.server = await websockets.serve(
                self._handle_client_connection,
                "0.0.0.0",
                self.port,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout
            )
            self.is_running = True
            logger.info(f"Network server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start network server: {e}", exc_info=True)
            raise NetworkError("Failed to start network server.")

    async def stop(self):
        """
        ネットワークサーバーを停止します。
        """
        if not self.is_running:
            return

        self.is_running = False

        # クライント接続を閉じる
        for client_id, client in list(self.clients.items()):
            try:
                await client.close()
            except Exception as e:
                logger.warning(f"Error closing client {client_id}: {e}", exc_info=True)

        # サーバー接続を閉じる
        for connection_id, connection in list(self.connections.items()):
            try:
                await connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection {connection_id}: {e}", exc_info=True)

        # サーバーを停止
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        self.connections.clear()
        self.clients.clear()
        logger.info("Network server stopped")

    async def connect(self, host: str, port: int) -> str:
        """
        他のインスタンスに接続します。

        Args:
            host: 接続先ホスト
            port: 接続先ポート

        Returns:
            接続したインスタンスのID
        """
        connection_id = f"{host}:{port}"
        
        if connection_id in self.pending_connections:
            raise ConnectionError(f"Connection to {connection_id} is already pending")

        if connection_id in self.clients:
            logger.info(f"Already connected to {connection_id}")
            return connection_id

        self.pending_connections.add(connection_id)

        try:
            uri = f"ws://{host}:{port}"
            websocket = await websockets.connect(
                uri,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout
            )

            # ハンドシェイクメッセージを送信
            handshake_msg = {
                'type': 'handshake',
                'instance_id': self.instance_id,
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(handshake_msg))

            # ハンドシェイク応答を待機
            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get('type') != 'handshake_ack':
                raise ConnectionError("Invalid handshake response")

            remote_instance_id = response_data.get('instance_id')
            if not remote_instance_id:
                raise ConnectionError("Remote instance ID not provided")

            self.clients[remote_instance_id] = websocket
            self.pending_connections.discard(connection_id)

            # メッセージ受信タスクを開始
            asyncio.create_task(self._handle_client_messages(remote_instance_id, websocket))

            logger.info(f"Connected to instance {remote_instance_id} at {host}:{port}")

            # 接続ハンドラーを呼び出し
            for handler in self.connection_handlers:
                await handler(remote_instance_id)

            return remote_instance_id

        except Exception as e:
            self.pending_connections.discard(connection_id)
            logger.error(f"Failed to connect to {host}:{port}: {e}", exc_info=True)
            raise ConnectionError(f"Connection to {host}:{port} failed.")

    async def send_to_instance(self, instance_id: str, message: Dict[str, Any]):
        """
        特定のインスタンスにメッセージを送信します。

        Args:
            instance_id: 送信先インスタンスID
            message: 送信するメッセージ
        """
        message['from_instance'] = self.instance_id
        message['timestamp'] = datetime.now().isoformat()
        message_json = json.dumps(message)

        # サーバー接続をチェック
        if instance_id in self.connections:
            try:
                await self.connections[instance_id].send(message_json)
                logger.debug(f"Message sent to {instance_id} via server connection")
                return
            except Exception as e:
                logger.warning(f"Failed to send via server connection to {instance_id}: {e}", exc_info=True)
                del self.connections[instance_id]

        # クライアント接続をチェック
        if instance_id in self.clients:
            try:
                await self.clients[instance_id].send(message_json)
                logger.debug(f"Message sent to {instance_id} via client connection")
                return
            except Exception as e:
                logger.warning(f"Failed to send via client connection to {instance_id}: {e}", exc_info=True)
                del self.clients[instance_id]

        raise ConnectionError(f"No connection to instance {instance_id}")

    async def broadcast(self, message: Dict[str, Any], exclude_instances: Optional[List[str]] = None):
        """
        接続されているすべてのインスタンスにメッセージをブロードキャストします。

        Args:
            message: ブロードキャストするメッセージ
            exclude_instances: 除外するインスタンスIDのリスト
        """
        exclude_instances = exclude_instances or []
        message['from_instance'] = self.instance_id
        message['timestamp'] = datetime.now().isoformat()
        message_json = json.dumps(message)

        # サーバー接続にブロードキャスト
        for instance_id, connection in list(self.connections.items()):
            if instance_id not in exclude_instances:
                try:
                    await connection.send(message_json)
                    logger.debug(f"Broadcast sent to {instance_id} via server")
                except Exception as e:
                    logger.warning(f"Failed to broadcast to {instance_id}: {e}", exc_info=True)
                    del self.connections[instance_id]

        # クライアント接続にブロードキャスト
        for instance_id, client in list(self.clients.items()):
            if instance_id not in exclude_instances:
                try:
                    await client.send(message_json)
                    logger.debug(f"Broadcast sent to {instance_id} via client")
                except Exception as e:
                    logger.warning(f"Failed to broadcast to {instance_id}: {e}", exc_info=True)
                    del self.clients[instance_id]

    def add_message_handler(self, message_type: str, handler: Callable):
        """
        メッセージタイプ別のハンドラーを追加します。

        Args:
            message_type: メッセージタイプ
            handler: ハンドラー関数
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    def add_connection_handler(self, handler: Callable):
        """
        接続時のハンドラーを追加します。

        Args:
            handler: ハンドラー関数
        """
        self.connection_handlers.append(handler)

    def add_disconnection_handler(self, handler: Callable):
        """
        切断時のハンドラーを追加します。

        Args:
            handler: ハンドラー関数
        """
        self.disconnection_handlers.append(handler)

    async def _handle_client_connection(self, websocket: WebSocketServerProtocol):
        """
        新しいクライアント接続を処理します。
        """
        logger.info(f"New client connection from {websocket.remote_address}")
        instance_id = None

        try:
            # ハンドシェイクを待機
            handshake_data = await websocket.recv()
            handshake_msg = json.loads(handshake_data)

            if handshake_msg.get('type') != 'handshake':
                await websocket.close(code=1003, reason="Expected handshake")
                return

            instance_id = handshake_msg.get('instance_id')
            if not instance_id:
                await websocket.close(code=1003, reason="Instance ID required")
                return

            # ハンドシェイク応答を送信
            response = {
                'type': 'handshake_ack',
                'instance_id': self.instance_id,
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))

            self.connections[instance_id] = websocket
            logger.info(f"Instance {instance_id} connected")

            # 接続ハンドラーを呼び出し
            for handler in self.connection_handlers:
                await handler(instance_id)

            # メッセージを処理
            await self._handle_server_messages(instance_id, websocket)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {instance_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client connection: {e}", exc_info=True)
        finally:
            if instance_id and instance_id in self.connections:
                del self.connections[instance_id]
                # 切断ハンドラーを呼び出し
                for handler in self.disconnection_handlers:
                    await handler(instance_id)

    async def _handle_server_messages(self, instance_id: str, websocket: WebSocketServerProtocol):
        """
        サーバー接続からのメッセージを処理します。
        """
        async for message in websocket:
            try:
                await self._process_message(instance_id, message)
            except Exception as e:
                logger.error(f"Error processing message from {instance_id}: {e}", exc_info=True)

    async def _handle_client_messages(self, instance_id: str, websocket: WebSocketClientProtocol):
        """
        クライアント接続からのメッセージを処理します。
        """
        try:
            async for message in websocket:
                try:
                    await self._process_message(instance_id, message)
                except Exception as e:
                    logger.error(f"Error processing message from {instance_id}: {e}", exc_info=True)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection to {instance_id} closed")
        except Exception as e:
            logger.error(f"Error in client message handler for {instance_id}: {e}", exc_info=True)
        finally:
            if instance_id in self.clients:
                del self.clients[instance_id]
                # 切断ハンドラーを呼び出し
                for handler in self.disconnection_handlers:
                    await handler(instance_id)

    async def _process_message(self, from_instance: str, message: str):
        """
        受信メッセージを処理します。

        Args:
            from_instance: 送信元インスタンスID
            message: 受信メッセージ（JSON文字列）
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')

            if not message_type:
                logger.warning(f"Message without type from {from_instance}")
                return

            logger.debug(f"Received {message_type} message from {from_instance}")

            # メッセージハンドラーを呼び出し
            if message_type in self.message_handlers:
                for handler in self.message_handlers[message_type]:
                    await handler(data)
            else:
                logger.debug(f"No handler for message type: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {from_instance}: {message[:100]}...", exc_info=True)
        except Exception as e:
            logger.error(f"Error processing message from {from_instance}: {e}", exc_info=True)

    def get_connected_instances(self) -> List[str]:
        """
        接続されているインスタンスのリストを取得します。

        Returns:
            接続されているインスタンスIDのリスト
        """
        connected = set()
        connected.update(self.connections.keys())
        connected.update(self.clients.keys())
        return list(connected)

    def is_connected(self, instance_id: str) -> bool:
        """
        指定されたインスタンスに接続されているかを確認します。

        Args:
            instance_id: インスタンスID

        Returns:
            接続されている場合True
        """
        return instance_id in self.connections or instance_id in self.clients

    def get_network_status(self) -> Dict[str, Any]:
        """
        ネットワークの状態情報を取得します。

        Returns:
            ネットワーク状態の辞書
        """
        return {
            'instance_id': self.instance_id,
            'port': self.port,
            'is_running': self.is_running,
            'server_connections': len(self.connections),
            'client_connections': len(self.clients),
            'total_connections': len(self.connections) + len(self.clients),
            'connected_instances': self.get_connected_instances()
        }
