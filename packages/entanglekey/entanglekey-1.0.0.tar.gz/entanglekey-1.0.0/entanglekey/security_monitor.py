"""
EntangleKey セキュリティ監視モジュール

リアルタイムセキュリティ監視とアノマリー検知を提供します。
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .config import SecurityConfig
from .logging_config import SecurityEventLogger


@dataclass
class SecurityMetrics:
    """
    セキュリティメトリクス
    """
    entanglement_correlation: float = 0.0
    entropy_quality: float = 0.0
    network_integrity: str = "OK"
    key_freshness: float = 0.0
    attack_attempts: int = 0
    failed_correlations: int = 0
    anomalous_connections: int = 0
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkAnomalyInfo:
    """
    ネットワーク異常情報
    """
    source_ip: str
    anomaly_type: str
    severity: str
    first_seen: datetime
    last_seen: datetime
    count: int = 1


class SecurityMonitor:
    """
    リアルタイムセキュリティ監視システム
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        セキュリティモニターを初期化します。
        
        Args:
            config: セキュリティ設定
        """
        self.config = config or SecurityConfig()
        self.security_logger = SecurityEventLogger(self.config)
        self.metrics = SecurityMetrics()
        
        # 監視データ
        self.correlation_history: deque = deque(maxlen=100)
        self.entropy_history: deque = deque(maxlen=100)
        self.key_generation_times: deque = deque(maxlen=50)
        self.connection_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.network_anomalies: Dict[str, NetworkAnomalyInfo] = {}
        
        # アラートコールバック
        self.alert_callbacks: List[Callable] = []
        
        # 監視タスク
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self):
        """
        セキュリティ監視を開始します。
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.security_logger.logger.info("Security monitoring started")
    
    async def stop(self):
        """
        セキュリティ監視を停止します。
        """
        if not self.is_running:
            return
        
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.security_logger.logger.info("Security monitoring stopped")
    
    def record_correlation_check(self, correlation_value: float, entanglement_id: str, success: bool):
        """
        相関チェック結果を記録します。
        
        Args:
            correlation_value: 相関値
            entanglement_id: もつれ状態ID
            success: 成功フラグ
        """
        self.correlation_history.append({
            'value': correlation_value,
            'entanglement_id': entanglement_id,
            'success': success,
            'timestamp': datetime.now()
        })
        
        if not success:
            self.metrics.failed_correlations += 1
            
            # 攻撃検知の可能性
            if correlation_value < 0.3:  # 極端に低い相関
                self.security_logger.log_attack_detection(
                    'potential_eavesdropping',
                    {
                        'correlation_value': correlation_value,
                        'entanglement_id': entanglement_id,
                        'threshold': self.config.correlation_threshold
                    },
                    'critical'
                )
                self._trigger_alert('potential_eavesdropping', {
                    'correlation_value': correlation_value,
                    'entanglement_id': entanglement_id
                })
        
        self._update_correlation_metrics()
    
    def record_entropy_quality(self, entropy_quality: float, source: str):
        """
        エントロピー品質を記録します。
        
        Args:
            entropy_quality: エントロピー品質（0.0-1.0）
            source: エントロピー源
        """
        self.entropy_history.append({
            'quality': entropy_quality,
            'source': source,
            'timestamp': datetime.now()
        })
        
        if entropy_quality < self.config.entropy_quality_threshold:
            self.security_logger.log_attack_detection(
                'low_entropy',
                {
                    'entropy_quality': entropy_quality,
                    'source': source,
                    'threshold': self.config.entropy_quality_threshold
                },
                'warning'
            )
        
        self._update_entropy_metrics()
    
    def record_key_generation(self, session_id: str, generation_time: float, key_quality: Dict[str, Any]):
        """
        キー生成を記録します。
        
        Args:
            session_id: セッションID
            generation_time: 生成時間（秒）
            key_quality: キー品質情報
        """
        self.key_generation_times.append({
            'session_id': session_id,
            'time': generation_time,
            'timestamp': datetime.now(),
            'quality': key_quality
        })
        
        self.security_logger.log_key_generation(session_id, "unknown", key_quality)
        self._update_key_freshness()
    
    def record_connection_attempt(self, source_ip: str, success: bool, instance_id: Optional[str] = None):
        """
        接続試行を記録します。
        
        Args:
            source_ip: 接続元IP
            success: 成功フラグ
            instance_id: インスタンスID
        """
        now = datetime.now()
        self.connection_attempts[source_ip].append(now)
        
        # 古い記録を削除（直近1時間のみ保持）
        cutoff = now - timedelta(hours=1)
        self.connection_attempts[source_ip] = [
            ts for ts in self.connection_attempts[source_ip] if ts > cutoff
        ]
        
        # 異常検知
        recent_attempts = len(self.connection_attempts[source_ip])
        if recent_attempts > 10:  # 1時間に10回以上
            self._detect_connection_anomaly(source_ip, recent_attempts)
        
        if not success:
            self.metrics.attack_attempts += 1
    
    def record_network_anomaly(self, source_ip: str, anomaly_type: str, details: Dict[str, Any]):
        """
        ネットワーク異常を記録します。
        
        Args:
            source_ip: 異常元IP
            anomaly_type: 異常タイプ
            details: 詳細情報
        """
        now = datetime.now()
        
        if source_ip in self.network_anomalies:
            anomaly = self.network_anomalies[source_ip]
            anomaly.last_seen = now
            anomaly.count += 1
        else:
            self.network_anomalies[source_ip] = NetworkAnomalyInfo(
                source_ip=source_ip,
                anomaly_type=anomaly_type,
                severity="warning",
                first_seen=now,
                last_seen=now
            )
        
        self.security_logger.log_network_anomaly(anomaly_type, source_ip, details)
        self.metrics.anomalous_connections += 1
    
    def add_alert_callback(self, callback: Callable):
        """
        アラートコールバックを追加します。
        
        Args:
            callback: コールバック関数
        """
        self.alert_callbacks.append(callback)
    
    def get_security_metrics(self) -> SecurityMetrics:
        """
        現在のセキュリティメトリクスを取得します。
        
        Returns:
            セキュリティメトリクス
        """
        self.metrics.last_update = datetime.now()
        return self.metrics
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        詳細なセキュリティレポートを生成します。
        
        Returns:
            セキュリティレポート
        """
        now = datetime.now()
        
        return {
            'timestamp': now.isoformat(),
            'metrics': {
                'entanglement_correlation': self.metrics.entanglement_correlation,
                'entropy_quality': self.metrics.entropy_quality,
                'network_integrity': self.metrics.network_integrity,
                'key_freshness': self.metrics.key_freshness,
                'attack_attempts': self.metrics.attack_attempts,
                'failed_correlations': self.metrics.failed_correlations,
                'anomalous_connections': self.metrics.anomalous_connections
            },
            'recent_activity': {
                'correlation_checks': len(self.correlation_history),
                'entropy_measurements': len(self.entropy_history),
                'key_generations': len(self.key_generation_times),
                'unique_connections': len(self.connection_attempts)
            },
            'anomalies': [
                {
                    'source_ip': anomaly.source_ip,
                    'type': anomaly.anomaly_type,
                    'severity': anomaly.severity,
                    'count': anomaly.count,
                    'first_seen': anomaly.first_seen.isoformat(),
                    'last_seen': anomaly.last_seen.isoformat()
                }
                for anomaly in self.network_anomalies.values()
            ]
        }
    
    async def _monitoring_loop(self):
        """
        メインの監視ループ
        """
        while self.is_running:
            try:
                await self._perform_security_checks()
                await asyncio.sleep(5.0)  # 5秒間隔で監視
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.security_logger.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _perform_security_checks(self):
        """
        定期的なセキュリティチェック
        """
        now = datetime.now()
        
        # 古いデータをクリーンアップ
        self._cleanup_old_data(now)
        
        # ネットワーク整合性チェック
        self._check_network_integrity()
        
        # 統計の更新
        self._update_statistics()
    
    def _cleanup_old_data(self, now: datetime):
        """
        古いデータをクリーンアップします。
        """
        cutoff = now - timedelta(hours=24)
        
        # 古い接続試行データを削除
        for source_ip in list(self.connection_attempts.keys()):
            self.connection_attempts[source_ip] = [
                ts for ts in self.connection_attempts[source_ip] if ts > cutoff
            ]
            if not self.connection_attempts[source_ip]:
                del self.connection_attempts[source_ip]
        
        # 古いネットワーク異常データを削除
        for source_ip in list(self.network_anomalies.keys()):
            if self.network_anomalies[source_ip].last_seen < cutoff:
                del self.network_anomalies[source_ip]
    
    def _check_network_integrity(self):
        """
        ネットワーク整合性をチェックします。
        """
        if self.metrics.anomalous_connections > 10:
            self.metrics.network_integrity = "COMPROMISED"
        elif self.metrics.anomalous_connections > 5:
            self.metrics.network_integrity = "SUSPICIOUS"
        else:
            self.metrics.network_integrity = "OK"
    
    def _update_correlation_metrics(self):
        """
        相関メトリクスを更新します。
        """
        if self.correlation_history:
            recent_correlations = [
                entry['value'] for entry in self.correlation_history
                if entry['success']
            ]
            if recent_correlations:
                self.metrics.entanglement_correlation = statistics.mean(recent_correlations)
    
    def _update_entropy_metrics(self):
        """
        エントロピーメトリクスを更新します。
        """
        if self.entropy_history:
            recent_entropy = [entry['quality'] for entry in self.entropy_history]
            self.metrics.entropy_quality = statistics.mean(recent_entropy)
    
    def _update_key_freshness(self):
        """
        キーの新鮮度を更新します。
        """
        if self.key_generation_times:
            latest_generation = max(
                entry['timestamp'] for entry in self.key_generation_times
            )
            time_since = (datetime.now() - latest_generation).total_seconds()
            self.metrics.key_freshness = time_since
    
    def _update_statistics(self):
        """
        統計情報を更新します。
        """
        self._update_correlation_metrics()
        self._update_entropy_metrics()
        self._update_key_freshness()
    
    def _detect_connection_anomaly(self, source_ip: str, attempt_count: int):
        """
        接続異常を検知します。
        """
        self.record_network_anomaly(
            source_ip,
            'excessive_connections',
            {
                'attempt_count': attempt_count,
                'timeframe': '1 hour'
            }
        )
        
        self._trigger_alert('excessive_connections', {
            'source_ip': source_ip,
            'attempt_count': attempt_count
        })
    
    def _trigger_alert(self, alert_type: str, details: Dict[str, Any]):
        """
        アラートをトリガーします。
        """
        alert_data = {
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(alert_data))
                else:
                    callback(alert_data)
            except Exception as e:
                self.security_logger.logger.error(f"Error in alert callback: {e}")


class QuantumSecurityValidator:
    """
    量子セキュリティ検証器
    """
    
    def __init__(self, security_monitor: SecurityMonitor):
        """
        量子セキュリティ検証器を初期化します。
        
        Args:
            security_monitor: セキュリティモニター
        """
        self.security_monitor = security_monitor
    
    def validate_entanglement_security(self, entanglement_id: str, measurements: Dict[str, bytes]) -> bool:
        """
        もつれ状態のセキュリティを検証します。
        
        Args:
            entanglement_id: もつれ状態ID
            measurements: 測定結果
            
        Returns:
            セキュリティが確保されている場合True
        """
        # 測定結果の一致度を計算
        correlation = self._calculate_correlation(measurements)
        
        # エントロピー品質を評価
        entropy_quality = self._evaluate_entropy_quality(measurements)
        
        # セキュリティモニターに記録
        self.security_monitor.record_correlation_check(
            correlation, entanglement_id, correlation >= 0.8
        )
        self.security_monitor.record_entropy_quality(entropy_quality, 'quantum_measurements')
        
        return correlation >= 0.8 and entropy_quality >= 0.9
    
    def _calculate_correlation(self, measurements: Dict[str, bytes]) -> float:
        """
        測定結果の相関を計算します。
        """
        if len(measurements) < 2:
            return 1.0
        
        measurement_values = list(measurements.values())
        first_measurement = measurement_values[0]
        
        total_bits = len(first_measurement) * 8
        matching_bits = 0
        
        for measurement in measurement_values[1:]:
            for i, (byte1, byte2) in enumerate(zip(first_measurement, measurement)):
                for bit_pos in range(8):
                    bit1 = (byte1 >> bit_pos) & 1
                    bit2 = (byte2 >> bit_pos) & 1
                    if bit1 == bit2:
                        matching_bits += 1
        
        total_comparisons = total_bits * (len(measurement_values) - 1)
        return matching_bits / total_comparisons if total_comparisons > 0 else 1.0
    
    def _evaluate_entropy_quality(self, measurements: Dict[str, bytes]) -> float:
        """
        エントロピー品質を評価します。
        """
        if not measurements:
            return 0.0
        
        # すべての測定結果を結合
        combined_data = b''.join(measurements.values())
        
        # ビット頻度を分析
        bit_counts = [0, 0]
        for byte in combined_data:
            for bit_pos in range(8):
                bit = (byte >> bit_pos) & 1
                bit_counts[bit] += 1
        
        total_bits = sum(bit_counts)
        if total_bits == 0:
            return 0.0
        
        # シャノンエントロピーを計算
        entropy = 0.0
        for count in bit_counts:
            if count > 0:
                p = count / total_bits
                entropy -= p * (p.bit_length() - 1)  # 簡略化されたエントロピー計算
        
        # 最大エントロピー（1.0）に正規化
        max_entropy = 1.0
        return min(entropy / max_entropy, 1.0)
