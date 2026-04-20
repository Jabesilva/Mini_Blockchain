from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def derivar_chave(senha: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=600_000)
    return kdf.derive(senha.encode())

def cifrar_aes_gcm(chave: bytes, dados: str) -> tuple[bytes, bytes]:
    iv = os.urandom(12)          # IV único
    aead = AESGCM(chave)
    ciphertext = aead.encrypt(iv, dados.encode(), None)
    return iv, ciphertext

def decifrar_aes_gcm(chave: bytes, iv: bytes, ciphertext: bytes) -> str:
    aead = AESGCM(chave)
    return aead.decrypt(iv, ciphertext, None).decode()
    # lança InvalidTag se o ciphertext foi adulterado 