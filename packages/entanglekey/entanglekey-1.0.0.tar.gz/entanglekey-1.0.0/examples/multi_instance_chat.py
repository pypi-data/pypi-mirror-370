#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntangleKey 多インスタンス・リアルタイムチャット例

量子もつれキーを使用したセキュアなリアルタイムチャットシステム。
複数のユーザーが安全にメッセージを交換できます。
"""

import asyncio
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from entanglekey import EntangleKeyManager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureChatNode:
    """
    セキュアチャットノード（参加者）
    """
    
    def __init__(self, username: str, port: int):
        """
        チャットノードを初期化します。
        
        Args:
            username: ユーザー名
            port: ネットワークポート
        """
        self.username = username
        self.port = port
        self.manager = EntangleKeyManager(
            instance_id=f"chat_{username}",
            network_port=port,
            key_length=256
        )
        
        # チャット管理
        self.connected_users: Dict[str, str] = {}  # username -> instance_id
        self.session_keys: Dict[str, bytes] = {}   # username -> session_key
        self.message_history: List[Dict] = []
        self.is_running = False
        
        # イベントハンドラーを設定
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """
        イベントハンドラーを設定します。
        """
        self.manager.add_instance_connected_callback(self._on_user_connected)
        self.manager.add_instance_disconnected_callback(self._on_user_disconnected)
        self.manager.add_key_generated_callback(self._on_key_established)
        self.manager.network_manager.add_message_handler('chat_message', self._handle_chat_message)
        self.manager.network_manager.add_message_handler('user_join', self._handle_user_join)
        self.manager.network_manager.add_message_handler('user_leave', self._handle_user_leave)
    
    async def start(self):
        """
        チャットノードを開始します。
        """
        await self.manager.start()
        self.is_running = True
        print(f"🚀 [{self.username}] チャットノードが開始されました (ポート: {self.port})")
    
    async def stop(self):
        """
        チャットノードを停止します。
        """
        if self.is_running:
            # 退出メッセージを送信
            await self._broadcast_user_leave()
            await self.manager.stop()
            self.is_running = False
            print(f"🛑 [{self.username}] チャットノードが停止されました")
    
    async def connect_to_user(self, host: str, port: int) -> bool:
        """
        他のユーザーに接続します。
        
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
            
            # ユーザー参加メッセージを送信
            await self._send_user_join(instance_id)
            
            print(f"🔗 [{self.username}] ユーザーに接続しました: {host}:{port}")
            return True
            
        except Exception as e:
            print(f"❌ [{self.username}] 接続に失敗: {host}:{port} - {e}")
            return False
    
    async def send_message(self, message: str):
        """
        メッセージを全員に送信します。
        
        Args:
            message: 送信するメッセージ
        """
        if not self.connected_users:
            print(f"❌ [{self.username}] 接続されているユーザーがいません")
            return
        
        timestamp = datetime.now()
        chat_message = {
            'type': 'chat_message',
            'username': self.username,
            'message': message,
            'timestamp': timestamp.isoformat()
        }
        
        # 各ユーザーに暗号化してメッセージを送信
        for username, instance_id in self.connected_users.items():
            if username in self.session_keys:
                try:
                    await self._send_encrypted_message(instance_id, chat_message)
                except Exception as e:
                    print(f"❌ [{self.username}] メッセージ送信失敗 -> {username}: {e}")
        
        # 自分のメッセージ履歴に追加
        self.message_history.append({
            'username': self.username,
            'message': message,
            'timestamp': timestamp,
            'direction': 'sent'
        })
        
        print(f"💬 [{self.username}] {message}")
    
    async def _send_encrypted_message(self, instance_id: str, message_data: Dict):
        """
        暗号化されたメッセージを送信します。
        """
        username = self._get_username_by_instance(instance_id)
        if not username or username not in self.session_keys:
            return
        
        session_key = self.session_keys[username]
        
        # メッセージを暗号化
        message_json = json.dumps(message_data).encode()
        encrypted_data, nonce = self.manager.key_generator.encrypt_data(message_json, session_key)
        signature = self.manager.key_generator.create_message_signature(message_json, session_key)
        
        encrypted_message = {
            'type': 'chat_message',
            'encrypted_data': encrypted_data.hex(),
            'nonce': nonce.hex(),
            'signature': signature.hex(),
            'sender': self.username
        }
        
        await self.manager.network_manager.send_to_instance(instance_id, encrypted_message)
    
    async def _send_user_join(self, instance_id: str):
        """
        ユーザー参加メッセージを送信します。
        """
        join_message = {
            'type': 'user_join',
            'username': self.username,
            'timestamp': datetime.now().isoformat()
        }
        await self.manager.network_manager.send_to_instance(instance_id, join_message)
    
    async def _broadcast_user_leave(self):
        """
        ユーザー退出メッセージをブロードキャストします。
        """
        leave_message = {
            'type': 'user_leave',
            'username': self.username,
            'timestamp': datetime.now().isoformat()
        }
        await self.manager.network_manager.broadcast(leave_message)
    
    async def _on_user_connected(self, instance_id: str):
        """
        ユーザー接続時のコールバック
        """
        print(f"🔗 [{self.username}] 新しい接続: {instance_id}")
    
    async def _on_user_disconnected(self, instance_id: str):
        """
        ユーザー切断時のコールバック
        """
        username = self._get_username_by_instance(instance_id)
        if username:
            print(f"❌ [{self.username}] {username} が切断されました")
            del self.connected_users[username]
            if username in self.session_keys:
                del self.session_keys[username]
    
    async def _on_key_established(self, session_id: str, key: bytes):
        """
        キー確立時のコールバック
        """
        print(f"🔑 [{self.username}] セキュアキーが確立されました: {session_id[:8]}...")
    
    async def _handle_chat_message(self, message: Dict):
        """
        チャットメッセージの処理
        """
        try:
            sender = message.get('sender')
            if sender not in self.session_keys:
                return
            
            session_key = self.session_keys[sender]
            
            # メッセージを復号化
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            signature = bytes.fromhex(message['signature'])
            
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            
            # 署名を検証
            if not self.manager.key_generator.verify_message_signature(
                decrypted_data, signature, session_key
            ):
                print(f"❌ [{self.username}] 無効な署名: {sender}")
                return
            
            # メッセージデータを復元
            chat_data = json.loads(decrypted_data.decode())
            
            # メッセージ履歴に追加
            self.message_history.append({
                'username': chat_data['username'],
                'message': chat_data['message'],
                'timestamp': datetime.fromisoformat(chat_data['timestamp']),
                'direction': 'received'
            })
            
            # メッセージを表示
            timestamp = datetime.fromisoformat(chat_data['timestamp'])
            print(f"💬 [{chat_data['username']}] {chat_data['message']} ({timestamp.strftime('%H:%M:%S')})")
            
        except Exception as e:
            print(f"❌ [{self.username}] メッセージ処理エラー: {e}")
    
    async def _handle_user_join(self, message: Dict):
        """
        ユーザー参加の処理
        """
        username = message.get('username')
        from_instance = message.get('from_instance')
        
        if username and from_instance:
            self.connected_users[username] = from_instance
            
            # セッションキーを確立
            try:
                session_id = await self.manager.generate_session_key([from_instance])
                session_key = await self.manager.get_session_key(session_id)
                self.session_keys[username] = session_key
                
                print(f"✅ [{self.username}] {username} がチャットに参加しました")
                
            except Exception as e:
                print(f"❌ [{self.username}] {username} とのキー確立に失敗: {e}")
    
    async def _handle_user_leave(self, message: Dict):
        """
        ユーザー退出の処理
        """
        username = message.get('username')
        if username in self.connected_users:
            print(f"👋 [{self.username}] {username} がチャットから退出しました")
            del self.connected_users[username]
            if username in self.session_keys:
                del self.session_keys[username]
    
    def _get_username_by_instance(self, instance_id: str) -> Optional[str]:
        """
        インスタンスIDからユーザー名を取得します。
        """
        for username, inst_id in self.connected_users.items():
            if inst_id == instance_id:
                return username
        return None
    
    def get_chat_status(self) -> Dict:
        """
        チャットの状態を取得します。
        """
        return {
            'username': self.username,
            'port': self.port,
            'connected_users': list(self.connected_users.keys()),
            'total_messages': len(self.message_history),
            'is_running': self.is_running
        }


