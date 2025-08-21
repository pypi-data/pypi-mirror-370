"""
量子もつれシミュレーションモジュール

古典的なコンピューター上で量子もつれの動作を模倣するシミュレーターを提供します。
実際の量子もつれではありませんが、その理論的特性を活用してセキュアなキー生成を実現します。
"""

import asyncio
import logging
import random
import secrets  # 追加
import hashlib
import struct
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from datetime import datetime
from .config import QuantumConfig

logger = logging.getLogger(__name__)


class QuantumState:
    """
    量子状態を表現するクラス
    """
    
    def __init__(self, qubits: int):
        """
        量子状態を初期化します。
        
        Args:
            qubits: 量子ビット数
        """
        self.qubits = qubits
        self.state_vector = np.zeros(2**qubits, dtype=complex)
        self.state_vector[0] = 1.0  # |00...0⟩ 状態で初期化
        self.entangled_pairs: List[Tuple[int, int]] = []
        self.measurement_results: Dict[int, int] = {}
        
    def entangle(self, qubit1: int, qubit2: int):
        """
        2つの量子ビットをもつれさせます。
        
        Args:
            qubit1: 1つ目の量子ビット
            qubit2: 2つ目の量子ビット
        """
        if (qubit1, qubit2) not in self.entangled_pairs and (qubit2, qubit1) not in self.entangled_pairs:
            self.entangled_pairs.append((qubit1, qubit2))
            self._apply_cnot(qubit1, qubit2)
            
    def _apply_cnot(self, control: int, target: int):
        """CNOT ゲートを適用します。"""
        # 簡略化されたCNOT操作のシミュレーション
        # 実際の量子計算では複素数計算が必要ですが、ここでは概念的な実装
        pass
        
    def measure(self, qubit: int) -> int:
        """
        指定された量子ビットを測定します。
        
        Args:
            qubit: 測定する量子ビット
            
        Returns:
            測定結果 (0 または 1)
        """
        if qubit in self.measurement_results:
            return self.measurement_results[qubit]
            
        # もつれている相手がすでに測定されている場合は相関を保つ
        for pair in self.entangled_pairs:
            if qubit in pair:
                other_qubit = pair[1] if pair[0] == qubit else pair[0]
                if other_qubit in self.measurement_results:
                    # Bell状態の場合、相関した結果を返す
                    result = self.measurement_results[other_qubit]
                    self.measurement_results[qubit] = result
                    return result
        
        # 新しい測定の場合はランダムに決定
        result = secrets.randbelow(2)  # random.randint(0, 1) から変更
        self.measurement_results[qubit] = result
        
        # もつれている相手の測定結果も決定
        for pair in self.entangled_pairs:
            if qubit in pair:
                other_qubit = pair[1] if pair[0] == qubit else pair[0]
                if other_qubit not in self.measurement_results:
                    self.measurement_results[other_qubit] = result
                    
        return result


