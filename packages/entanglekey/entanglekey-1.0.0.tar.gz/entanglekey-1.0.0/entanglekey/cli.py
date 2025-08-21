"""
EntangleKey コマンドラインインターフェース

EntangleKeyライブラリの機能をコマンドラインから利用するためのCLIツール
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Optional

from .core import EntangleKeyManager
from .exceptions import EntangleKeyError
from .config_loader import ConfigLoader, create_sample_config_file


def setup_logging(verbose: bool = False):
    """
    ログ設定を初期化します。
    
    Args:
        verbose: 詳細ログを有効にする場合True
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def start_server_command(args):
    """
    サーバーモードでEntangleKeyを開始します。
    """
    print(f"Starting EntangleKey server on port {args.port}")
    
    manager = EntangleKeyManager(
        instance_id=args.instance_id,
        network_port=args.port,
        key_length=args.key_length,
        sync_timeout=args.timeout,
        config_file=getattr(args, 'config', None)
    )
    
    # イベントハンドラーを設定
    async def on_key_generated(session_id: str, key: bytes):
        print(f"✅ Session key generated: {session_id}")
        print(f"   Key hash: {manager.key_generator.hash_key(key)[:16]}...")
    
    async def on_instance_connected(instance_id: str):
        print(f"🔗 Instance connected: {instance_id}")
    
    async def on_instance_disconnected(instance_id: str):
        print(f"❌ Instance disconnected: {instance_id}")
    
    manager.add_key_generated_callback(on_key_generated)
    manager.add_instance_connected_callback(on_instance_connected)
    manager.add_instance_disconnected_callback(on_instance_disconnected)
    
    try:
        await manager.start()
        print(f"🚀 EntangleKey server started (ID: {manager.instance_id})")
        print("Press Ctrl+C to stop...")
        
        # サーバーを実行し続ける
        try:
            while True:
                await asyncio.sleep(1)
                
                # 定期的にステータスを表示
                if hasattr(args, 'show_status') and args.show_status:
                    status = manager.get_status()
                    print(f"Status: {status['connected_instances']} connections, "
                          f"{status['active_sessions']} active sessions")
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
    
    except EntangleKeyError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        await manager.stop()
        print("✅ Server stopped")
    
    return 0


async def connect_command(args):
    """
    他のインスタンスに接続します。
    """
    print(f"Connecting to {args.host}:{args.target_port}...")
    
    manager = EntangleKeyManager(
        instance_id=args.instance_id,
        network_port=args.port,
        key_length=args.key_length,
        config_file=getattr(args, 'config', None)
    )
    
    try:
        await manager.start()
        print(f"🚀 Local instance started (ID: {manager.instance_id})")
        
        # 対象インスタンスに接続
        remote_instance_id = await manager.connect_instance(args.host, args.target_port)
        print(f"🔗 Connected to instance: {remote_instance_id}")
        
        # セッションキーを生成
        session_id = await manager.generate_session_key([remote_instance_id])
        session_key = await manager.get_session_key(session_id)
        
        print(f"✅ Session key generated: {session_id}")
        print(f"   Key hash: {manager.key_generator.hash_key(session_key)}")
        
        if args.save_key:
            with open(args.save_key, 'wb') as f:
                f.write(session_key)
            print(f"💾 Key saved to: {args.save_key}")
        
        # 接続を維持
        if args.keep_alive:
            print("🔄 Keeping connection alive... Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Disconnecting...")
    
    except EntangleKeyError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        await manager.stop()
        print("✅ Disconnected")
    
    return 0


async def generate_key_command(args):
    """
    セッションキーを生成します（スタンドアロンモード）。
    """
    print("Generating quantum-entangled session key...")
    
    manager = EntangleKeyManager(
        instance_id=args.instance_id,
        key_length=args.key_length,
        config_file=getattr(args, 'config', None)
    )
    
    # 模擬的なパートナーインスタンス
    partner_instances = args.partners.split(',') if args.partners else ['partner_1']
    
    try:
        await manager.start()
        
        # 量子もつれ状態を作成
        entanglement_state = await manager.quantum_sim.create_entanglement(
            [manager.instance_id] + partner_instances
        )
        
        # セッションキーを生成
        session_key = await manager.key_generator.generate_key(
            entanglement_state, partner_instances
        )
        
        print(f"✅ Session key generated successfully")
        print(f"   Length: {len(session_key)} bytes ({len(session_key) * 8} bits)")
        print(f"   Hash: {manager.key_generator.hash_key(session_key)}")
        
        if args.verbose:
            key_info = manager.key_generator.get_key_info(session_key)
            print(f"   Key info: {json.dumps(key_info, indent=2)}")
        
        if args.output:
            with open(args.output, 'wb') as f:
                f.write(session_key)
            print(f"💾 Key saved to: {args.output}")
        
        if args.hex_output:
            print(f"   Hex: {session_key.hex()}")
    
    except EntangleKeyError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        await manager.stop()
    
    return 0


