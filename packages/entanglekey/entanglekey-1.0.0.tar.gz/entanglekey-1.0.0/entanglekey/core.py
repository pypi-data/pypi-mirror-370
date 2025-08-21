"""
EntangleKey コアモジュール

分散セッションキー生成の中心となるマネージャークラスを提供します。
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta

from .quantum import QuantumEntanglementSimulator
from .network import NetworkManager
from .crypto import SessionKeyGenerator
from .exceptions import EntangleKeyError, SynchronizationError
from .config import EntangleKeyConfig
from .config_loader import ConfigLoader
from .security_monitor import SecurityMonitor, QuantumSecurityValidator
from .logging_config import setup_logging, StructuredLogger


logger = logging.getLogger(__name__)


class EntangleKeyManager:
    """
    量子もつれベースの分散セッションキー生成マネージャー
    
    複数のプログラムインスタンス間でセッションキーの生成・同期を管理します。
    """

    def __init__(
        self,
        instance_id: Optional[str] = None,
        network_port: int = 8888,
        key_length: int = 256,
        sync_timeout: float = 30.0,
        config: Optional[EntangleKeyConfig] = None,
        config_file: Optional[str] = None,
    ):
        """
        EntangleKeyManagerを初期化します。

        Args:
            instance_id: インスタンスの一意識別子（自動生成可能）
            network_port: ネットワーク通信用ポート
            key_length: 生成するセッションキーの長さ（ビット）
            sync_timeout: 同期タイムアウト時間（秒）
            config: 詳細設定（オプション）
            config_file: 設定ファイルのパス（オプション）
        """
        # 設定の優先順位: config > config_file > デフォルト設定 > 個別パラメータ
        if config is None:
            if config_file:
                config = ConfigLoader.load_from_file(config_file)
            else:
                config = ConfigLoader.load_default_config()
            
            # 個別パラメータが指定されている場合は上書き
            if network_port != 8888:
                config.network.port = network_port
                config.network.default_port = network_port
            if key_length != 256:
                config.crypto.key_length = key_length
                config.crypto.default_key_length = key_length
            
        self.config = config
        self.instance_id = instance_id or str(uuid.uuid4())
        self.network_port = network_port
        self.key_length = key_length
        self.sync_timeout = sync_timeout

        # コンポーネントの初期化
        self.quantum_sim = QuantumEntanglementSimulator(self.config.quantum)
        self.network_manager = NetworkManager(self.instance_id, network_port)
        self.key_generator = SessionKeyGenerator(key_length)

        # セキュリティ監視システム
        self.security_monitor = SecurityMonitor(self.config.security)
        self.security_validator = QuantumSecurityValidator(self.security_monitor)
        self.structured_logger = StructuredLogger(f"entanglekey.manager.{self.instance_id}")

        # 状態管理
        self.connected_instances: Dict[str, Any] = {}
        self.session_keys: Dict[str, bytes] = {}
        self.entanglement_states: Dict[str, Any] = {}
        self.is_running = False
        self.sync_acknowledgements: Dict[str, asyncio.Future] = {}  # 追加
        
        # イベントハンドラー
        self.key_generated_callbacks: List[Callable] = []
        self.instance_connected_callbacks: List[Callable] = []
        self.instance_disconnected_callbacks: List[Callable] = []
        
        # セキュリティアラートハンドラー
        self.security_monitor.add_alert_callback(self._handle_security_alert)

    async def start(self):
        """
        EntangleKeyManagerを開始します。
        """
        if self.is_running:
            logger.warning("EntangleKeyManager is already running")
            return

        logger.info(f"Starting EntangleKeyManager (ID: {self.instance_id})")
        
        try:
            # ログシステムを初期化
            setup_logging(logging.INFO, self.config.security)
            
            await self.network_manager.start()
            await self.security_monitor.start()
            self._setup_event_handlers()
            self.is_running = True
            
            self.structured_logger.info(
                "EntangleKeyManager started successfully",
                instance_id=self.instance_id,
                network_port=self.network_port,
                key_length=self.key_length
            )
        except Exception as e:
            logger.error(f"Failed to start EntangleKeyManager: {e}", exc_info=True)
            raise EntangleKeyError("Failed to start EntangleKeyManager due to an internal error.")

    async def stop(self):
        """
        EntangleKeyManagerを停止します。
        """
        if not self.is_running:
            return

        logger.info("Stopping EntangleKeyManager")
        
        try:
            await self.network_manager.stop()
            await self.security_monitor.stop()
            self.is_running = False
            self.connected_instances.clear()
            self.session_keys.clear()
            self.entanglement_states.clear()
            
            self.structured_logger.info(
                "EntangleKeyManager stopped",
                instance_id=self.instance_id
            )
        except Exception as e:
            logger.error(f"Error stopping EntangleKeyManager: {e}", exc_info=True)

    async def connect_instance(self, target_host: str, target_port: int) -> str:
        """
        他のインスタンスに接続します。

        Args:
            target_host: 接続先ホスト
            target_port: 接続先ポート

        Returns:
            接続したインスタンスのID
        """
        try:
            instance_id = await self.network_manager.connect(target_host, target_port)
            self.connected_instances[instance_id] = {
                'host': target_host,
                'port': target_port,
                'connected_at': datetime.now(),
            }
            
            logger.info(f"Connected to instance {instance_id}")
            
            # イベント通知
            for callback in self.instance_connected_callbacks:
                await callback(instance_id)
                
            return instance_id
        except Exception as e:
            logger.error(f"Failed to connect to {target_host}:{target_port}: {e}", exc_info=True)
            raise EntangleKeyError(f"Connection to {target_host}:{target_port} failed.")

    async def generate_session_key(self, partner_instances: List[str]) -> str:
        """
        指定されたインスタンスとの間でセッションキーを生成します。

        Args:
            partner_instances: パートナーインスタンスのIDリスト

        Returns:
            生成されたセッションのID
        """
        if not self.is_running:
            raise EntangleKeyError("EntangleKeyManager is not running")

        session_id = str(uuid.uuid4())
        
        try:
            # 量子もつれ状態をシミュレート
            entanglement_state = await self.quantum_sim.create_entanglement(
                [self.instance_id] + partner_instances
            )
            
            # セッションキーを生成
            session_key = await self.key_generator.generate_key(
                entanglement_state, partner_instances
            )
            
            # キー同期プロセスを開始
            await self._synchronize_key(session_id, session_key, partner_instances)
            
            self.session_keys[session_id] = session_key
            self.entanglement_states[session_id] = entanglement_state
            
            logger.info(f"Session key generated: {session_id}")
            
            # イベント通知
            for callback in self.key_generated_callbacks:
                await callback(session_id, session_key)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to generate session key: {e}", exc_info=True)
            raise EntangleKeyError("Key generation failed due to an internal error.")

    async def get_session_key(self, session_id: str) -> Optional[bytes]:
        """
        指定されたセッションのキーを取得します。

        Args:
            session_id: セッションID

        Returns:
            セッションキー（存在しない場合はNone）
        """
        return self.session_keys.get(session_id)

    async def revoke_session_key(self, session_id: str):
        """
        指定されたセッションキーを破棄します。

        Args:
            session_id: セッションID
        """
        if session_id in self.session_keys:
            del self.session_keys[session_id]
            del self.entanglement_states[session_id]
            
            # パートナーインスタンスにも破棄を通知
            await self.network_manager.broadcast({
                'type': 'key_revoked',
                'session_id': session_id,
                'from_instance': self.instance_id
            })
            
            logger.info(f"Session key revoked: {session_id}")

    def add_key_generated_callback(self, callback: Callable):
        """キー生成時のコールバックを追加します。"""
        self.key_generated_callbacks.append(callback)

    def add_instance_connected_callback(self, callback: Callable):
        """インスタンス接続時のコールバックを追加します。"""
        self.instance_connected_callbacks.append(callback)

    def add_instance_disconnected_callback(self, callback: Callable):
        """インスタンス切断時のコールバックを追加します。"""
        self.instance_disconnected_callbacks.append(callback)

    async def _synchronize_key(self, session_id: str, session_key: bytes, partner_instances: List[str]):
        """
        セッションキーを他のインスタンスと同期します。
        """
        sync_message = {
            'type': 'key_sync',
            'session_id': session_id,
            'key_hash': self.key_generator.hash_key(session_key),
            'from_instance': self.instance_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # 同期確認を待つ Future を用意
        ack_futures = []
        for instance_id in partner_instances:
            future = asyncio.Future()
            self.sync_acknowledgements[f"{session_id}:{instance_id}"] = future
            ack_futures.append(future)

        # パートナーインスタンスに同期メッセージを送信
        for instance_id in partner_instances:
            try:
                await self.network_manager.send_to_instance(instance_id, sync_message)
            except Exception as e:
                logger.warning(f"Failed to send sync message to {instance_id}: {e}")
                # 送信失敗したインスタンスの Future をキャンセル
                future_key = f"{session_id}:{instance_id}"
                if future_key in self.sync_acknowledgements:
                    self.sync_acknowledgements[future_key].set_exception(
                        SynchronizationError(f"Failed to send sync to {instance_id}")
                    )

        # すべてのパートナーからの ACK を待つ
        try:
            await asyncio.wait_for(
                asyncio.gather(*ack_futures, return_exceptions=True),
                timeout=self.sync_timeout
            )
            
            success_count = sum(1 for f in ack_futures if f.done() and not f.exception())
            
            if success_count < len(partner_instances):
                 logger.warning(f"Only {success_count}/{len(partner_instances)} instances acknowledged sync.")
            
            if success_count == 0:
                raise SynchronizationError("Failed to sync with any partner instance")

            logger.info(f"Key synchronized with {success_count}/{len(partner_instances)} instances")

        except asyncio.TimeoutError:
            logger.error(f"Synchronization timed out for session {session_id}")
            raise SynchronizationError(f"Synchronization timed out for session {session_id}")
        finally:
            # Future をクリーンアップ
            for instance_id in partner_instances:
                del self.sync_acknowledgements[f"{session_id}:{instance_id}"]

    def _setup_event_handlers(self):
        """
        ネットワークイベントのハンドラーを設定します。
        """
        self.network_manager.add_message_handler('key_sync', self._handle_key_sync)
        self.network_manager.add_message_handler('sync_ack', self._handle_sync_ack) # 追加
        self.network_manager.add_message_handler('key_revoked', self._handle_key_revoked)
        self.network_manager.add_connection_handler(self._handle_instance_connected)
        self.network_manager.add_disconnection_handler(self._handle_instance_disconnected)

    async def _handle_key_sync(self, message: Dict[str, Any]):
        """キー同期メッセージのハンドラー"""
        session_id = message['session_id']
        key_hash = message['key_hash']
        from_instance = message['from_instance']
        
        logger.info(f"Received key sync from {from_instance} for session {session_id}")
        
        # 同期確認を送信
        await self.network_manager.send_to_instance(from_instance, {
            'type': 'sync_ack',
            'session_id': session_id,
            'from_instance': self.instance_id
        })

    async def _handle_sync_ack(self, message: Dict[str, Any]):
        """同期確認(ACK)メッセージのハンドラー"""
        session_id = message.get('session_id')
        from_instance = message.get('from_instance')
        
        future_key = f"{session_id}:{from_instance}"
        if future_key in self.sync_acknowledgements:
            self.sync_acknowledgements[future_key].set_result(True)
            logger.debug(f"Sync ACK received from {from_instance} for session {session_id}")

    async def _handle_key_revoked(self, message: Dict[str, Any]):
        """キー破棄メッセージのハンドラー"""
        session_id = message['session_id']
        from_instance = message['from_instance']
        
        if session_id in self.session_keys:
            del self.session_keys[session_id]
            del self.entanglement_states[session_id]
            logger.info(f"Session key {session_id} revoked by {from_instance}")

    async def _handle_instance_connected(self, instance_id: str):
        """インスタンス接続ハンドラー"""
        for callback in self.instance_connected_callbacks:
            await callback(instance_id)

    async def _handle_instance_disconnected(self, instance_id: str):
        """インスタンス切断ハンドラー"""
        if instance_id in self.connected_instances:
            del self.connected_instances[instance_id]
        
        for callback in self.instance_disconnected_callbacks:
            await callback(instance_id)

    def get_status(self) -> Dict[str, Any]:
        """
        現在のステータスを取得します。

        Returns:
            ステータス情報の辞書
        """
        status = {
            'instance_id': self.instance_id,
            'is_running': self.is_running,
            'connected_instances': len(self.connected_instances),
            'active_sessions': len(self.session_keys),
            'network_port': self.network_port
        }
        
        # セキュリティメトリクスを追加
        if hasattr(self, 'security_monitor'):
            security_metrics = self.security_monitor.get_security_metrics()
            status['security'] = {
                'entanglement_correlation': security_metrics.entanglement_correlation,
                'entropy_quality': security_metrics.entropy_quality,
                'network_integrity': security_metrics.network_integrity,
                'key_freshness': security_metrics.key_freshness,
                'attack_attempts': security_metrics.attack_attempts,
                'failed_correlations': security_metrics.failed_correlations
            }
        
        return status

    async def _handle_security_alert(self, alert_data: Dict[str, Any]):
        """
        セキュリティアラートを処理します。
        
        Args:
            alert_data: アラートデータ
        """
        alert_type = alert_data.get('type')
        self.structured_logger.warning(
            f"Security alert: {alert_type}",
            alert_type=alert_type,
            alert_details=alert_data.get('details', {}),
            instance_id=self.instance_id
        )
        
        # 重大なアラートの場合は自動的に対応
        if alert_type == 'potential_eavesdropping':
            # すべてのセッションキーを無効化
            await self._emergency_key_revocation(alert_data)
        elif alert_type == 'excessive_connections':
            # 疑わしい接続をブロック
            await self._block_suspicious_connection(alert_data)

    async def _emergency_key_revocation(self, alert_data: Dict[str, Any]):
        """
        緊急時のキー無効化処理
        
        Args:
            alert_data: アラートデータ
        """
        self.structured_logger.error(
            "Emergency key revocation triggered",
            reason=alert_data.get('type'),
            instance_id=self.instance_id
        )
        
        # すべてのアクティブなセッションキーを破棄
        sessions_to_revoke = list(self.session_keys.keys())
        for session_id in sessions_to_revoke:
            await self.revoke_session_key(session_id)

    async def _block_suspicious_connection(self, alert_data: Dict[str, Any]):
        """
        疑わしい接続をブロックする処理
        
        Args:
            alert_data: アラートデータ
        """
        details = alert_data.get('details', {})
        source_ip = details.get('source_ip')
        
        if source_ip:
            self.structured_logger.warning(
                f"Blocking suspicious connection from {source_ip}",
                source_ip=source_ip,
                instance_id=self.instance_id
            )
            # 実際のブロック処理はネットワークレベルで実装する必要があります
