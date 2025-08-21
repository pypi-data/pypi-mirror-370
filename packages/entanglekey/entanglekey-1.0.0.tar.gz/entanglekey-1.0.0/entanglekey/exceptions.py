"""
EntangleKey カスタム例外クラス

ライブラリ固有のエラーハンドリングのための例外クラスを定義します。
"""


class EntangleKeyError(Exception):
    """
    EntangleKey ライブラリの基本例外クラス
    """
    pass


class QuantumError(EntangleKeyError):
    """
    量子もつれシミュレーション関連のエラー
    """
    pass


class NetworkError(EntangleKeyError):
    """
    ネットワーク通信関連のエラー
    """
    pass


class ConnectionError(NetworkError):
    """
    接続関連のエラー
    """
    pass


class CryptoError(EntangleKeyError):
    """
    暗号化・復号化関連のエラー
    """
    pass


class SynchronizationError(EntangleKeyError):
    """
    インスタンス間同期関連のエラー
    """
    pass


class ValidationError(EntangleKeyError):
    """
    データ検証関連のエラー
    """
    pass


class KeyGenerationError(CryptoError):
    """
    キー生成関連のエラー
    """
    pass


class EntanglementError(QuantumError):
    """
    量子もつれ状態関連のエラー
    """
    pass
