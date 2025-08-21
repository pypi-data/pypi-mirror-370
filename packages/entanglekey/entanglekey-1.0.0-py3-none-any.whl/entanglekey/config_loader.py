"""
EntangleKey 設定ファイルローダー

YAML、JSON、TOML形式の設定ファイルを読み込み、EntangleKeyConfigオブジェクトを生成します。
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import os

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

from .config import EntangleKeyConfig, QuantumConfig, NetworkConfig, CryptoConfig, SecurityConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    設定ファイルローダー
    """
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> EntangleKeyConfig:
        """
        設定ファイルからEntangleKeyConfigを読み込みます。
        
        Args:
            file_path: 設定ファイルのパス
            
        Returns:
            EntangleKeyConfig インスタンス
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: 設定ファイルの形式が不正な場合
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        # ファイル拡張子から形式を判定
        suffix = file_path.suffix.lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if suffix == '.json':
                    config_dict = json.load(f)
                elif suffix in ['.yml', '.yaml']:
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAML is required for YAML config files. Install with: pip install PyYAML")
                    config_dict = yaml.safe_load(f)
                elif suffix == '.toml':
                    if not TOML_AVAILABLE:
                        raise ImportError("toml is required for TOML config files. Install with: pip install toml")
                    config_dict = toml.load(f)
                else:
                    # 形式を推測して読み込み
                    content = f.read()
                    config_dict = ConfigLoader._parse_content(content)
            
            logger.info(f"Loaded config from {file_path}")
            return ConfigLoader._dict_to_config(config_dict)
            
        except Exception as e:
            raise ValueError(f"Failed to parse config file {file_path}: {e}")
    
    @staticmethod
    def load_from_env() -> EntangleKeyConfig:
        """
        環境変数からEntangleKeyConfigを読み込みます。
        
        Returns:
            EntangleKeyConfig インスタンス
        """
        env_config = {}
        
        # Quantum設定
        quantum_config = {}
        if os.getenv('ENTANGLEKEY_QUBITS_PER_INSTANCE'):
            quantum_config['qubits_per_instance'] = int(os.getenv('ENTANGLEKEY_QUBITS_PER_INSTANCE'))
        if os.getenv('ENTANGLEKEY_CORRELATION_THRESHOLD'):
            quantum_config['correlation_threshold'] = float(os.getenv('ENTANGLEKEY_CORRELATION_THRESHOLD'))
        if os.getenv('ENTANGLEKEY_ENTROPY_POOL_SIZE'):
            quantum_config['entropy_pool_size'] = int(os.getenv('ENTANGLEKEY_ENTROPY_POOL_SIZE'))
        if quantum_config:
            env_config['quantum'] = quantum_config
        
        # Network設定
        network_config = {}
        if os.getenv('ENTANGLEKEY_DEFAULT_PORT'):
            network_config['default_port'] = int(os.getenv('ENTANGLEKEY_DEFAULT_PORT'))
            network_config['port'] = int(os.getenv('ENTANGLEKEY_DEFAULT_PORT'))  # 後方互換性
        if os.getenv('ENTANGLEKEY_PING_INTERVAL'):
            network_config['ping_interval'] = int(os.getenv('ENTANGLEKEY_PING_INTERVAL'))
        if os.getenv('ENTANGLEKEY_CONNECTION_TIMEOUT'):
            network_config['connection_timeout'] = float(os.getenv('ENTANGLEKEY_CONNECTION_TIMEOUT'))
        if network_config:
            env_config['network'] = network_config
        
        # Crypto設定
        crypto_config = {}
        if os.getenv('ENTANGLEKEY_KEY_LENGTH'):
            crypto_config['key_length'] = int(os.getenv('ENTANGLEKEY_KEY_LENGTH'))
            crypto_config['default_key_length'] = int(os.getenv('ENTANGLEKEY_KEY_LENGTH'))
        if os.getenv('ENTANGLEKEY_RSA_KEY_SIZE'):
            crypto_config['rsa_key_size'] = int(os.getenv('ENTANGLEKEY_RSA_KEY_SIZE'))
        if os.getenv('ENTANGLEKEY_ENCRYPTION_ALGORITHM'):
            crypto_config['encryption_algorithm'] = os.getenv('ENTANGLEKEY_ENCRYPTION_ALGORITHM')
        if crypto_config:
            env_config['crypto'] = crypto_config
        
        # Security設定
        security_config = {}
        if os.getenv('ENTANGLEKEY_ATTACK_DETECTION_ENABLED'):
            security_config['attack_detection_enabled'] = os.getenv('ENTANGLEKEY_ATTACK_DETECTION_ENABLED').lower() == 'true'
        if os.getenv('ENTANGLEKEY_LOG_SECURITY_EVENTS'):
            security_config['log_security_events'] = os.getenv('ENTANGLEKEY_LOG_SECURITY_EVENTS').lower() == 'true'
        if os.getenv('ENTANGLEKEY_KEY_FRESHNESS_TIMEOUT'):
            security_config['key_freshness_timeout'] = float(os.getenv('ENTANGLEKEY_KEY_FRESHNESS_TIMEOUT'))
        if security_config:
            env_config['security'] = security_config
        
        logger.info("Loaded config from environment variables")
        return ConfigLoader._dict_to_config(env_config)
    
    @staticmethod
    def load_default_config() -> EntangleKeyConfig:
        """
        デフォルト設定を読み込みます。
        
        Returns:
            EntangleKeyConfig インスタンス
        """
        # 標準的な設定ファイルの場所を検索
        config_paths = [
            Path("entanglekey.yml"),
            Path("entanglekey.yaml"),
            Path("entanglekey.json"),
            Path("entanglekey.toml"),
            Path("config/entanglekey.yml"),
            Path("config/entanglekey.yaml"),
            Path("config/entanglekey.json"),
            Path("~/.entanglekey/config.yml").expanduser(),
            Path("~/.entanglekey/config.yaml").expanduser(),
            Path("~/.entanglekey/config.json").expanduser(),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                logger.info(f"Found config file: {config_path}")
                return ConfigLoader.load_from_file(config_path)
        
        # 環境変数からの読み込みを試行
        env_config = ConfigLoader.load_from_env()
        if env_config.quantum.qubits_per_instance != 8:  # デフォルト値から変更されている
            return env_config
        
        # デフォルト設定を返す
        logger.info("Using default configuration")
        return EntangleKeyConfig()
    
    @staticmethod
    def save_to_file(config: EntangleKeyConfig, file_path: Union[str, Path], format: str = 'yaml'):
        """
        設定をファイルに保存します。
        
        Args:
            config: 保存するEntangleKeyConfig
            file_path: 保存先ファイルパス
            format: 保存形式 ('yaml', 'json', 'toml')
        """
        file_path = Path(file_path)
        config_dict = config.to_dict()
        
        # ディレクトリを作成
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format.lower() == 'json':
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                elif format.lower() in ['yaml', 'yml']:
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAML is required for YAML format. Install with: pip install PyYAML")
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif format.lower() == 'toml':
                    if not TOML_AVAILABLE:
                        raise ImportError("toml is required for TOML format. Install with: pip install toml")
                    toml.dump(config_dict, f)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Saved config to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config to {file_path}: {e}")
            raise
    
    @staticmethod
    def _parse_content(content: str) -> Dict[str, Any]:
        """
        コンテンツを解析して設定辞書を取得します。
        
        Args:
            content: ファイルコンテンツ
            
        Returns:
            設定辞書
        """
        # JSON形式を試行
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # YAML形式を試行
        if YAML_AVAILABLE:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                pass
        
        # TOML形式を試行
        if TOML_AVAILABLE:
            try:
                return toml.loads(content)
            except toml.TomlDecodeError:
                pass
        
        raise ValueError("Unable to parse config file content")
    
    @staticmethod
    def _dict_to_config(config_dict: Dict[str, Any]) -> EntangleKeyConfig:
        """
        設定辞書からEntangleKeyConfigを作成します。
        
        Args:
            config_dict: 設定辞書
            
        Returns:
            EntangleKeyConfig インスタンス
        """
        # 空の設定の場合はデフォルトを返す
        if not config_dict:
            return EntangleKeyConfig()
        
        # 各セクションの設定を作成
        quantum_config = QuantumConfig(**config_dict.get('quantum', {}))
        network_config = NetworkConfig(**config_dict.get('network', {}))
        crypto_config = CryptoConfig(**config_dict.get('crypto', {}))
        security_config = SecurityConfig(**config_dict.get('security', {}))
        
        return EntangleKeyConfig(
            quantum=quantum_config,
            network=network_config,
            crypto=crypto_config,
            security=security_config
        )


def generate_sample_config() -> str:
    """
    サンプル設定ファイル（YAML形式）を生成します。
    
    Returns:
        サンプル設定ファイルの内容
    """
    sample_config = """# EntangleKey 設定ファイル