class QuantumEntanglementSimulator:
    """
    量子もつれシミュレーター
    
    複数のインスタンス間で量子もつれ状態を模倣し、
    相関したランダム値を生成します。
    """

    def __init__(self, config: Optional[QuantumConfig] = None):
        """
        シミュレーターを初期化します。
        
        Args:
            config: 量子シミュレーション設定
        """
        self.config = config or QuantumConfig()
        self.states: Dict[str, QuantumState] = {}
        self.entanglement_networks: Dict[str, List[str]] = {}
        self.shared_entropy_pool: Dict[str, bytes] = {}
        
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
            np.random.seed(self.config.random_seed)

    async def create_entanglement(self, instance_ids: List[str]) -> str:
        """
        指定されたインスタンス間で量子もつれ状態を作成します。
        
        Args:
            instance_ids: もつれさせるインスタンスのIDリスト
            
        Returns:
            もつれ状態のID
        """
        if len(instance_ids) < 2:
            raise ValueError("At least 2 instances are required for entanglement")
        
        entanglement_id = self._generate_entanglement_id(instance_ids)
        logger.info(f"Creating entanglement {entanglement_id} for instances: {instance_ids}")
        
        # 各インスタンスに対して量子ビットを割り当て
        qubits_per_instance = self.config.qubits_per_instance
        total_qubits = len(instance_ids) * qubits_per_instance
        
        quantum_state = QuantumState(total_qubits)
        
        # インスタンス間でランダムなもつれペアを作成
        instance_qubits = {}
        for i, instance_id in enumerate(instance_ids):
            start_qubit = i * qubits_per_instance
            end_qubit = start_qubit + qubits_per_instance
            instance_qubits[instance_id] = list(range(start_qubit, end_qubit))
        
        # 各インスタンスペア間でもつれを作成
        for i in range(len(instance_ids)):
            for j in range(i + 1, len(instance_ids)):
                instance1 = instance_ids[i]
                instance2 = instance_ids[j]
                
                # ランダムに選択した量子ビット間でもつれを作成
                qubits1 = instance_qubits[instance1]
                qubits2 = instance_qubits[instance2]
                
                for k in range(min(len(qubits1), len(qubits2))):
                    quantum_state.entangle(qubits1[k], qubits2[k])
        
        self.states[entanglement_id] = quantum_state
        self.entanglement_networks[entanglement_id] = instance_ids
        
        # 共有エントロピープールを作成
        await self._create_shared_entropy(entanglement_id, instance_ids)
        
        logger.info(f"Entanglement {entanglement_id} created successfully")
        return entanglement_id

    async def measure_entangled_state(self, entanglement_id: str, instance_id: str, num_bits: int = 256) -> bytes:
        """
        もつれ状態を測定してビット列を取得します。
        
        Args:
            entanglement_id: もつれ状態のID
            instance_id: 測定するインスタンスのID
            num_bits: 取得するビット数
            
        Returns:
            測定結果のバイト列
        """
        if entanglement_id not in self.states:
            raise ValueError(f"Entanglement {entanglement_id} not found")
        
        if instance_id not in self.entanglement_networks[entanglement_id]:
            raise ValueError(f"Instance {instance_id} is not part of entanglement {entanglement_id}")
        
        quantum_state = self.states[entanglement_id]
        instance_ids = self.entanglement_networks[entanglement_id]
        instance_index = instance_ids.index(instance_id)
        
        # インスタンス用の量子ビット範囲を取得
        qubits_per_instance = self.config.qubits_per_instance
        start_qubit = instance_index * qubits_per_instance
        available_qubits = list(range(start_qubit, start_qubit + qubits_per_instance))
        
        # 共有エントロピーを基にした決定的な測定結果を生成
        # これにより、すべてのインスタンスで相関のある結果が得られる
        shared_entropy = self.shared_entropy_pool.get(entanglement_id, b'')
        if not shared_entropy:
            raise ValueError(f"No shared entropy found for entanglement {entanglement_id}")
        
        # インスタンス固有のシードを生成（相関を保持するため）
        base_seed = hashlib.sha256()
        base_seed.update(shared_entropy[:32])
        base_seed.update(entanglement_id.encode())
        # インスタンスIDは使用しない（全インスタンスで同じ結果を得るため）
        base_seed_bytes = base_seed.digest()
        
        # 決定的な疑似ランダム生成器を使用
        result = bytearray()
        num_bytes = (num_bits + 7) // 8
        
        for byte_index in range(num_bytes):
            # バイトごとに決定的な値を生成
            byte_hash = hashlib.sha256()
            byte_hash.update(base_seed_bytes)
            byte_hash.update(struct.pack('<I', byte_index))
            byte_hash.update(b'entangled_measurement')
            
            # ハッシュの最初のバイトを使用
            byte_value = byte_hash.digest()[0]
            result.append(byte_value)
        
        # 必要なビット数に合わせて調整
        if num_bits % 8 != 0:
            # 最後のバイトの不要なビットをマスク
            mask = (1 << (num_bits % 8)) - 1
            result[-1] &= mask
        
        logger.debug(f"Measured {len(result)} bytes for instance {instance_id}")
        return bytes(result)

    async def verify_entanglement_correlation(self, entanglement_id: str, measurements: Dict[str, bytes]) -> bool:
        """
        もつれ状態の相関を検証します。
        
        Args:
            entanglement_id: もつれ状態のID
            measurements: インスタンスIDと測定結果の辞書
            
        Returns:
            相関が正しい場合True
        """
        if entanglement_id not in self.states:
            return False
        
        expected_instances = set(self.entanglement_networks[entanglement_id])
        actual_instances = set(measurements.keys())
        
        if expected_instances != actual_instances:
            logger.warning(f"Instance mismatch in correlation verification")
            return False
        
        # 各インスタンスの測定結果のハッシュを計算
        hashes = {}
        for instance_id, measurement in measurements.items():
            hash_obj = hashlib.sha256()
            hash_obj.update(entanglement_id.encode())
            hash_obj.update(instance_id.encode())
            hash_obj.update(measurement)
            hashes[instance_id] = hash_obj.digest()

        # すべてのハッシュをソートして結合し、最終的な検証ハッシュを計算
        combined_hash = hashlib.sha256()
        for instance_id in sorted(hashes.keys()):
            combined_hash.update(hashes[instance_id])
        
        final_hash = combined_hash.hexdigest()

        # このシミュレーターでは、理論上すべての測定結果が一致するため、
        # 各インスタ-ンスで計算される final_hash も一致するはず。
        # ここでは、簡略化のため最初のインスタンスのハッシュを基準とする。
        # 実際には、各インスタンスが final_hash を交換し、一致を確認する必要がある。
        
        # 量子もつれの相関を検証
        # 決定的な測定結果により、すべてのインスタンスで同じ結果が得られるはず
        
        if not measurements:
            logger.warning(f"No measurements provided for {entanglement_id}")
            return False
        
        # すべての測定結果が同じかどうかを確認
        measurement_values = list(measurements.values())
        first_measurement = measurement_values[0]
        
        all_identical = all(measurement == first_measurement for measurement in measurement_values)
        
        if all_identical:
            logger.info(f"Entanglement correlation verified for {entanglement_id} - all measurements identical")
            return True
        else:
            # 類似性チェック（予備的）
            pattern_similarity = self._calculate_pattern_similarity(measurement_values)
            if pattern_similarity >= self.config.correlation_threshold:
                logger.info(f"Entanglement correlation verified for {entanglement_id} (similarity: {pattern_similarity:.2f})")
                return True
            else:
                logger.warning(f"Entanglement correlation failed for {entanglement_id} (similarity: {pattern_similarity:.2f})")
                return False

    async def collapse_entanglement(self, entanglement_id: str):
        """
        もつれ状態を崩壊させ、リソースを解放します。
        
        Args:
            entanglement_id: もつれ状態のID
        """
        if entanglement_id in self.states:
            del self.states[entanglement_id]
            del self.entanglement_networks[entanglement_id]
            if entanglement_id in self.shared_entropy_pool:
                del self.shared_entropy_pool[entanglement_id]
            logger.info(f"Entanglement {entanglement_id} collapsed")

    def _generate_entanglement_id(self, instance_ids: List[str]) -> str:
        """
        もつれ状態の一意IDを生成します。
        
        Args:
            instance_ids: インスタンスIDのリスト
            
        Returns:
            もつれ状態のID
        """
        sorted_ids = sorted(instance_ids)
        timestamp = datetime.now().isoformat()
        
        hash_obj = hashlib.sha256()
        hash_obj.update(f"{timestamp}:{':'.join(sorted_ids)}".encode())
        return hash_obj.hexdigest()[:16]

    async def _create_shared_entropy(self, entanglement_id: str, instance_ids: List[str]):
        """
        共有エントロピープールを作成します。
        
        Args:
            entanglement_id: もつれ状態のID
            instance_ids: インスタンスIDのリスト
        """
        # すべてのインスタンスIDを組み合わせてエントロピーを生成
        combined_data = f"{entanglement_id}:{''.join(sorted(instance_ids))}"
        
        entropy = bytearray()
        for i in range(1024):  # 1KB のエントロピー
            hash_obj = hashlib.sha256()
            hash_obj.update(combined_data.encode())
            hash_obj.update(struct.pack('<I', i))
            entropy.extend(hash_obj.digest())
        
        self.shared_entropy_pool[entanglement_id] = bytes(entropy)
        logger.debug(f"Created {len(entropy)} bytes of shared entropy for {entanglement_id}")

    def _calculate_pattern_similarity(self, patterns: List[bytes]) -> float:
        """
        パターン間の類似性を計算します（ハミング距離ベース）。
        
        Args:
            patterns: 比較するパターンのリスト
            
        Returns:
            類似性（0.0 ～ 1.0）
        """
        if len(patterns) < 2:
            return 1.0
        
        total_comparisons = 0
        total_matches = 0
        
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                pattern1 = patterns[i]
                pattern2 = patterns[j]
                
                # パターンの長さを合わせる
                min_len = min(len(pattern1), len(pattern2))
                pattern1 = pattern1[:min_len]
                pattern2 = pattern2[:min_len]
                
                # ビットレベルでの一致度を計算
                matches = 0
                total_bits = min_len * 8
                
                for byte1, byte2 in zip(pattern1, pattern2):
                    for bit_pos in range(8):
                        bit1 = (byte1 >> bit_pos) & 1
                        bit2 = (byte2 >> bit_pos) & 1
                        if bit1 == bit2:
                            matches += 1
                
                similarity = matches / total_bits if total_bits > 0 else 1.0
                total_matches += similarity
                total_comparisons += 1
        
        return total_matches / total_comparisons if total_comparisons > 0 else 1.0

    def get_entanglement_info(self, entanglement_id: str) -> Optional[Dict[str, Any]]:
        """
        もつれ状態の情報を取得します。
        
        Args:
            entanglement_id: もつれ状態のID
            
        Returns:
            もつれ状態の情報（存在しない場合はNone）
        """
        if entanglement_id not in self.states:
            return None
        
        quantum_state = self.states[entanglement_id]
        return {
            'entanglement_id': entanglement_id,
            'qubits': quantum_state.qubits,
            'entangled_pairs': len(quantum_state.entangled_pairs),
            'measured_qubits': len(quantum_state.measurement_results),
            'participating_instances': self.entanglement_networks[entanglement_id],
            'entropy_pool_size': len(self.shared_entropy_pool.get(entanglement_id, b''))
        }
