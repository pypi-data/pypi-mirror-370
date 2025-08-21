"""
EntangleKey 基本テスト

ライブラリの基本機能をテストします。
"""

import pytest
import asyncio
from entanglekey import EntangleKeyManager, QuantumEntanglementSimulator, SessionKeyGenerator


class TestQuantumEntanglementSimulator:
    """量子もつれシミュレーターのテスト"""
    
    def test_simulator_initialization(self):
        """シミュレーターの初期化テスト"""
        simulator = QuantumEntanglementSimulator()
        assert isinstance(simulator, QuantumEntanglementSimulator)
    
    @pytest.mark.asyncio
    async def test_create_entanglement(self):
        """もつれ状態の作成テスト"""
        simulator = QuantumEntanglementSimulator()
        instance_ids = ["instance_1", "instance_2"]
        
        entanglement_id = await simulator.create_entanglement(instance_ids)
        assert isinstance(entanglement_id, str)
        assert len(entanglement_id) > 0
    
    @pytest.mark.asyncio
    async def test_measure_entangled_state(self):
        """もつれ状態の測定テスト"""
        simulator = QuantumEntanglementSimulator()
        instance_ids = ["instance_1", "instance_2"]
        
        entanglement_id = await simulator.create_entanglement(instance_ids)
        measurement = await simulator.measure_entangled_state(
            entanglement_id, "instance_1", num_bits=256
        )
        
        assert isinstance(measurement, bytes)
        assert len(measurement) == 32  # 256 bits = 32 bytes
    
    @pytest.mark.asyncio
    async def test_verify_entanglement_correlation(self):
        """もつれ相関の検証テスト"""
        simulator = QuantumEntanglementSimulator()
        instance_ids = ["instance_1", "instance_2"]
        
        entanglement_id = await simulator.create_entanglement(instance_ids)
        
        # 両方のインスタンスで測定
        measurement1 = await simulator.measure_entangled_state(
            entanglement_id, "instance_1", num_bits=256
        )
        measurement2 = await simulator.measure_entangled_state(
            entanglement_id, "instance_2", num_bits=256
        )
        
        measurements = {
            "instance_1": measurement1,
            "instance_2": measurement2
        }
        
        # 相関検証（シミュレーション環境では常にTrueになる設計）
        is_correlated = await simulator.verify_entanglement_correlation(
            entanglement_id, measurements
        )
        assert is_correlated is True


class TestSessionKeyGenerator:
    """セッションキー生成器のテスト"""
    
    def test_generator_initialization(self):
        """生成器の初期化テスト"""
        generator = SessionKeyGenerator(key_length=256)
        assert generator.key_length == 256
        assert generator.key_bytes == 32
    
    @pytest.mark.asyncio
    async def test_generate_key(self):
        """キー生成テスト"""
        generator = SessionKeyGenerator(key_length=256)
        entanglement_state = "test_entanglement_123"
        partner_instances = ["partner_1", "partner_2"]
        
        session_key = await generator.generate_key(entanglement_state, partner_instances)
        
        assert isinstance(session_key, bytes)
        assert len(session_key) == 32  # 256 bits = 32 bytes
    
    def test_hash_key(self):
        """キーハッシュテスト"""
        generator = SessionKeyGenerator()
        test_key = b"test_key_data_12345678901234567890"
        
        key_hash = generator.hash_key(test_key)
        assert isinstance(key_hash, str)
        assert len(key_hash) == 64  # SHA256 hash is 64 hex characters
    
    def test_encrypt_decrypt_data(self):
        """データ暗号化・復号化テスト"""
        generator = SessionKeyGenerator()
        test_data = b"This is a secret message for testing"
        test_key = b"test_encryption_key_32_bytes_long!"
        
        # 暗号化
        encrypted_data, nonce = generator.encrypt_data(test_data, test_key)
        assert isinstance(encrypted_data, bytes)
        assert isinstance(nonce, bytes)
        assert len(encrypted_data) > 0
        assert len(nonce) > 0
        
        # 復号化
        decrypted_data = generator.decrypt_data(encrypted_data, nonce, test_key)
        assert decrypted_data == test_data
    
    def test_message_signature(self):
        """メッセージ署名テスト"""
        generator = SessionKeyGenerator()
        test_message = b"Test message for signature verification"
        test_key = b"test_signature_key_32_bytes_long!!"
        
        # 署名作成
        signature = generator.create_message_signature(test_message, test_key)
        assert isinstance(signature, bytes)
        assert len(signature) > 0
        
        # 署名検証
        is_valid = generator.verify_message_signature(test_message, signature, test_key)
        assert is_valid is True
        
        # 無効な署名検証
        wrong_signature = b"invalid_signature_data"
        is_invalid = generator.verify_message_signature(test_message, wrong_signature, test_key)
        assert is_invalid is False


class TestEntangleKeyManager:
    """EntangleKeyマネージャーのテスト"""
    
    def test_manager_initialization(self):
        """マネージャーの初期化テスト"""
        manager = EntangleKeyManager(
            instance_id="test_instance",
            network_port=9999,
            key_length=256
        )
        
        assert manager.instance_id == "test_instance"
        assert manager.network_port == 9999
        assert manager.key_length == 256
        assert manager.is_running is False
    
    @pytest.mark.asyncio
    async def test_manager_start_stop(self):
        """マネージャーの開始・停止テスト"""
        manager = EntangleKeyManager(
            instance_id="test_instance",
            network_port=9998  # 他のテストと被らないポート
        )
        
        # 開始
        await manager.start()
        assert manager.is_running is True
        
        # 停止
        await manager.stop()
        assert manager.is_running is False
    
    def test_get_status(self):
        """ステータス取得テスト"""
        manager = EntangleKeyManager(
            instance_id="test_instance",
            network_port=9997
        )
        
        status = manager.get_status()
        assert isinstance(status, dict)
        assert "instance_id" in status
        assert "is_running" in status
        assert "connected_instances" in status
        assert "active_sessions" in status
        assert "network_port" in status
        
        assert status["instance_id"] == "test_instance"
        assert status["is_running"] is False
        assert status["network_port"] == 9997


@pytest.mark.asyncio
async def test_full_key_generation_workflow():
    """完全なキー生成ワークフローのテスト"""
    # シミュレーターでもつれ状態を作成
    simulator = QuantumEntanglementSimulator()
    instance_ids = ["test_instance_1", "test_instance_2"]
    entanglement_id = await simulator.create_entanglement(instance_ids)
    
    # キー生成器でセッションキーを生成
    generator = SessionKeyGenerator(key_length=256)
    session_key = await generator.generate_key(entanglement_id, instance_ids[1:])
    
    # キーの品質を確認
    assert isinstance(session_key, bytes)
    assert len(session_key) == 32
    
    # キー情報を取得
    key_info = generator.get_key_info(session_key)
    assert key_info["length_bytes"] == 32
    assert key_info["length_bits"] == 256
    assert "hash_sha256" in key_info
    assert "bit_balance" in key_info


if __name__ == "__main__":
    pytest.main([__file__])
