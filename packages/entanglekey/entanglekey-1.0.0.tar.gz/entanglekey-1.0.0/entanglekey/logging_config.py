"""
EntangleKey ログ設定モジュール

構造化ログとセキュリティイベントログを提供します。
"""

import logging
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path

from .config import SecurityConfig


class SecurityEventLogger:
    """
    セキュリティイベント専用ロガー
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        セキュリティロガーを初期化します。
        
        Args:
            config: セキュリティ設定
        """
        self.config = config or SecurityConfig()
        self.logger = logging.getLogger('entanglekey.security')
        self._setup_security_logger()
    
    def _setup_security_logger(self):
        """
        セキュリティロガーのセットアップ
        """
        if not self.config.log_security_events:
            return
        
        # ログディレクトリを作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # セキュリティログファイルハンドラー
        security_handler = logging.FileHandler(
            log_dir / "security_events.log",
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        
        # JSONフォーマッター
        formatter = SecurityEventFormatter()
        security_handler.setFormatter(formatter)
        
        self.logger.addHandler(security_handler)
        self.logger.setLevel(logging.WARNING)
    
    def log_key_generation(self, session_id: str, instance_id: str, key_quality: Dict[str, Any]):
        """
        キー生成イベントをログ
        """
        event = {
            'event_type': 'key_generation',
            'session_id': session_id,
            'instance_id': instance_id,
            'key_quality': key_quality,
            'severity': 'info'
        }
        self.logger.info(f"Key generated: {session_id}", extra={'security_event': event})
    
    def log_attack_detection(self, attack_type: str, details: Dict[str, Any], severity: str = 'warning'):
        """
        攻撃検知イベントをログ
        """
        event = {
            'event_type': 'attack_detection',
            'attack_type': attack_type,
            'details': details,
            'severity': severity
        }
        level = getattr(logging, severity.upper(), logging.WARNING)
        self.logger.log(level, f"Attack detected: {attack_type}", extra={'security_event': event})
    
    def log_correlation_failure(self, entanglement_id: str, similarity: float, instances: list):
        """
        量子相関失敗イベントをログ
        """
        event = {
            'event_type': 'correlation_failure',
            'entanglement_id': entanglement_id,
            'similarity': similarity,
            'instances': instances,
            'severity': 'error'
        }
        self.logger.error(f"Correlation failure: {entanglement_id}", extra={'security_event': event})
    
    def log_network_anomaly(self, anomaly_type: str, source: str, details: Dict[str, Any]):
        """
        ネットワーク異常イベントをログ
        """
        event = {
            'event_type': 'network_anomaly',
            'anomaly_type': anomaly_type,
            'source': source,
            'details': details,
            'severity': 'warning'
        }
        self.logger.warning(f"Network anomaly: {anomaly_type}", extra={'security_event': event})


class SecurityEventFormatter(logging.Formatter):
    """
    セキュリティイベント用のJSONフォーマッター
    """
    
    def format(self, record):
        """
        ログレコードをJSON形式でフォーマット
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # セキュリティイベント情報を追加
        if hasattr(record, 'security_event'):
            log_entry['security_event'] = record.security_event
        
        return json.dumps(log_entry, ensure_ascii=False, indent=None)


class StructuredLogger:
    """
    構造化ログを提供するクラス
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        """
        構造化ロガーを初期化します。
        
        Args:
            name: ロガー名
            level: ログレベル
        """
        self.logger = logging.getLogger(name)
        self._setup_logger(level)
    
    def _setup_logger(self, level: int):
        """
        ロガーのセットアップ
        """
        # 既にハンドラーが設定されている場合はスキップ
        if self.logger.handlers:
            return
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # ファイルハンドラー
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / "entanglekey.log",
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # フォーマッター
        formatter = StructuredFormatter()
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(level)
    
    def info(self, message: str, **kwargs):
        """構造化情報ログ"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """構造化警告ログ"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """構造化エラーログ"""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """構造化デバッグログ"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """
        構造化ログの出力
        """
        extra = {
            'structured_data': kwargs,
            'pid': os.getpid(),
            'thread_id': f"{threading.current_thread().ident}"
        }
        self.logger.log(level, message, extra=extra)


class StructuredFormatter(logging.Formatter):
    """
    構造化ログ用のフォーマッター
    """
    
    def format(self, record):
        """
        ログレコードを構造化形式でフォーマット
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 構造化データを追加
        if hasattr(record, 'structured_data'):
            log_entry.update(record.structured_data)
        
        if hasattr(record, 'pid'):
            log_entry['pid'] = record.pid
        
        if hasattr(record, 'thread_id'):
            log_entry['thread_id'] = record.thread_id
        
        return json.dumps(log_entry, ensure_ascii=False, indent=None)


def setup_logging(level: int = logging.INFO, security_config: Optional[SecurityConfig] = None):
    """
    EntangleKeyのログシステムを初期化します。
    
    Args:
        level: ログレベル
        security_config: セキュリティ設定
    """
    # ルートロガーの設定
    root_logger = logging.getLogger('entanglekey')
    
    if root_logger.handlers:
        return  # 既に設定されている
    
    # ログディレクトリを作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(
        log_dir / "entanglekey.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)
    
    # セキュリティロガーを初期化
    if security_config and security_config.log_security_events:
        security_logger = SecurityEventLogger(security_config)
    
    logging.info("EntangleKey logging system initialized")


# スレッドモジュールの遅延インポート
import threading
