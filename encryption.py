import os
import base64
import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json

class EncryptionManager:
    """Gestionnaire de chiffrement pour les données sensibles"""
    
    def __init__(self, master_key=None):
        self.master_key = master_key or os.environ.get('MASTER_KEY')
        if not self.master_key:
            raise ValueError("Master key is required for encryption")
        
        self.fernet = self._create_fernet_key()
    
    def _create_fernet_key(self):
        """Crée une clé Fernet à partir de la clé maître"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'bunker_salt_2025',  # En production, utiliser un salt aléatoire
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt_string(self, plaintext):
        """Chiffre une chaîne de caractères"""
        if not plaintext:
            return None
        
        encrypted = self.fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, ciphertext):
        """Déchiffre une chaîne de caractères"""
        if not ciphertext:
            return None
        
        try:
            encrypted_data = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception:
            return None
    
    def encrypt_dict(self, data):
        """Chiffre un dictionnaire"""
        if not data:
            return None
        
        json_data = json.dumps(data, sort_keys=True)
        return self.encrypt_string(json_data)
    
    def decrypt_dict(self, ciphertext):
        """Déchiffre un dictionnaire"""
        if not ciphertext:
            return None
        
        json_data = self.decrypt_string(ciphertext)
        if json_data:
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                return None
        return None
    
    def hash_password(self, password, salt=None):
        """Hash un mot de passe avec salt"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt, 
                                     100000)
        
        return {
            'hash': base64.b64encode(pwdhash).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }
    
    def verify_password(self, password, stored_hash, stored_salt):
        """Vérifie un mot de passe"""
        salt = base64.b64decode(stored_salt.encode('utf-8'))
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                     password.encode('utf-8'),
                                     salt,
                                     100000)
        
        stored_hash_bytes = base64.b64decode(stored_hash.encode('utf-8'))
        return hmac.compare_digest(pwdhash, stored_hash_bytes)
    
    def generate_secure_token(self, length=32):
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(length)
    
    def create_hmac_signature(self, data, secret=None):
        """Crée une signature HMAC"""
        if secret is None:
            secret = self.master_key
        
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        signature = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_hmac_signature(self, data, signature, secret=None):
        """Vérifie une signature HMAC"""
        expected_signature = self.create_hmac_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)

class SecureStorage:
    """Stockage sécurisé pour les données sensibles"""
    
    def __init__(self, encryption_manager):
        self.encryption = encryption_manager
        self.storage = {}  # En production, utiliser Redis ou une base sécurisée
    
    def store_sensitive_data(self, key, data, ttl=3600):
        """Stocke des données sensibles chiffrées"""
        encrypted_data = self.encryption.encrypt_dict(data)
        
        self.storage[key] = {
            'data': encrypted_data,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def retrieve_sensitive_data(self, key):
        """Récupère des données sensibles"""
        if key not in self.storage:
            return None
        
        stored_item = self.storage[key]
        
        # Vérifier l'expiration
        if time.time() > stored_item['expires_at']:
            del self.storage[key]
            return None
        
        return self.encryption.decrypt_dict(stored_item['data'])
    
    def delete_sensitive_data(self, key):
        """Supprime des données sensibles"""
        if key in self.storage:
            del self.storage[key]
    
    def cleanup_expired_data(self):
        """Nettoie les données expirées"""
        now = time.time()
        expired_keys = [
            key for key, item in self.storage.items()
            if now > item['expires_at']
        ]
        
        for key in expired_keys:
            del self.storage[key]
        
        return len(expired_keys)

class DataMasking:
    """Utilitaires de masquage de données"""
    
    @staticmethod
    def mask_email(email):
        """Masque une adresse email"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone):
        """Masque un numéro de téléphone"""
        if not phone:
            return phone
        
        # Garder seulement les chiffres
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) < 4:
            return '*' * len(digits)
        
        return digits[:2] + '*' * (len(digits) - 4) + digits[-2:]
    
    @staticmethod
    def mask_credit_card(card_number):
        """Masque un numéro de carte de crédit"""
        if not card_number:
            return card_number
        
        digits = ''.join(filter(str.isdigit, card_number))
        
        if len(digits) < 8:
            return '*' * len(digits)
        
        return '*' * (len(digits) - 4) + digits[-4:]
    
    @staticmethod
    def mask_sensitive_dict(data, sensitive_fields=None):
        """Masque les champs sensibles d'un dictionnaire"""
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'token', 'secret', 'key', 'credit_card',
                'ssn', 'social_security', 'passport', 'license'
            ]
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            key_lower = key.lower()
            
            if any(field in key_lower for field in sensitive_fields):
                if isinstance(value, str):
                    if 'email' in key_lower:
                        masked_data[key] = DataMasking.mask_email(value)
                    elif 'phone' in key_lower:
                        masked_data[key] = DataMasking.mask_phone(value)
                    elif 'card' in key_lower:
                        masked_data[key] = DataMasking.mask_credit_card(value)
                    else:
                        masked_data[key] = '*' * min(len(value), 8)
                else:
                    masked_data[key] = '[MASKED]'
        
        return masked_data

# Décorateur pour le chiffrement automatique
def encrypt_response_data(fields_to_encrypt=None):
    """Décorateur pour chiffrer automatiquement les données de réponse"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if isinstance(response, dict) and fields_to_encrypt:
                encryption_manager = EncryptionManager()
                
                for field in fields_to_encrypt:
                    if field in response:
                        response[field] = encryption_manager.encrypt_string(
                            str(response[field])
                        )
            
            return response
        
        return decorated_function
    return decorator