# 量子もつれベースの分散セッションキー生成ライブラリ

# 量子シミュレーション設定
quantum:
  qubits_per_instance: 8          # インスタンスあたりの量子ビット数
  random_seed: null               # 乱数シード (null = ランダム)
  correlation_threshold: 0.8      # 相関閾値
  entropy_pool_size: 1024         # エントロピープールサイズ
  max_measurement_cache: 1000     # 測定結果キャッシュ最大数

# ネットワーク通信設定
network:
  port: 8888                      # 待受ポート番号
  default_port: 8888              # デフォルトポート
  ping_interval: 20               # Pingインターバル (秒)
  ping_timeout: 10                # Pingタイムアウト (秒)
  connection_timeout: 30.0        # 接続タイムアウト (秒)
  max_connections: 100            # 最大接続数
  buffer_size: 8192               # バッファサイズ

# 暗号化設定
crypto:
  key_length: 256                 # キー長 (ビット)
  default_key_length: 256         # デフォルトキー長
  rsa_key_size: 2048             # RSA鍵サイズ
  hkdf_salt_size: 32             # HKDF塩サイズ
  nonce_size: 24                 # ナンスサイズ
  signature_algorithm: "HMAC-SHA256"  # 署名アルゴリズム
  encryption_algorithm: "ChaCha20Poly1305"  # 暗号化アルゴリズム
  key_rotation_interval: 3600     # キーローテーション間隔 (秒)

# セキュリティ監視設定
security:
  correlation_threshold: 0.8      # 相関閾値
  entropy_quality_threshold: 0.9  # エントロピー品質閾値
  key_freshness_timeout: 30.0     # キー新鮮度タイムアウト (秒)
  attack_detection_enabled: true  # 攻撃検知の有効化
  log_security_events: true       # セキュリティイベントログの有効化
"""
    return sample_config


def create_sample_config_file(file_path: Union[str, Path] = "entanglekey.yml"):
    """
    サンプル設定ファイルを作成します。
    
    Args:
        file_path: 作成する設定ファイルのパス
    """
    file_path = Path(file_path)
    
    if file_path.exists():
        response = input(f"Config file {file_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generate_sample_config())
        
        print(f"✅ Sample config file created: {file_path}")
        print(f"You can now edit {file_path} to customize your EntangleKey configuration.")
        
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")


if __name__ == "__main__":
    # サンプル設定ファイルを作成
    create_sample_config_file()
