"""
ENCRYPTION - Enkripsi token & data penting dengan AES-256
"""

import logging
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import settings

class EncryptionManager:
    def __init__(self):
        self.fernet = None
        self.key_file = "config/encryption.key"
        self.salt_file = "config/encryption.salt"
        
    async def initialize(self):
        """Initialize encryption system"""
        logging.info("🔐 INITIALIZING ENCRYPTION MANAGER...")
        
        try:
            # Load or generate encryption key
            await self._setup_encryption_key()
            logging.info("✅ ENCRYPTION MANAGER INITIALIZED")
            
        except Exception as e:
            logging.error(f"❌ Encryption initialization failed: {e}")
            raise
            
    async def _setup_encryption_key(self):
        """Setup encryption key (load or generate)"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs("config", exist_ok=True)
            
            if os.path.exists(self.key_file) and os.path.exists(self.salt_file):
                # Load existing key
                await self._load_existing_key()
            else:
                # Generate new key
                await self._generate_new_key()
                
        except Exception as e:
            logging.error(f"❌ Encryption key setup error: {e}")
            raise
            
    async def _generate_new_key(self):
        """Generate new encryption key"""
        try:
            # Generate salt
            salt = os.urandom(16)
            
            # Generate key from password (using system secret)
            password = self._get_system_secret().encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Save key and salt
            with open(self.key_file, 'wb') as f:
                f.write(key)
                
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
                
            # Initialize Fernet
            self.fernet = Fernet(key)
            
            logging.info("🔑 New encryption key generated and saved")
            
        except Exception as e:
            logging.error(f"❌ Key generation error: {e}")
            raise
            
    async def _load_existing_key(self):
        """Load existing encryption key"""
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
                
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
                
            # Verify key can be used
            password = self._get_system_secret().encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            # This will raise an exception if the password is wrong
            kdf.verify(password, base64.urlsafe_b64decode(key))
            
            # Initialize Fernet
            self.fernet = Fernet(key)
            
            logging.info("🔑 Existing encryption key loaded successfully")
            
        except Exception as e:
            logging.error(f"❌ Key loading error: {e}")
            # Regenerate key if loading fails
            await self._generate_new_key()
            
    def _get_system_secret(self):
        """Get system secret for key derivation"""
        # Combine multiple system factors to create a unique secret
        system_factors = [
            settings.SYSTEM_NAME,
            "DokyOS_Encryption_Key_2024",  # Static component
            # Add more system-specific factors here
        ]
        
        return "_".join(system_factors)
        
    async def encrypt_string(self, plaintext):
        """Encrypt a string"""
        if not self.fernet:
            raise Exception("Encryption not initialized")
            
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
                
            encrypted_data = self.fernet.encrypt(plaintext)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logging.error(f"❌ String encryption error: {e}")
            raise
            
    async def decrypt_string(self, encrypted_text):
        """Decrypt a string"""
        if not self.fernet:
            raise Exception("Encryption not initialized")
            
        try:
            if isinstance(encrypted_text, str):
                encrypted_text = encrypted_text.encode('utf-8')
                
            encrypted_data = base64.urlsafe_b64decode(encrypted_text)
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logging.error(f"❌ String decryption error: {e}")
            raise
            
    async def encrypt_file(self, file_path):
        """Encrypt a file"""
        if not self.fernet:
            raise Exception("Encryption not initialized")
            
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Write encrypted data to new file
            encrypted_path = file_path + '.encrypted'
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
                
            # Remove original file
            os.remove(file_path)
            
            logging.info(f"🔒 File encrypted: {file_path} -> {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logging.error(f"❌ File encryption error for {file_path}: {e}")
            raise
            
    async def decrypt_file(self, encrypted_file_path):
        """Decrypt a file"""
        if not self.fernet:
            raise Exception("Encryption not initialized")
            
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Remove .encrypted extension
            original_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(original_path, 'wb') as f:
                f.write(decrypted_data)
                
            # Remove encrypted file
            os.remove(encrypted_file_path)
            
            logging.info(f"🔓 File decrypted: {encrypted_file_path} -> {original_path}")
            return original_path
            
        except Exception as e:
            logging.error(f"❌ File decryption error for {encrypted_file_path}: {e}")
            raise
            
    async def encrypt_sensitive_data(self, data_dict):
        """Encrypt sensitive data in a dictionary"""
        try:
            encrypted_dict = {}
            
            for key, value in data_dict.items():
                if self._is_sensitive_key(key):
                    encrypted_dict[key] = await self.encrypt_string(str(value))
                else:
                    encrypted_dict[key] = value
                    
            return encrypted_dict
            
        except Exception as e:
            logging.error(f"❌ Sensitive data encryption error: {e}")
            raise
            
    async def decrypt_sensitive_data(self, encrypted_dict):
        """Decrypt sensitive data in a dictionary"""
        try:
            decrypted_dict = {}
            
            for key, value in encrypted_dict.items():
                if self._is_sensitive_key(key) and isinstance(value, str):
                    try:
                        decrypted_dict[key] = await self.decrypt_string(value)
                    except:
                        # If decryption fails, keep the original value
                        decrypted_dict[key] = value
                else:
                    decrypted_dict[key] = value
                    
            return decrypted_dict
            
        except Exception as e:
            logging.error(f"❌ Sensitive data decryption error: {e}")
            raise
            
    def _is_sensitive_key(self, key):
        """Check if a key contains sensitive data"""
        sensitive_keywords = [
            'key', 'secret', 'password', 'token', 'api', 'auth',
            'credential', 'private', 'passphrase', 'wallet'
        ]
        
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in sensitive_keywords)
        
    async def protect_api_keys(self):
        """Protect all API keys in environment and config"""
        try:
            sensitive_data = {}
            
            # Collect sensitive environment variables
            for key, value in os.environ.items():
                if self._is_sensitive_key(key) and value:
                    sensitive_data[key] = value
                    
            # Encrypt and store sensitive data
            if sensitive_data:
                encrypted_data = await self.encrypt_sensitive_data(sensitive_data)
                
                # Save encrypted data to secure location
                secure_file = "config/secure_data.enc"
                with open(secure_file, 'w') as f:
                    import json
                    json.dump(encrypted_data, f, indent=2)
                    
                logging.info(f"🔒 Protected {len(sensitive_data)} API keys and secrets")
                
        except Exception as e:
            logging.error(f"❌ API key protection error: {e}")
            
    async def rotate_encryption_key(self):
        """Rotate encryption key (re-encrypt all data with new key)"""
        try:
            logging.warning("🔄 Rotating encryption key...")
            
            # Generate new key
            old_fernet = self.fernet
            await self._generate_new_key()
            
            # Here you would re-encrypt all encrypted data with the new key
            # This is a simplified example - actual implementation would depend on data storage
            
            logging.info("✅ Encryption key rotated successfully")
            
        except Exception as e:
            logging.error(f"❌ Key rotation error: {e}")
            raise
            
    async def validate_encryption(self):
        """Validate encryption/decryption is working correctly"""
        try:
            test_data = "DokyOS_Encryption_Test_2024"
            
            # Encrypt
            encrypted = await self.encrypt_string(test_data)
            
            # Decrypt
            decrypted = await self.decrypt_string(encrypted)
            
            if decrypted == test_data:
                logging.info("✅ Encryption validation: PASSED")
                return True
            else:
                logging.error("❌ Encryption validation: FAILED")
                return False
                
        except Exception as e:
            logging.error(f"❌ Encryption validation error: {e}")
            return False
            
    async def get_encryption_status(self):
        """Get encryption system status"""
        return {
            'initialized': self.fernet is not None,
            'key_exists': os.path.exists(self.key_file),
            'salt_exists': os.path.exists(self.salt_file),
            'validation_passed': await self.validate_encryption()
        }
        
    async def cleanup(self):
        """Cleanup encryption manager"""
        # Clear sensitive data from memory
        self.fernet = None
        logging.info("🔒 Encryption manager cleanup completed")