async def interactive_chat_session(username: str, port: int):
    """
    インタラクティブなチャットセッション
    
    Args:
        username: ユーザー名
        port: ポート番号
    """
    chat_node = SecureChatNode(username, port)
    
    try:
        await chat_node.start()
        
        print(f"""
🔐 EntangleKey セキュアチャット
ユーザー: {username}
ポート: {port}

コマンド:
  /connect <host> <port>  - 他のユーザーに接続
  /status                 - チャット状態を表示
  /history               - メッセージ履歴を表示
  /quit                  - チャットを終了
  
メッセージを入力してEnterキーを押すと送信されます。
        """)
        
        # 非同期で入力を処理
        input_task = asyncio.create_task(handle_user_input(chat_node))
        
        # メインループ
        try:
            while chat_node.is_running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+Cが押されました")
        finally:
            input_task.cancel()
            await chat_node.stop()
    
    except Exception as e:
        print(f"❌ チャットエラー: {e}")
        await chat_node.stop()


async def handle_user_input(chat_node: SecureChatNode):
    """
    ユーザー入力を処理します（非同期）
    """
    loop = asyncio.get_event_loop()
    
    while chat_node.is_running:
        try:
            # 非同期で入力を取得
            user_input = await loop.run_in_executor(None, input, "💬 > ")
            
            if not user_input.strip():
                continue
            
            if user_input.startswith('/'):
                await process_command(chat_node, user_input)
            else:
                await chat_node.send_message(user_input)
                
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"❌ 入力処理エラー: {e}")


