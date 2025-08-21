"""
EntangleKey 設定モジュール

ライブラリの各種設定クラスを提供します。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QuantumConfig:
    """
    量子シミュレーション設定
    """
    qubits_per_instance: int = 8
    random_seed: Optional[int] = None
    correlation_threshold: float = 0.8
    entropy_pool_size: int = 1024
    max_measurement_cache: int = 1000


@dataclass
class NetworkConfig:
    """
    ネットワーク通信設定
    """
    port: int = 8888  # 後方互換性のため
    default_port: int = 8888
    ping_interval: int = 20
    ping_timeout: int = 10
    connection_timeout: float = 30.0
    max_connections: int = 100
    buffer_size: int = 8192


@dataclass
class CryptoConfig:
    """
    暗号化設定
    """
    key_length: int = 256  # 後方互換性のため
    default_key_length: int = 256
    rsa_key_size: int = 2048  # RSA鍵のサイズ
    hkdf_salt_size: int = 32
    nonce_size: int = 24
    signature_algorithm: str = "HMAC-SHA256"
    encryption_algorithm: str = "ChaCha20Poly1305"
    key_rotation_interval: int = 3600  # 秒


@dataclass
class SecurityConfig:
    """
    セキュリティ監視設定
    """
    correlation_threshold: float = 0.8
    entropy_quality_threshold: float = 0.9
    key_freshness_timeout: float = 30.0
    attack_detection_enabled: bool = True
    log_security_events: bool = True


@dataclass
class EntangleKeyConfig:
    """
    EntangleKey 総合設定
    """
    quantum: QuantumConfig
    network: NetworkConfig
    crypto: CryptoConfig
    security: SecurityConfig
    
    def __init__(
        self,
        quantum: Optional[QuantumConfig] = None,
        network: Optional[NetworkConfig] = None,
        crypto: Optional[CryptoConfig] = None,
        security: Optional[SecurityConfig] = None
    ):
        self.quantum = quantum or QuantumConfig()
        self.network = network or NetworkConfig()
        self.crypto = crypto or CryptoConfig()
        self.security = security or SecurityConfig()

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'EntangleKeyConfig':
        """
        辞書から設定を作成します。
        
        Args:
            config_dict: 設定辞書
            
        Returns:
            EntangleKeyConfig インスタンス
        """
        quantum_config = QuantumConfig(**config_dict.get('quantum', {}))
        network_config = NetworkConfig(**config_dict.get('network', {}))
        crypto_config = CryptoConfig(**config_dict.get('crypto', {}))
        security_config = SecurityConfig(**config_dict.get('security', {}))
        
        return cls(
            quantum=quantum_config,
            network=network_config,
            crypto=crypto_config,
            security=security_config
        )

    def to_dict(self) -> dict:
        """
        設定を辞書形式で返します。
        
        Returns:
            設定辞書
        """
        return {
            'quantum': self.quantum.__dict__,
            'network': self.network.__dict__,
            'crypto': self.crypto.__dict__,
            'security': self.security.__dict__
        }