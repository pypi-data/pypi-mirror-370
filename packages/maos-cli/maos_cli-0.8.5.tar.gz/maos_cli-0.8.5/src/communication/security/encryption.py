"""Message encryption and decryption capabilities."""

import os
import logging
from typing import Any, Dict, Optional, Tuple
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

logger = logging.getLogger(__name__)


class CipherSuite(Enum):
    """Available encryption cipher suites."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc" 
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_OAEP = "rsa_oaep"
    HYBRID = "hybrid"  # RSA + AES


class EncryptionError(Exception):
    """Encryption-related errors."""
    pass


class EncryptionManager:
    """Handles encryption and decryption of messages."""
    
    def __init__(
        self,
        default_cipher: CipherSuite = CipherSuite.AES_256_GCM,
        key_derivation_iterations: int = 100000
    ):
        self.default_cipher = default_cipher
        self.key_derivation_iterations = key_derivation_iterations
        
        # Key storage
        self.symmetric_keys: Dict[str, bytes] = {}
        self.asymmetric_keys: Dict[str, Tuple[bytes, bytes]] = {}  # (public, private)
        self.master_key: Optional[bytes] = None
        
        # Cipher instances
        self.fernet_instances: Dict[str, Fernet] = {}
        
        logger.info("Encryption manager initialized")
    
    def generate_master_key(self, passphrase: Optional[str] = None) -> bytes:
        """Generate or derive master key."""
        try:
            if passphrase:
                # Derive key from passphrase
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=self.key_derivation_iterations,
                )
                key = kdf.derive(passphrase.encode())
                self.master_key = salt + key  # Store salt with key
            else:
                # Generate random key
                self.master_key = os.urandom(32)
            
            logger.info("Master key generated")
            return self.master_key
            
        except Exception as e:
            logger.error(f"Failed to generate master key: {e}")
            raise EncryptionError(f"Master key generation failed: {e}")
    
    def load_master_key(self, key_data: bytes, passphrase: Optional[str] = None) -> bool:
        """Load master key from data."""
        try:
            if passphrase and len(key_data) > 32:
                # Extract salt and derive key
                salt = key_data[:16]
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=self.key_derivation_iterations,
                )
                derived_key = kdf.derive(passphrase.encode())
                
                # Verify key
                if key_data[16:] == derived_key:
                    self.master_key = derived_key
                    logger.info("Master key loaded and verified")
                    return True
                else:
                    logger.error("Invalid passphrase for master key")
                    return False
            else:
                self.master_key = key_data
                logger.info("Master key loaded")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load master key: {e}")
            return False
    
    def generate_symmetric_key(self, key_id: str, cipher: Optional[CipherSuite] = None) -> bytes:
        """Generate symmetric encryption key."""
        try:
            cipher = cipher or self.default_cipher
            
            if cipher == CipherSuite.FERNET:
                key = Fernet.generate_key()
                self.fernet_instances[key_id] = Fernet(key)
            else:
                key = os.urandom(32)  # 256-bit key for AES/ChaCha20
            
            self.symmetric_keys[key_id] = key
            logger.info(f"Generated symmetric key: {key_id}")
            return key
            
        except Exception as e:
            logger.error(f"Failed to generate symmetric key: {e}")
            raise EncryptionError(f"Symmetric key generation failed: {e}")
    
    def generate_asymmetric_keypair(self, key_id: str, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """Generate RSA asymmetric key pair."""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Store keys
            self.asymmetric_keys[key_id] = (public_pem, private_pem)
            
            logger.info(f"Generated asymmetric key pair: {key_id}")
            return public_pem, private_pem
            
        except Exception as e:
            logger.error(f"Failed to generate asymmetric key pair: {e}")
            raise EncryptionError(f"Asymmetric key generation failed: {e}")
    
    def import_public_key(self, key_id: str, public_key_pem: bytes):
        """Import a public key for encryption."""
        try:
            # Validate key format
            public_key = serialization.load_pem_public_key(public_key_pem)
            
            # Store only public key (no private key)
            self.asymmetric_keys[key_id] = (public_key_pem, b"")
            
            logger.info(f"Imported public key: {key_id}")
            
        except Exception as e:
            logger.error(f"Failed to import public key: {e}")
            raise EncryptionError(f"Public key import failed: {e}")
    
    def encrypt_message(
        self,
        plaintext: str,
        key_id: str,
        cipher: Optional[CipherSuite] = None
    ) -> Dict[str, Any]:
        """Encrypt a message."""
        try:
            cipher = cipher or self.default_cipher
            
            if cipher == CipherSuite.FERNET:
                return self._encrypt_fernet(plaintext, key_id)
            elif cipher == CipherSuite.AES_256_GCM:
                return self._encrypt_aes_gcm(plaintext, key_id)
            elif cipher == CipherSuite.AES_256_CBC:
                return self._encrypt_aes_cbc(plaintext, key_id)
            elif cipher == CipherSuite.RSA_OAEP:
                return self._encrypt_rsa(plaintext, key_id)
            elif cipher == CipherSuite.HYBRID:
                return self._encrypt_hybrid(plaintext, key_id)
            else:
                raise EncryptionError(f"Unsupported cipher: {cipher}")
                
        except Exception as e:
            logger.error(f"Message encryption failed: {e}")
            raise EncryptionError(f"Encryption failed: {e}")
    
    def decrypt_message(self, encrypted_data: Dict[str, Any]) -> str:
        """Decrypt a message."""
        try:
            cipher_suite = CipherSuite(encrypted_data["cipher"])
            key_id = encrypted_data["key_id"]
            
            if cipher_suite == CipherSuite.FERNET:
                return self._decrypt_fernet(encrypted_data, key_id)
            elif cipher_suite == CipherSuite.AES_256_GCM:
                return self._decrypt_aes_gcm(encrypted_data, key_id)
            elif cipher_suite == CipherSuite.AES_256_CBC:
                return self._decrypt_aes_cbc(encrypted_data, key_id)
            elif cipher_suite == CipherSuite.RSA_OAEP:
                return self._decrypt_rsa(encrypted_data, key_id)
            elif cipher_suite == CipherSuite.HYBRID:
                return self._decrypt_hybrid(encrypted_data, key_id)
            else:
                raise EncryptionError(f"Unsupported cipher: {cipher_suite}")
                
        except Exception as e:
            logger.error(f"Message decryption failed: {e}")
            raise EncryptionError(f"Decryption failed: {e}")
    
    def _encrypt_fernet(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """Encrypt using Fernet (AES 128 CBC + HMAC)."""
        if key_id not in self.fernet_instances:
            if key_id not in self.symmetric_keys:
                raise EncryptionError(f"Key not found: {key_id}")
            self.fernet_instances[key_id] = Fernet(self.symmetric_keys[key_id])
        
        fernet = self.fernet_instances[key_id]
        ciphertext = fernet.encrypt(plaintext.encode())
        
        return {
            "cipher": CipherSuite.FERNET.value,
            "key_id": key_id,
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "algorithm": "fernet"
        }
    
    def _decrypt_fernet(self, encrypted_data: Dict[str, Any], key_id: str) -> str:
        """Decrypt using Fernet."""
        if key_id not in self.fernet_instances:
            if key_id not in self.symmetric_keys:
                raise EncryptionError(f"Key not found: {key_id}")
            self.fernet_instances[key_id] = Fernet(self.symmetric_keys[key_id])
        
        fernet = self.fernet_instances[key_id]
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        plaintext = fernet.decrypt(ciphertext)
        
        return plaintext.decode()
    
    def _encrypt_aes_gcm(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """Encrypt using AES-256-GCM."""
        if key_id not in self.symmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        key = self.symmetric_keys[key_id]
        iv = os.urandom(16)  # 128-bit IV
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        
        return {
            "cipher": CipherSuite.AES_256_GCM.value,
            "key_id": key_id,
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "iv": base64.b64encode(iv).decode(),
            "tag": base64.b64encode(encryptor.tag).decode(),
            "algorithm": "aes-256-gcm"
        }
    
    def _decrypt_aes_gcm(self, encrypted_data: Dict[str, Any], key_id: str) -> str:
        """Decrypt using AES-256-GCM."""
        if key_id not in self.symmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        key = self.symmetric_keys[key_id]
        iv = base64.b64decode(encrypted_data["iv"])
        tag = base64.b64decode(encrypted_data["tag"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode()
    
    def _encrypt_aes_cbc(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """Encrypt using AES-256-CBC."""
        if key_id not in self.symmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        key = self.symmetric_keys[key_id]
        iv = os.urandom(16)
        
        # Pad plaintext to block size
        pad_length = 16 - (len(plaintext) % 16)
        padded_plaintext = plaintext + chr(pad_length) * pad_length
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_plaintext.encode()) + encryptor.finalize()
        
        return {
            "cipher": CipherSuite.AES_256_CBC.value,
            "key_id": key_id,
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "iv": base64.b64encode(iv).decode(),
            "algorithm": "aes-256-cbc"
        }
    
    def _decrypt_aes_cbc(self, encrypted_data: Dict[str, Any], key_id: str) -> str:
        """Decrypt using AES-256-CBC."""
        if key_id not in self.symmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        key = self.symmetric_keys[key_id]
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        pad_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-pad_length]
        
        return plaintext.decode()
    
    def _encrypt_rsa(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """Encrypt using RSA-OAEP."""
        if key_id not in self.asymmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        public_key_pem, _ = self.asymmetric_keys[key_id]
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        # RSA can only encrypt limited data, so we'll limit message size
        if len(plaintext) > 190:  # Conservative limit for 2048-bit key
            raise EncryptionError("Message too long for RSA encryption")
        
        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            "cipher": CipherSuite.RSA_OAEP.value,
            "key_id": key_id,
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "algorithm": "rsa-oaep-sha256"
        }
    
    def _decrypt_rsa(self, encrypted_data: Dict[str, Any], key_id: str) -> str:
        """Decrypt using RSA-OAEP."""
        if key_id not in self.asymmetric_keys:
            raise EncryptionError(f"Key not found: {key_id}")
        
        _, private_key_pem = self.asymmetric_keys[key_id]
        if not private_key_pem:
            raise EncryptionError(f"Private key not available: {key_id}")
        
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode()
    
    def _encrypt_hybrid(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """Encrypt using hybrid RSA + AES encryption."""
        # Generate session key for AES
        session_key = os.urandom(32)
        session_key_id = f"session_{os.urandom(8).hex()}"
        
        # Store session key temporarily
        self.symmetric_keys[session_key_id] = session_key
        
        try:
            # Encrypt message with AES
            aes_encrypted = self._encrypt_aes_gcm(plaintext, session_key_id)
            
            # Encrypt session key with RSA
            session_key_b64 = base64.b64encode(session_key).decode()
            rsa_encrypted = self._encrypt_rsa(session_key_b64, key_id)
            
            return {
                "cipher": CipherSuite.HYBRID.value,
                "key_id": key_id,
                "encrypted_session_key": rsa_encrypted["ciphertext"],
                "encrypted_data": aes_encrypted,
                "algorithm": "rsa-oaep+aes-256-gcm"
            }
        finally:
            # Clean up session key
            if session_key_id in self.symmetric_keys:
                del self.symmetric_keys[session_key_id]
    
    def _decrypt_hybrid(self, encrypted_data: Dict[str, Any], key_id: str) -> str:
        """Decrypt using hybrid RSA + AES encryption."""
        # Decrypt session key with RSA
        rsa_data = {
            "cipher": CipherSuite.RSA_OAEP.value,
            "key_id": key_id,
            "ciphertext": encrypted_data["encrypted_session_key"],
            "algorithm": "rsa-oaep-sha256"
        }
        
        session_key_b64 = self._decrypt_rsa(rsa_data, key_id)
        session_key = base64.b64decode(session_key_b64)
        session_key_id = f"session_{os.urandom(8).hex()}"
        
        # Store session key temporarily
        self.symmetric_keys[session_key_id] = session_key
        
        try:
            # Decrypt message with AES
            aes_data = encrypted_data["encrypted_data"]
            aes_data["key_id"] = session_key_id
            
            plaintext = self._decrypt_aes_gcm(aes_data, session_key_id)
            return plaintext
        finally:
            # Clean up session key
            if session_key_id in self.symmetric_keys:
                del self.symmetric_keys[session_key_id]
    
    def get_supported_ciphers(self) -> List[str]:
        """Get list of supported cipher suites."""
        return [cipher.value for cipher in CipherSuite]
    
    def has_key(self, key_id: str, key_type: str = "any") -> bool:
        """Check if a key is available."""
        if key_type == "symmetric" or key_type == "any":
            if key_id in self.symmetric_keys:
                return True
        
        if key_type == "asymmetric" or key_type == "any":
            if key_id in self.asymmetric_keys:
                return True
        
        return False
    
    def remove_key(self, key_id: str) -> bool:
        """Remove a key from storage."""
        removed = False
        
        if key_id in self.symmetric_keys:
            del self.symmetric_keys[key_id]
            removed = True
        
        if key_id in self.asymmetric_keys:
            del self.asymmetric_keys[key_id]
            removed = True
        
        if key_id in self.fernet_instances:
            del self.fernet_instances[key_id]
        
        if removed:
            logger.info(f"Removed key: {key_id}")
        
        return removed
    
    def clear_all_keys(self):
        """Clear all stored keys."""
        self.symmetric_keys.clear()
        self.asymmetric_keys.clear()
        self.fernet_instances.clear()
        self.master_key = None
        
        logger.warning("All encryption keys cleared")
    
    def get_key_info(self) -> Dict[str, Any]:
        """Get information about stored keys."""
        return {
            "symmetric_keys": list(self.symmetric_keys.keys()),
            "asymmetric_keys": list(self.asymmetric_keys.keys()),
            "has_master_key": self.master_key is not None,
            "default_cipher": self.default_cipher.value
        }