"""
暗号化・セッションキー生成モジュール

量子もつれシミュレーションの結果を基に、セキュアなセッションキーの生成と管理を行います。
"""

import hashlib
import hmac
import logging
import secrets
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import struct

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box

from .exceptions import CryptoError
from .config import CryptoConfig


logger = logging.getLogger(__name__)


class SessionKeyGenerator:
    """
    量子もつれ状態を基にしたセッションキー生成器
    """

    def __init__(self, key_length: int = 256, config: Optional['CryptoConfig'] = None):
        """
        セッションキー生成器を初期化します。

        Args:
            key_length: 生成するキーの長さ（ビット）
            config: 暗号化設定
        """
        if config is None:
            from .config import CryptoConfig
            config = CryptoConfig(key_length=key_length)
        
        self.config = config
        self.key_length = key_length
        self.key_bytes = self.key_length // 8
        self.active_keys: Dict[str, bytes] = {}
        self.key_derivation_counter = 0

        # RSA キーペアを生成（キー交換用）
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.rsa_key_size
        )
        self.public_key = self.private_key.public_key()

        # NaCl キーペア（高速暗号化用）
        self.nacl_private_key = PrivateKey.generate()
        self.nacl_public_key = self.nacl_private_key.public_key

    async def generate_key(self, entanglement_state: str, partner_instances: List[str]) -> bytes:
        """
        量子もつれ状態を基にセッションキーを生成します。

        Args:
            entanglement_state: 量子もつれ状態のID
            partner_instances: パートナーインスタンスのリスト

        Returns:
            生成されたセッションキー
        """
        try:
            logger.info(f"Generating session key from entanglement {entanglement_state}")

            # 基本エントロピーを生成
            base_entropy = self._generate_base_entropy(entanglement_state, partner_instances)

            # 量子もつれ由来のエントロピーを取得（模擬）
            quantum_entropy = await self._extract_quantum_entropy(entanglement_state)

            # 時間的エントロピーを追加
            temporal_entropy = self._generate_temporal_entropy()

            # すべてのエントロピーを結合
            combined_entropy = base_entropy + quantum_entropy + temporal_entropy

            # HKDF を使用してキーを導出
            session_key = self._derive_session_key(
                combined_entropy,
                entanglement_state,
                partner_instances
            )

            # 生成されたキーを検証
            if not self._validate_key_quality(session_key):
                raise CryptoError("Generated key failed quality validation")

            logger.info(f"Session key generated successfully ({len(session_key)} bytes)")
            return session_key

        except Exception as e:
            logger.error(f"Failed to generate session key: {e}", exc_info=True)
            raise CryptoError("Key generation failed due to an internal error.")

    def _generate_base_entropy(self, entanglement_state: str, partner_instances: List[str]) -> bytes:
        """
        基本エントロピーを生成します。

        Args:
            entanglement_state: 量子もつれ状態のID
            partner_instances: パートナーインスタンスのリスト

        Returns:
            基本エントロピー
        """
        hasher = hashlib.sha512()
        hasher.update(entanglement_state.encode())

        # パートナーインスタンスをソートして決定的な順序を確保
        sorted_partners = sorted(partner_instances)
        for partner in sorted_partners:
            hasher.update(partner.encode())

        # カウンターを追加して一意性を確保
        self.key_derivation_counter += 1
        hasher.update(struct.pack('<Q', self.key_derivation_counter))

        return hasher.digest()

    async def _extract_quantum_entropy(self, entanglement_state: str) -> bytes:
        """
        量子もつれ状態からエントロピーを抽出します（模擬）。

        Args:
            entanglement_state: 量子もつれ状態のID

        Returns:
            量子エントロピー
        """
        # 実際の実装では量子シミュレーターから測定結果を取得
        # ここでは決定的だが安全な方法でエントロピーを生成
        
        quantum_seed = hashlib.sha256(entanglement_state.encode()).digest()
        
        # 疑似量子ランダム性を生成
        quantum_entropy = bytearray()
        for i in range(64):  # 64バイトの量子エントロピー
            hasher = hashlib.sha256()
            hasher.update(quantum_seed)
            hasher.update(struct.pack('<I', i))
            hasher.update(b'quantum_measurement')
            quantum_entropy.extend(hasher.digest()[:1])

        return bytes(quantum_entropy)

    def _generate_temporal_entropy(self) -> bytes:
        """
        時間的エントロピーを生成します。

        Returns:
            時間的エントロピー
        """
        timestamp = datetime.now()
        
        hasher = hashlib.sha256()
        hasher.update(timestamp.isoformat().encode())
        hasher.update(struct.pack('<f', timestamp.timestamp()))
        
        # 高精度タイムスタンプを追加
        import time
        hasher.update(struct.pack('<Q', int(time.time_ns())))
        
        # システム乱数を追加
        hasher.update(secrets.token_bytes(32))
        
        return hasher.digest()

    def _derive_session_key(self, entropy: bytes, entanglement_id: str, partners: List[str]) -> bytes:
        """
        HKDF を使用してセッションキーを導出します。

        Args:
            entropy: エントロピー源
            entanglement_id: もつれ状態のID
            partners: パートナーインスタンスのリスト

        Returns:
            導出されたセッションキー
        """
        # 情報文字列を構築
        info_parts = [
            b'EntangleKey-SessionKey',
            entanglement_id.encode(),
        ]
        
        for partner in sorted(partners):
            info_parts.append(partner.encode())
        
        info = b':'.join(info_parts)
        
        # HKDF でキーを導出
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_bytes,
            salt=None,
            info=info,
        )
        
        return hkdf.derive(entropy)

    def _validate_key_quality(self, key: bytes) -> bool:
        """
        生成されたキーの品質を検証します。

        Args:
            key: 検証するキー

        Returns:
            キーが適切な品質を持つ場合True
        """
        if len(key) != self.key_bytes:
            return False

        # エントロピー分析
        bit_counts = [0, 0]
        for byte in key:
            for i in range(8):
                bit = (byte >> i) & 1
                bit_counts[bit] += 1

        total_bits = len(key) * 8
        zero_ratio = bit_counts[0] / total_bits
        one_ratio = bit_counts[1] / total_bits

        # ビット比率が極端でないことを確認
        if zero_ratio < 0.4 or zero_ratio > 0.6:
            logger.warning(f"Key quality check failed: unbalanced bits (0s: {zero_ratio:.3f})")
            return False

        # 連続する同じバイトの検出
        consecutive_count = 1
        max_consecutive = 1
        for i in range(1, len(key)):
            if key[i] == key[i-1]:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1

        if max_consecutive > 4:  # 4バイト以上の連続は疑わしい
            logger.warning(f"Key quality check failed: too many consecutive bytes ({max_consecutive})")
            return False

        return True

    def hash_key(self, key: bytes) -> str:
        """
        キーのハッシュ値を計算します（検証用）。

        Args:
            key: ハッシュ化するキー

        Returns:
            ハッシュ値（16進数文字列）
        """
        return hashlib.sha256(key).hexdigest()

    def encrypt_data(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """
        データを暗号化します。

        Args:
            data: 暗号化するデータ
            key: 暗号化キー

        Returns:
            (暗号化されたデータ, ナンス)のタプル
        """
        try:
            box = nacl.secret.SecretBox(key[:32])  # NaCl は32バイトキーを使用
            encrypted = box.encrypt(data)
            return encrypted.ciphertext, encrypted.nonce
        except Exception as e:
            logger.error(f"Encryption failed: {e}", exc_info=True)
            raise CryptoError("Encryption failed due to an internal error.")

    def decrypt_data(self, encrypted_data: bytes, nonce: bytes, key: bytes) -> bytes:
        """
        データを復号化します。

        Args:
            encrypted_data: 暗号化されたデータ
            nonce: ナンス
            key: 復号化キー

        Returns:
            復号化されたデータ
        """
        try:
            box = nacl.secret.SecretBox(key[:32])
            decrypted = box.decrypt(encrypted_data, nonce)
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {e}", exc_info=True)
            raise CryptoError("Decryption failed due to an internal error.")

    def create_message_signature(self, message: bytes, key: bytes) -> bytes:
        """
        メッセージの署名を作成します。

        Args:
            message: 署名するメッセージ
            key: 署名キー

        Returns:
            署名
        """
        return hmac.new(key, message, hashlib.sha256).digest()

    def verify_message_signature(self, message: bytes, signature: bytes, key: bytes) -> bool:
        """
        メッセージの署名を検証します。

        Args:
            message: 元のメッセージ
            signature: 署名
            key: 検証キー

        Returns:
            署名が正しい場合True
        """
        try:
            expected_signature = hmac.new(key, message, hashlib.sha256).digest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}", exc_info=True)
            return False

    async def rotate_key(self, old_key: bytes, entanglement_state: str, partners: List[str]) -> bytes:
        """
        既存のキーを基に新しいキーを生成します（キーローテーション）。

        Args:
            old_key: 古いキー
            entanglement_state: 量子もつれ状態のID
            partners: パートナーインスタンス

        Returns:
            新しいキー
        """
        # 古いキーと新しいエントロピーを組み合わせ
        rotation_entropy = self._generate_base_entropy(entanglement_state, partners)
        
        hasher = hashlib.sha512()
        hasher.update(old_key)
        hasher.update(rotation_entropy)
        hasher.update(b'key_rotation')
        hasher.update(struct.pack('<Q', int(datetime.now().timestamp())))
        
        combined_entropy = hasher.digest()
        
        # 新しいキーを導出
        new_key = self._derive_session_key(
            combined_entropy,
            f"{entanglement_state}_rotated",
            partners
        )
        
        logger.info("Session key rotated successfully")
        return new_key

    def get_public_key_pem(self) -> bytes:
        """
        RSA公開キーのPEM形式を取得します。

        Returns:
            PEM形式の公開キー
        """
        return self.public_key.public_key_pem()

    def get_nacl_public_key(self) -> bytes:
        """
        NaCl公開キーを取得します。

        Returns:
            NaCl公開キー
        """
        return bytes(self.nacl_public_key)

    def encrypt_with_public_key(self, data: bytes, public_key_pem: bytes) -> bytes:
        """
        公開キーでデータを暗号化します。

        Args:
            data: 暗号化するデータ
            public_key_pem: PEM形式の公開キー

        Returns:
            暗号化されたデータ
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            encrypted = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted
        except Exception as e:
            logger.error(f"Public key encryption failed: {e}", exc_info=True)
            raise CryptoError("Public key encryption failed due to an internal error.")

    def decrypt_with_private_key(self, encrypted_data: bytes) -> bytes:
        """
        秘密キーでデータを復号化します。

        Args:
            encrypted_data: 暗号化されたデータ

        Returns:
            復号化されたデータ
        """
        try:
            decrypted = self.private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted
        except Exception as e:
            logger.error(f"Private key decryption failed: {e}", exc_info=True)
            raise CryptoError("Private key decryption failed due to an internal error.")

    def create_key_exchange_box(self, remote_public_key: bytes) -> Box:
        """
        NaClキー交換用のBoxを作成します。

        Args:
            remote_public_key: 相手の公開キー

        Returns:
            NaCl Box
        """
        try:
            remote_key = PublicKey(remote_public_key)
            return Box(self.nacl_private_key, remote_key)
        except Exception as e:
            logger.error(f"Failed to create key exchange box: {e}", exc_info=True)
            raise CryptoError("Key exchange box creation failed due to an internal error.")

    def get_key_info(self, key: bytes) -> Dict[str, Any]:
        """
        キーの情報を取得します。

        Args:
            key: 分析するキー

        Returns:
            キー情報の辞書
        """
        info = {
            'length_bytes': len(key),
            'length_bits': len(key) * 8,
            'hash_sha256': hashlib.sha256(key).hexdigest(),
            'hash_sha512': hashlib.sha512(key).hexdigest()[:32],  # 最初の32文字のみ
        }

        # エントロピー分析
        bit_counts = [0, 0]
        byte_frequencies = {}
        
        for byte in key:
            if byte in byte_frequencies:
                byte_frequencies[byte] += 1
            else:
                byte_frequencies[byte] = 1
                
            for i in range(8):
                bit = (byte >> i) & 1
                bit_counts[bit] += 1

        total_bits = len(key) * 8
        info['bit_balance'] = {
            'zeros': bit_counts[0],
            'ones': bit_counts[1],
            'zero_ratio': bit_counts[0] / total_bits,
            'one_ratio': bit_counts[1] / total_bits
        }

        info['byte_diversity'] = {
            'unique_bytes': len(byte_frequencies),
            'most_frequent_byte': max(byte_frequencies, key=byte_frequencies.get),
            'max_frequency': max(byte_frequencies.values())
        }

        return info
