#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntangleKey セキュア通信例

複数のインスタンス間でセッションキーを生成し、
そのキーを使用してセキュアな通信を行う例
"""

import asyncio
import json
import logging
from datetime import datetime
from entanglekey import EntangleKeyManager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureCommunicator:
    """
    セキュアな通信を行うクラス
    """
    
    def __init__(self, instance_id: str, port: int):
        self.instance_id = instance_id
        self.port = port
        self.manager = EntangleKeyManager(
            instance_id=instance_id,
            network_port=port,
            key_length=256
        )
        self.session_keys = {}
        self.message_counter = 0
        
        # イベントハンドラーを設定
        self.manager.add_key_generated_callback(self._on_key_generated)
        self.manager.add_instance_connected_callback(self._on_instance_connected)
        self.manager.network_manager.add_message_handler('secure_message', self._handle_secure_message)
    
    async def start(self):
        """
        通信システムを開始
        """
        await self.manager.start()
        print(f"🚀 [{self.instance_id}] Secure communicator started on port {self.port}")
    
    async def stop(self):
        """
        通信システムを停止
        """
        await self.manager.stop()
        print(f"🛑 [{self.instance_id}] Secure communicator stopped")
    
    async def connect_to_instance(self, host: str, port: int) -> str:
        """
        他のインスタンスに接続し、セッションキーを確立
        """
        remote_instance_id = await self.manager.connect_instance(host, port)
        print(f"🔗 [{self.instance_id}] Connected to {remote_instance_id}")
        
        # セッションキーを生成
        session_id = await self.manager.generate_session_key([remote_instance_id])
        session_key = await self.manager.get_session_key(session_id)
        
        self.session_keys[remote_instance_id] = {
            'session_id': session_id,
            'key': session_key
        }
        
        print(f"🔑 [{self.instance_id}] Session key established with {remote_instance_id}")
        return remote_instance_id
    
    async def send_secure_message(self, target_instance: str, message: str):
        """
        セキュアなメッセージを送信
        """
        if target_instance not in self.session_keys:
            raise ValueError(f"No session key for instance {target_instance}")
        
        session_info = self.session_keys[target_instance]
        session_key = session_info['key']
        
        # メッセージを暗号化
        message_data = {
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'counter': self.message_counter,
            'from': self.instance_id
        }
        
        message_json = json.dumps(message_data).encode()
        encrypted_data, nonce = self.manager.key_generator.encrypt_data(message_json, session_key)
        
        # 署名を作成
        signature = self.manager.key_generator.create_message_signature(message_json, session_key)
        
        # セキュアメッセージとして送信
        secure_msg = {
            'type': 'secure_message',
            'session_id': session_info['session_id'],
            'encrypted_data': encrypted_data.hex(),
            'nonce': nonce.hex(),
            'signature': signature.hex(),
            'message_id': f"{self.instance_id}_{self.message_counter}"
        }
        
        await self.manager.network_manager.send_to_instance(target_instance, secure_msg)
        
        self.message_counter += 1
        print(f"📤 [{self.instance_id}] Sent secure message to {target_instance}: '{message}'")
    
    async def _on_key_generated(self, session_id: str, key: bytes):
        """
        キー生成時のコールバック
        """
        print(f"✅ [{self.instance_id}] Session key generated: {session_id}")
        print(f"   Key hash: {self.manager.key_generator.hash_key(key)[:16]}...")
    
    async def _on_instance_connected(self, instance_id: str):
        """
        インスタンス接続時のコールバック
        """
        print(f"🔗 [{self.instance_id}] Instance connected: {instance_id}")
    
    async def _handle_secure_message(self, message):
        """
        セキュアメッセージの受信処理
        """
        try:
            session_id = message['session_id']
            encrypted_data = bytes.fromhex(message['encrypted_data'])
            nonce = bytes.fromhex(message['nonce'])
            signature = bytes.fromhex(message['signature'])
            message_id = message['message_id']
            
            # 対応するセッションキーを探す
            session_key = None
            for instance_id, session_info in self.session_keys.items():
                if session_info['session_id'] == session_id:
                    session_key = session_info['key']
                    break
            
            if not session_key:
                # まだキーを持っていない場合は、マネージャーから取得を試行
                session_key = await self.manager.get_session_key(session_id)
                if session_key:
                    # 送信者を特定し、キー情報を保存
                    from_instance = message.get('from_instance')
                    if from_instance and from_instance not in self.session_keys:
                        self.session_keys[from_instance] = {
                            'session_id': session_id,
                            'key': session_key
                        }
            
            if not session_key:
                print(f"❌ [{self.instance_id}] No session key for message {message_id}")
                return
            
            # メッセージを復号化
            decrypted_data = self.manager.key_generator.decrypt_data(
                encrypted_data, nonce, session_key
            )
            
            # 署名を検証
            if not self.manager.key_generator.verify_message_signature(
                decrypted_data, signature, session_key
            ):
                print(f"❌ [{self.instance_id}] Invalid signature for message {message_id}")
                return
            
            # メッセージデータを解析
            message_data = json.loads(decrypted_data.decode())
            
            print(f"📥 [{self.instance_id}] Received secure message from {message_data['from']}: '{message_data['content']}'")
            print(f"   Message ID: {message_id}, Timestamp: {message_data['timestamp']}")
            
        except Exception as e:
            print(f"❌ [{self.instance_id}] Error handling secure message: {e}")


async def alice_communicator():
    """
    Alice（送信者）のコミュニケーター
    """
    alice = SecureCommunicator("alice", 8888)
    
    try:
        await alice.start()
        
        # Bobの接続を待つ
        print("⏳ [Alice] Waiting for Bob to connect...")
        while len(alice.manager.get_connected_instances()) == 0:
            await asyncio.sleep(0.5)
        
        # 少し待ってからメッセージを送信
        await asyncio.sleep(2)
        
        bob_id = alice.manager.get_connected_instances()[0]
        
        # 複数のメッセージを送信
        messages = [
            "Hello Bob! This is a secure message from Alice.",
            "The quantum-entangled session key is working perfectly!",
            "This communication is protected against eavesdropping.",
            "EntangleKey ensures our messages are secure."
        ]
        
        for i, msg in enumerate(messages):
            await alice.send_secure_message(bob_id, msg)
            await asyncio.sleep(1)  # メッセージ間の間隔
        
        # 少し待機してから終了
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"❌ [Alice] Error: {e}")
    finally:
        await alice.stop()


async def bob_communicator():
    """
    Bob（受信者）のコミュニケーター
    """
    bob = SecureCommunicator("bob", 8889)
    
    try:
        await bob.start()
        
        # 少し待ってからAliceに接続
        await asyncio.sleep(1)
        
        alice_id = await bob.connect_to_instance("localhost", 8888)
        
        # Aliceからのメッセージを受信するために待機
        await asyncio.sleep(1)
        
        # 返信メッセージを送信
        reply_messages = [
            "Hi Alice! I received your secure message.",
            "The encryption is working great!",
            "Thanks for the secure communication demo."
        ]
        
        await asyncio.sleep(3)  # Aliceのメッセージを受信するまで待つ
        
        for msg in reply_messages:
            await bob.send_secure_message(alice_id, msg)
            await asyncio.sleep(1)
        
        # 少し待機
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ [Bob] Error: {e}")
    finally:
        await bob.stop()


async def main():
    """
    メイン関数 - セキュア通信のデモ
    """
    print("=" * 70)
    print("EntangleKey セキュア通信デモ")
    print("量子もつれキーを使用した暗号化通信")
    print("=" * 70)
    
    # AliceとBobを並行して起動
    await asyncio.gather(
        alice_communicator(),
        bob_communicator()
    )
    
    print("✅ セキュア通信デモ完了")


if __name__ == "__main__":
    asyncio.run(main())
