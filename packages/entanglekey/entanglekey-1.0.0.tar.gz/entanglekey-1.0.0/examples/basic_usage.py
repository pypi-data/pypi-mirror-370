#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntangleKey 基本使用例

2つのインスタンス間でセッションキーを生成・共有する基本的な例
"""

import asyncio
import logging
from entanglekey import EntangleKeyManager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def instance_a():
    """
    インスタンスA（サーバー役）
    """
    print("🚀 Starting Instance A (Server)")
    
    manager_a = EntangleKeyManager(
        instance_id="instance_a",
        network_port=8888,
        key_length=256
    )
    
    # イベントハンドラーを設定
    async def on_key_generated(session_id: str, key: bytes):
        print(f"✅ [A] Session key generated: {session_id}")
        print(f"   [A] Key hash: {manager_a.key_generator.hash_key(key)[:16]}...")
    
    async def on_instance_connected(instance_id: str):
        print(f"🔗 [A] Instance connected: {instance_id}")
    
    manager_a.add_key_generated_callback(on_key_generated)
    manager_a.add_instance_connected_callback(on_instance_connected)
    
    try:
        await manager_a.start()
        print(f"✅ [A] Instance A started on port 8888")
        
        # インスタンスBの接続を待つ
        print("⏳ [A] Waiting for Instance B to connect...")
        
        # 接続されるまで待機
        while len(manager_a.get_connected_instances()) == 0:
            await asyncio.sleep(0.5)
        
        connected_instances = manager_a.get_connected_instances()
        print(f"✅ [A] Connected to: {connected_instances}")
        
        # セッションキーを生成
        session_id = await manager_a.generate_session_key(connected_instances)
        session_key = await manager_a.get_session_key(session_id)
        
        print(f"🔑 [A] Generated session key: {session_key.hex()[:32]}...")
        
        # 少し待機してから終了
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ [A] Error: {e}")
    finally:
        await manager_a.stop()
        print("🛑 [A] Instance A stopped")


async def instance_b():
    """
    インスタンスB（クライアント役）
    """
    print("🚀 Starting Instance B (Client)")
    
    manager_b = EntangleKeyManager(
        instance_id="instance_b",
        network_port=8889,
        key_length=256
    )
    
    # イベントハンドラーを設定
    async def on_key_generated(session_id: str, key: bytes):
        print(f"✅ [B] Session key received: {session_id}")
        print(f"   [B] Key hash: {manager_b.key_generator.hash_key(key)[:16]}...")
    
    manager_b.add_key_generated_callback(on_key_generated)
    
    try:
        await manager_b.start()
        print(f"✅ [B] Instance B started on port 8889")
        
        # 少し待ってからインスタンスAに接続
        await asyncio.sleep(1)
        
        print("🔗 [B] Connecting to Instance A...")
        instance_a_id = await manager_b.connect_instance("localhost", 8888)
        print(f"✅ [B] Connected to Instance A: {instance_a_id}")
        
        # インスタンスAがキーを生成するまで待機
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ [B] Error: {e}")
    finally:
        await manager_b.stop()
        print("🛑 [B] Instance B stopped")


async def main():
    """
    メイン関数 - 2つのインスタンスを並行実行
    """
    print("=" * 60)
    print("EntangleKey 基本使用例")
    print("2つのインスタンス間でのセッションキー生成")
    print("=" * 60)
    
    # 2つのインスタンスを並行して起動
    await asyncio.gather(
        instance_a(),
        instance_b()
    )
    
    print("✅ デモ完了")


if __name__ == "__main__":
    asyncio.run(main())