async def status_command(args):
    """
    実行中のインスタンスのステータスを表示します。
    """
    manager = EntangleKeyManager(
        instance_id=args.instance_id,
        network_port=args.port,
        config_file=getattr(args, 'config', None)
    )
    
    try:
        await manager.start()
        status = manager.get_status()
        network_status = manager.network_manager.get_network_status()
        
        print("📊 EntangleKey Status")
        print("=" * 50)
        print(f"Instance ID: {status['instance_id']}")
        print(f"Running: {status['is_running']}")
        print(f"Network Port: {status['network_port']}")
        print(f"Connected Instances: {status['connected_instances']}")
        print(f"Active Sessions: {status['active_sessions']}")
        print(f"Total Connections: {network_status['total_connections']}")
        
        if network_status['connected_instances']:
            print("\n🔗 Connected Instances:")
            for instance_id in network_status['connected_instances']:
                print(f"  • {instance_id}")
    
    except EntangleKeyError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        await manager.stop()
    
    return 0


def create_config_command(args):
    """
    サンプル設定ファイルを作成します。
    """
    from .config import EntangleKeyConfig
    from pathlib import Path
    
    output_path = Path(args.output)
    
    if output_path.exists():
        response = input(f"設定ファイル {output_path} は既に存在します。上書きしますか？ (y/N): ")
        if response.lower() != 'y':
            print("❌ キャンセルされました。")
            return 1
    
    try:
        # デフォルト設定を作成
        default_config = EntangleKeyConfig()
        
        # 設定ファイルを保存
        ConfigLoader.save_to_file(default_config, output_path, args.format)
        
        print(f"✅ サンプル設定ファイルを作成しました: {output_path}")
        print(f"設定を編集してEntangleKeyをカスタマイズできます。")
        print(f"")
        print(f"使用方法:")
        print(f"  entanglekey --config {output_path} server")
        
        return 0
        
    except Exception as e:
        print(f"❌ 設定ファイルの作成に失敗しました: {e}")
        return 1


def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(
        description="EntangleKey - 量子もつれベースの分散セッションキー生成ライブラリ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # サーバーモードで起動
  entanglekey server --port 8888
  
  # 他のインスタンスに接続してキーを生成
  entanglekey connect localhost 8888 --save-key session.key
  
  # スタンドアロンでキーを生成
  entanglekey generate --output session.key --hex-output
  
  # ステータスを確認
  entanglekey status --port 8888
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを有効にする'
    )
    
    parser.add_argument(
        '--instance-id',
        help='インスタンスID（自動生成される場合は省略可能）'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='設定ファイルのパス'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='使用可能なコマンド')
    
    # サーバーコマンド
    server_parser = subparsers.add_parser('server', help='サーバーモードで起動')
    server_parser.add_argument('--port', type=int, default=8888, help='待受ポート番号')
    server_parser.add_argument('--key-length', type=int, default=256, help='キー長（ビット）')
    server_parser.add_argument('--timeout', type=float, default=30.0, help='同期タイムアウト（秒）')
    server_parser.add_argument('--show-status', action='store_true', help='定期的にステータスを表示')
    
    # 接続コマンド
    connect_parser = subparsers.add_parser('connect', help='他のインスタンスに接続')
    connect_parser.add_argument('host', help='接続先ホスト')
    connect_parser.add_argument('target_port', type=int, help='接続先ポート')
    connect_parser.add_argument('--port', type=int, default=8889, help='ローカルポート番号')
    connect_parser.add_argument('--key-length', type=int, default=256, help='キー長（ビット）')
    connect_parser.add_argument('--save-key', help='キーを保存するファイル名')
    connect_parser.add_argument('--keep-alive', action='store_true', help='接続を維持する')
    
    # キー生成コマンド
    generate_parser = subparsers.add_parser('generate', help='セッションキーを生成')
    generate_parser.add_argument('--key-length', type=int, default=256, help='キー長（ビット）')
    generate_parser.add_argument('--partners', help='パートナーインスタンス（カンマ区切り）')
    generate_parser.add_argument('--output', '-o', help='キーを保存するファイル名')
    generate_parser.add_argument('--hex-output', action='store_true', help='16進数でキーを表示')
    
    # ステータスコマンド
    status_parser = subparsers.add_parser('status', help='ステータスを表示')
    status_parser.add_argument('--port', type=int, default=8888, help='ポート番号')
    
    # 設定作成コマンド
    config_parser = subparsers.add_parser('create-config', help='サンプル設定ファイルを作成')
    config_parser.add_argument('--output', '-o', default='entanglekey.yml', help='出力ファイル名')
    config_parser.add_argument('--format', choices=['yaml', 'json', 'toml'], default='yaml', help='設定ファイルの形式')
    
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(args.verbose)
    
    # コマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return 1
    
    # コマンドを実行
    try:
        if args.command == 'server':
            return asyncio.run(start_server_command(args))
        elif args.command == 'connect':
            return asyncio.run(connect_command(args))
        elif args.command == 'generate':
            return asyncio.run(generate_key_command(args))
        elif args.command == 'status':
            return asyncio.run(status_command(args))
        elif args.command == 'create-config':
            return create_config_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
