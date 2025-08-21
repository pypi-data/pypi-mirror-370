"""
EntangleKey - 量子もつれベースの分散セッションキー生成ライブラリ

このライブラリは、量子もつれの理論を基盤とした分散セッションキー生成システムを提供します。
複数のプログラムインスタンス間で安全で盗聴不可能なセッションキーの生成と同期を行います。
"""

__version__ = "1.0.0"
__author__ = "tikisan"
__email__ = ""

import logging

from .core import EntangleKeyManager
from .quantum import QuantumEntanglementSimulator
from .network import NetworkManager
from .crypto import SessionKeyGenerator

__all__ = [
    "EntangleKeyManager",
    "QuantumEntanglementSimulator", 
    "NetworkManager",
    "SessionKeyGenerator",
]

# ライブラリ使用者がロギング設定を行わない場合の警告を抑制
logging.getLogger(__name__).addHandler(logging.NullHandler())