async def process_command(chat_node: SecureChatNode, command: str):
    """
    コマンドを処理します。
    """
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == '/connect' and len(parts) >= 3:
        host = parts[1]
        try:
            port = int(parts[2])
            await chat_node.connect_to_user(host, port)
        except ValueError:
            print("❌ 無効なポート番号")
    
    elif cmd == '/status':
        status = chat_node.get_chat_status()
        print(f"📊 チャット状態:")
        print(f"  ユーザー: {status['username']}")
        print(f"  接続ユーザー: {', '.join(status['connected_users']) or 'なし'}")
        print(f"  メッセージ数: {status['total_messages']}")
    
    elif cmd == '/history':
        print("📜 メッセージ履歴:")
        for msg in chat_node.message_history[-10:]:  # 最新10件
            direction = "→" if msg['direction'] == 'sent' else "←"
            timestamp = msg['timestamp'].strftime('%H:%M:%S') if isinstance(msg['timestamp'], datetime) else msg['timestamp']
            print(f"  {direction} [{msg['username']}] {msg['message']} ({timestamp})")
    
    elif cmd == '/quit':
        chat_node.is_running = False
        print("👋 チャットを終了します...")
    
    else:
        print("❌ 不明なコマンド。使用可能: /connect, /status, /history, /quit")


async def multi_user_demo():
    """
    複数ユーザーのデモンストレーション
    """
    print("=" * 60)
    print("EntangleKey マルチユーザー・セキュアチャット デモ")
    print("=" * 60)
    
    # 3人のユーザーを作成
    alice = SecureChatNode("Alice", 8881)
    bob = SecureChatNode("Bob", 8882)
    charlie = SecureChatNode("Charlie", 8883)
    
    try:
        # チャットノードを開始
        await alice.start()
        await bob.start()
        await charlie.start()
        
        print("\n🚀 すべてのチャットノードが開始されました")
        
        # 接続を確立
        await asyncio.sleep(1)
        await bob.connect_to_user("localhost", 8881)  # Bob -> Alice
        await asyncio.sleep(1)
        await charlie.connect_to_user("localhost", 8881)  # Charlie -> Alice
        await asyncio.sleep(1)
        await charlie.connect_to_user("localhost", 8882)  # Charlie -> Bob
        
        print("\n✅ ユーザー間の接続が確立されました")
        await asyncio.sleep(2)
        
        # メッセージ交換のデモ
        print("\n💬 メッセージ交換デモ:")
        
        await alice.send_message("こんにちは！Aliceです。")
        await asyncio.sleep(1)
        
        await bob.send_message("こんにちは、Alice！Bobです。")
        await asyncio.sleep(1)
        
        await charlie.send_message("皆さん、こんにちは！Charlieです。")
        await asyncio.sleep(1)
        
        await alice.send_message("量子もつれキーでセキュアに通信できますね！")
        await asyncio.sleep(1)
        
        await bob.send_message("EntangleKeyすごいですね！")
        await asyncio.sleep(1)
        
        await charlie.send_message("盗聴不可能な通信、素晴らしい！")
        await asyncio.sleep(2)
        
        # 状態表示
        print("\n📊 最終状態:")
        for user in [alice, bob, charlie]:
            status = user.get_chat_status()
            print(f"  {status['username']}: 接続ユーザー {len(status['connected_users'])}人, メッセージ {status['total_messages']}件")
        
        await asyncio.sleep(2)
        
    finally:
        # クリーンアップ
        await alice.stop()
        await bob.stop()
        await charlie.stop()
        
        print("\n✅ デモ完了")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 3:
        # インタラクティブモード
        username = sys.argv[1]
        port = int(sys.argv[2])
        asyncio.run(interactive_chat_session(username, port))
    else:
        # デモモード
        asyncio.run(multi_user_demo())
