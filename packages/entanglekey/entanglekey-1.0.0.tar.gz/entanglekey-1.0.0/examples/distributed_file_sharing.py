#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntangleKey 分散ファイル共有システム例

量子もつれキーを使用したセキュアな分散ファイル共有システム。
複数のノード間でファイルを安全に共有・同期できます。
"""

import asyncio
import hashlib
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import base64

from entanglekey import EntangleKeyManager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileMetadata:
    """
    ファイルメタデータ
    """
    
    def __init__(self, filename: str, size: int, checksum: str, 
                 modified_time: datetime, owner: str):
        self.filename = filename
        self.size = size
        self.checksum = checksum
        self.modified_time = modified_time
        self.owner = owner
        self.version = 1
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            'filename': self.filename,
            'size': self.size,
            'checksum': self.checksum,
            'modified_time': self.modified_time.isoformat(),
            'owner': self.owner,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileMetadata':
        """辞書から作成"""
        return cls(
            filename=data['filename'],
            size=data['size'],
            checksum=data['checksum'],
            modified_time=datetime.fromisoformat(data['modified_time']),
            owner=data['owner']
        )


class SecureFileNode:
    """
    セキュアファイル共有ノード
    """
    
    def __init__(self, node_id: str, port: int, shared_dir: Optional[Path] = None):
        """
        ファイル共有ノードを初期化します。
        
        Args:
            node_id: ノードID
            port: ネットワークポート
            shared_dir: 共有ディレクトリ
        """
        self.node_id = node_id
        self.port = port
        self.shared_dir = shared_dir or Path(f"shared_{node_id}")
        self.shared_dir.mkdir(exist_ok=True)
        
        # EntangleKeyマネージャー
        self.manager = EntangleKeyManager(
            instance_id=f"filenode_{node_id}",
            network_port=port,
            key_length=256
        )
        
        # ファイル管理
        self.file_metadata: Dict[str, FileMetadata] = {}
        self.connected_nodes: Dict[str, str] = {}  # node_id -> instance_id
        self.session_keys: Dict[str, bytes] = {}   # node_id -> session_key
        self.pending_transfers: Set[str] = set()
        
        # 状態
        self.is_running = False
        
        # イベントハンドラーを設定
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """
        イベントハンドラーを設定します。
        """
        self.manager.add_instance_connected_callback(self._on_node_connected)
        self.manager.add_instance_disconnected_callback(self._on_node_disconnected)
        self.manager.add_key_generated_callback(self._on_key_established)
        
        # ファイル共有メッセージハンドラー
        self.manager.network_manager.add_message_handler('file_list_request', self._handle_file_list_request)
        self.manager.network_manager.add_message_handler('file_list_response', self._handle_file_list_response)
        self.manager.network_manager.add_message_handler('file_request', self._handle_file_request)
        self.manager.network_manager.add_message_handler('file_data', self._handle_file_data)
        self.manager.network_manager.add_message_handler('sync_request', self._handle_sync_request)
        self.manager.network_manager.add_message_handler('node_join', self._handle_node_join)
    
    async def start(self):
        """
        ファイル共有ノードを開始します。
        """
        await self.manager.start()
        self.is_running = True
        
        # 既存ファイルをスキャン
        await self._scan_existing_files()
        
        print(f"🚀 [{self.node_id}] ファイル共有ノードが開始されました")
        print(f"   共有ディレクトリ: {self.shared_dir.absolute()}")
        print(f"   ポート: {self.port}")
        print(f"   ファイル数: {len(self.file_metadata)}")
    
    async def stop(self):
        """
        ファイル共有ノードを停止します。
        """
        if self.is_running:
            await self.manager.stop()
            self.is_running = False
            print(f"🛑 [{self.node_id}] ファイル共有ノードが停止されました")
    
    async def connect_to_node(self, host: str, port: int) -> bool:
        """
        他のノードに接続します。
        
        Args:
            host: 接続先ホスト
            port: 接続先ポート
            
        Returns:
            接続成功フラグ
        """
        try:
            instance_id = await self.manager.connect_instance(host, port)
            
            # セッションキーを確立
            session_id = await self.manager.generate_session_key([instance_id])
            session_key = await self.manager.get_session_key(session_id)
            
            # ノード参加メッセージを送信
            await self._send_node_join(instance_id)
            
            print(f"🔗 [{self.node_id}] ノードに接続しました: {host}:{port}")
            return True
            
        except Exception as e:
            print(f"❌ [{self.node_id}] 接続に失敗: {host}:{port} - {e}")
            return False
    
    async def add_file(self, file_path: Path) -> bool:
        """
        ファイルを共有に追加します。
        
        Args:
            file_path: 追加するファイルのパス
            
        Returns:
            追加成功フラグ
        """
        if not file_path.exists():
            print(f"❌ [{self.node_id}] ファイルが見つかりません: {file_path}")
            return False
        
        try:
            # ファイルを共有ディレクトリにコピー
            target_path = self.shared_dir / file_path.name
            
            with open(file_path, 'rb') as src, open(target_path, 'wb') as dst:
                data = src.read()
                dst.write(data)
            
            # メタデータを作成
            checksum = hashlib.sha256(data).hexdigest()
            metadata = FileMetadata(
                filename=file_path.name,
                size=len(data),
                checksum=checksum,
                modified_time=datetime.fromtimestamp(file_path.stat().st_mtime),
                owner=self.node_id
            )
            
            self.file_metadata[file_path.name] = metadata
            
            print(f"✅ [{self.node_id}] ファイルを追加しました: {file_path.name}")
            
            # 他のノードに同期通知
            await self._notify_file_sync()
            
            return True
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイル追加エラー: {e}")
            return False
    
    async def download_file(self, filename: str, source_node: str) -> bool:
        """
        他のノードからファイルをダウンロードします。
        
        Args:
            filename: ダウンロードするファイル名
            source_node: ソースノードID
            
        Returns:
            ダウンロード成功フラグ
        """
        if source_node not in self.connected_nodes:
            print(f"❌ [{self.node_id}] ノードが接続されていません: {source_node}")
            return False
        
        if filename in self.pending_transfers:
            print(f"⏳ [{self.node_id}] ファイル転送が進行中です: {filename}")
            return False
        
        try:
            self.pending_transfers.add(filename)
            instance_id = self.connected_nodes[source_node]
            
            # ファイル要求メッセージを送信
            await self._send_encrypted_message(instance_id, {
                'type': 'file_request',
                'filename': filename,
                'requester': self.node_id
            }, source_node)
            
            print(f"📥 [{self.node_id}] ファイルダウンロードを要求しました: {filename} from {source_node}")
            return True
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイルダウンロード要求エラー: {e}")
            self.pending_transfers.discard(filename)
            return False
    
    async def list_remote_files(self, node_id: str) -> Optional[List[Dict]]:
        """
        リモートノードのファイル一覧を取得します。
        
        Args:
            node_id: ノードID
            
        Returns:
            ファイル一覧
        """
        if node_id not in self.connected_nodes:
            return None
        
        try:
            instance_id = self.connected_nodes[node_id]
            
            # ファイル一覧要求メッセージを送信
            await self._send_encrypted_message(instance_id, {
                'type': 'file_list_request',
                'requester': self.node_id
            }, node_id)
            
            # 応答を待機（簡略化）
            await asyncio.sleep(1)
            
            return []  # 実際の実装では応答を待機して返す
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイル一覧取得エラー: {e}")
            return None
    
    async def sync_with_network(self):
        """
        ネットワーク全体と同期します。
        """
        print(f"🔄 [{self.node_id}] ネットワーク同期を開始...")
        
        for node_id in self.connected_nodes:
            try:
                await self.list_remote_files(node_id)
            except Exception as e:
                print(f"❌ [{self.node_id}] {node_id} との同期に失敗: {e}")
        
        print(f"✅ [{self.node_id}] ネットワーク同期完了")
    
    def get_file_list(self) -> List[Dict]:
        """
        ローカルファイル一覧を取得します。
        
        Returns:
            ファイル一覧
        """
        return [metadata.to_dict() for metadata in self.file_metadata.values()]
    
    def get_status(self) -> Dict:
        """
        ノードの状態を取得します。
        
        Returns:
            ノード状態
        """
        return {
            'node_id': self.node_id,
            'port': self.port,
            'connected_nodes': list(self.connected_nodes.keys()),
            'total_files': len(self.file_metadata),
            'shared_directory': str(self.shared_dir.absolute()),
            'pending_transfers': len(self.pending_transfers),
            'is_running': self.is_running
        }
    
    async def _scan_existing_files(self):
        """
        既存ファイルをスキャンしてメタデータを作成します。
        """
        for file_path in self.shared_dir.glob('*'):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    checksum = hashlib.sha256(data).hexdigest()
                    metadata = FileMetadata(
                        filename=file_path.name,
                        size=len(data),
                        checksum=checksum,
                        modified_time=datetime.fromtimestamp(file_path.stat().st_mtime),
                        owner=self.node_id
                    )
                    
                    self.file_metadata[file_path.name] = metadata
                    
                except Exception as e:
                    print(f"❌ [{self.node_id}] ファイルスキャンエラー: {file_path.name} - {e}")
    
    async def _send_encrypted_message(self, instance_id: str, message_data: Dict, target_node: str):
        """
        暗号化されたメッセージを送信します。
        """
        if target_node not in self.session_keys:
            return
        
        session_key = self.session_keys[target_node]
        
        # メッセージを暗号化
        message_json = json.dumps(message_data).encode()
        encrypted_data, nonce = self.manager.key_generator.encrypt_data(message_json, session_key)
        signature = self.manager.key_generator.create_message_signature(message_json, session_key)
        
        encrypted_message = {
            'type': message_data['type'],
            'encrypted_data': encrypted_data.hex(),
            'nonce': nonce.hex(),
            'signature': signature.hex(),
            'sender': self.node_id
        }
        
        await self.manager.network_manager.send_to_instance(instance_id, encrypted_message)
    
    async def _send_node_join(self, instance_id: str):
        """
        ノード参加メッセージを送信します。
        """
        join_message = {
            'type': 'node_join',
            'node_id': self.node_id,
            'timestamp': datetime.now().isoformat()
        }
        await self.manager.network_manager.send_to_instance(instance_id, join_message)
    
    async def _notify_file_sync(self):
        """
        ファイル同期通知をブロードキャストします。
        """
        sync_message = {
            'type': 'sync_request',
            'node_id': self.node_id,
            'file_count': len(self.file_metadata),
            'timestamp': datetime.now().isoformat()
        }
        await self.manager.network_manager.broadcast(sync_message)
    
    async def _on_node_connected(self, instance_id: str):
        """
        ノード接続時のコールバック
        """
        print(f"🔗 [{self.node_id}] 新しい接続: {instance_id}")
    
    async def _on_node_disconnected(self, instance_id: str):
        """
        ノード切断時のコールバック
        """
        # 切断されたノードを特定
        disconnected_node = None
        for node_id, inst_id in self.connected_nodes.items():
            if inst_id == instance_id:
                disconnected_node = node_id
                break
        
        if disconnected_node:
            print(f"❌ [{self.node_id}] {disconnected_node} が切断されました")
            del self.connected_nodes[disconnected_node]
            if disconnected_node in self.session_keys:
                del self.session_keys[disconnected_node]
    
    async def _on_key_established(self, session_id: str, key: bytes):
        """
        キー確立時のコールバック
        """
        print(f"🔑 [{self.node_id}] セキュアキーが確立されました: {session_id[:8]}...")
    
    async def _handle_node_join(self, message: Dict):
        """
        ノード参加の処理
        """
        node_id = message.get('node_id')
        from_instance = message.get('from_instance')
        
        if node_id and from_instance:
            self.connected_nodes[node_id] = from_instance
            
            # セッションキーを確立
            try:
                session_id = await self.manager.generate_session_key([from_instance])
                session_key = await self.manager.get_session_key(session_id)
                self.session_keys[node_id] = session_key
                
                print(f"✅ [{self.node_id}] {node_id} がネットワークに参加しました")
                
            except Exception as e:
                print(f"❌ [{self.node_id}] {node_id} とのキー確立に失敗: {e}")
    
    async def _handle_file_list_request(self, message: Dict):
        """
        ファイル一覧要求の処理
        """
        try:
            requester = message.get('sender')
            if requester not in self.session_keys:
                return
            
            # 暗号化されたメッセージを復号化
            session_key = self.session_keys[requester]
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            request_data = json.loads(decrypted_data.decode())
            
            # ファイル一覧を送信
            file_list = self.get_file_list()
            instance_id = self.connected_nodes[requester]
            
            await self._send_encrypted_message(instance_id, {
                'type': 'file_list_response',
                'files': file_list,
                'responder': self.node_id
            }, requester)
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイル一覧要求処理エラー: {e}")
    
    async def _handle_file_list_response(self, message: Dict):
        """
        ファイル一覧応答の処理
        """
        try:
            sender = message.get('sender')
            if sender not in self.session_keys:
                return
            
            # 暗号化されたメッセージを復号化
            session_key = self.session_keys[sender]
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            response_data = json.loads(decrypted_data.decode())
            
            # ファイル一覧を表示
            files = response_data.get('files', [])
            print(f"📁 [{self.node_id}] {sender} のファイル一覧:")
            for file_info in files:
                print(f"  - {file_info['filename']} ({file_info['size']} bytes, {file_info['owner']})")
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイル一覧応答処理エラー: {e}")
    
    async def _handle_file_request(self, message: Dict):
        """
        ファイル要求の処理
        """
        try:
            sender = message.get('sender')
            if sender not in self.session_keys:
                return
            
            # 暗号化されたメッセージを復号化
            session_key = self.session_keys[sender]
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            request_data = json.loads(decrypted_data.decode())
            
            filename = request_data.get('filename')
            if filename in self.file_metadata:
                # ファイルを読み込んで送信
                file_path = self.shared_dir / filename
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # ファイルデータをBase64エンコード
                    encoded_data = base64.b64encode(file_data).decode()
                    metadata = self.file_metadata[filename]
                    
                    instance_id = self.connected_nodes[sender]
                    await self._send_encrypted_message(instance_id, {
                        'type': 'file_data',
                        'filename': filename,
                        'data': encoded_data,
                        'metadata': metadata.to_dict(),
                        'sender': self.node_id
                    }, sender)
                    
                    print(f"📤 [{self.node_id}] ファイルを送信しました: {filename} → {sender}")
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイル要求処理エラー: {e}")
    
    async def _handle_file_data(self, message: Dict):
        """
        ファイルデータの処理
        """
        try:
            sender = message.get('sender')
            if sender not in self.session_keys:
                return
            
            # 暗号化されたメッセージを復号化
            session_key = self.session_keys[sender]
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            file_data = json.loads(decrypted_data.decode())
            
            filename = file_data.get('filename')
            encoded_data = file_data.get('data')
            metadata_dict = file_data.get('metadata')
            
            if filename and encoded_data and metadata_dict:
                # ファイルデータをデコード
                file_content = base64.b64decode(encoded_data)
                
                # チェックサムを検証
                checksum = hashlib.sha256(file_content).hexdigest()
                if checksum != metadata_dict['checksum']:
                    print(f"❌ [{self.node_id}] ファイル破損検出: {filename}")
                    return
                
                # ファイルを保存
                file_path = self.shared_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                
                # メタデータを保存
                metadata = FileMetadata.from_dict(metadata_dict)
                self.file_metadata[filename] = metadata
                
                # 転送完了
                self.pending_transfers.discard(filename)
                
                print(f"📥 [{self.node_id}] ファイルを受信しました: {filename} ({len(file_content)} bytes)")
            
        except Exception as e:
            print(f"❌ [{self.node_id}] ファイルデータ処理エラー: {e}")
    
    async def _handle_sync_request(self, message: Dict):
        """
        同期要求の処理
        """
        sender_node = message.get('node_id')
        file_count = message.get('file_count', 0)
        
        if sender_node:
            print(f"🔄 [{self.node_id}] {sender_node} から同期要求 (ファイル数: {file_count})")


async def multi_node_demo():
    """
    複数ノードによるファイル共有デモ
    """
    print("=" * 60)
    print("EntangleKey 分散ファイル共有システム デモ")
    print("=" * 60)
    
    # テンポラリディレクトリを作成
    temp_dir = Path(tempfile.mkdtemp())
    print(f"テンポラリディレクトリ: {temp_dir}")
    
    try:
        # 3つのノードを作成
        node_a = SecureFileNode("NodeA", 8881, temp_dir / "nodeA")
        node_b = SecureFileNode("NodeB", 8882, temp_dir / "nodeB")
        node_c = SecureFileNode("NodeC", 8883, temp_dir / "nodeC")
        
        # ノードを開始
        await node_a.start()
        await node_b.start()
        await node_c.start()
        
        # テストファイルを作成
        test_file_a = temp_dir / "test_file_a.txt"
        test_file_b = temp_dir / "test_file_b.txt"
        
        with open(test_file_a, 'w') as f:
            f.write("これはNodeAのテストファイルです。\n量子もつれキーで安全に共有されています。")
        
        with open(test_file_b, 'w') as f:
            f.write("これはNodeBのテストファイルです。\n分散ファイル共有システムのデモです。")
        
        # ファイルを各ノードに追加
        await node_a.add_file(test_file_a)
        await node_b.add_file(test_file_b)
        
        print("\n📁 ファイルを各ノードに追加しました")
        
        # ノード間を接続
        await asyncio.sleep(1)
        await node_b.connect_to_node("localhost", 8881)  # B -> A
        await asyncio.sleep(1)
        await node_c.connect_to_node("localhost", 8881)  # C -> A
        await asyncio.sleep(1)
        await node_c.connect_to_node("localhost", 8882)  # C -> B
        
        print("\n🔗 ノード間の接続が確立されました")
        await asyncio.sleep(2)
        
        # ファイル共有のデモ
        print("\n📥 ファイル共有のデモ:")
        
        # NodeCがNodeAのファイルをダウンロード
        await node_c.download_file("test_file_a.txt", "NodeA")
        await asyncio.sleep(2)
        
        # NodeCがNodeBのファイルをダウンロード
        await node_c.download_file("test_file_b.txt", "NodeB")
        await asyncio.sleep(2)
        
        # NodeAがNodeBのファイルをダウンロード
        await node_a.download_file("test_file_b.txt", "NodeB")
        await asyncio.sleep(2)
        
        # 最終状態を表示
        print("\n📊 最終状態:")
        for node in [node_a, node_b, node_c]:
            status = node.get_status()
            print(f"  {status['node_id']}:")
            print(f"    接続ノード: {', '.join(status['connected_nodes'])}")
            print(f"    ファイル数: {status['total_files']}")
            print(f"    共有ディレクトリ: {status['shared_directory']}")
        
        await asyncio.sleep(1)
        
    finally:
        # クリーンアップ
        await node_a.stop()
        await node_b.stop()
        await node_c.stop()
        
        # テンポラリディレクトリを削除
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n✅ デモ完了 (テンポラリディレクトリを削除: {temp_dir})")


async def interactive_file_node(node_id: str, port: int):
    """
    インタラクティブなファイル共有ノード
    
    Args:
        node_id: ノードID
        port: ポート番号
    """
    shared_dir = Path(f"shared_{node_id}")
    node = SecureFileNode(node_id, port, shared_dir)
    
    try:
        await node.start()
        
        print(f"""
📁 EntangleKey 分散ファイル共有ノード
ノードID: {node_id}
ポート: {port}
共有ディレクトリ: {shared_dir.absolute()}

コマンド:
  /connect <host> <port>    - 他のノードに接続
  /add <file_path>          - ファイルを共有に追加
  /download <filename> <node> - ファイルをダウンロード
  /list [node_id]           - ファイル一覧を表示
  /sync                     - ネットワーク同期
  /status                   - ノード状態を表示
  /quit                     - ノードを終了
        """)
        
        # 非同期で入力を処理
        input_task = asyncio.create_task(handle_file_node_input(node))
        
        # メインループ
        try:
            while node.is_running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+Cが押されました")
        finally:
            input_task.cancel()
            await node.stop()
    
    except Exception as e:
        print(f"❌ ノードエラー: {e}")
        await node.stop()


async def handle_file_node_input(node: SecureFileNode):
    """
    ファイルノードの入力を処理します（非同期）
    """
    loop = asyncio.get_event_loop()
    
    while node.is_running:
        try:
            # 非同期で入力を取得
            user_input = await loop.run_in_executor(None, input, "📁 > ")
            
            if not user_input.strip():
                continue
            
            await process_file_node_command(node, user_input)
                
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"❌ 入力処理エラー: {e}")


async def process_file_node_command(node: SecureFileNode, command: str):
    """
    ファイルノードのコマンドを処理します。
    """
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == '/connect' and len(parts) >= 3:
        host = parts[1]
        try:
            port = int(parts[2])
            await node.connect_to_node(host, port)
        except ValueError:
            print("❌ 無効なポート番号")
    
    elif cmd == '/add' and len(parts) >= 2:
        file_path = Path(parts[1])
        await node.add_file(file_path)
    
    elif cmd == '/download' and len(parts) >= 3:
        filename = parts[1]
        source_node = parts[2]
        await node.download_file(filename, source_node)
    
    elif cmd == '/list':
        if len(parts) >= 2:
            # リモートノードのファイル一覧
            node_id = parts[1]
            await node.list_remote_files(node_id)
        else:
            # ローカルファイル一覧
            files = node.get_file_list()
            print(f"📁 ローカルファイル一覧:")
            if files:
                for file_info in files:
                    print(f"  - {file_info['filename']} ({file_info['size']} bytes, {file_info['owner']})")
            else:
                print("  (ファイルなし)")
    
    elif cmd == '/sync':
        await node.sync_with_network()
    
    elif cmd == '/status':
        status = node.get_status()
        print(f"📊 ノード状態:")
        print(f"  ノードID: {status['node_id']}")
        print(f"  接続ノード: {', '.join(status['connected_nodes']) or 'なし'}")
        print(f"  ファイル数: {status['total_files']}")
        print(f"  転送中: {status['pending_transfers']}")
    
    elif cmd == '/quit':
        node.is_running = False
        print("👋 ノードを終了します...")
    
    else:
        print("❌ 不明なコマンド。使用可能: /connect, /add, /download, /list, /sync, /status, /quit")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 3:
        # インタラクティブモード
        node_id = sys.argv[1]
        port = int(sys.argv[2])
        asyncio.run(interactive_file_node(node_id, port))
    else:
        # デモモード
        asyncio.run(multi_node_demo())
