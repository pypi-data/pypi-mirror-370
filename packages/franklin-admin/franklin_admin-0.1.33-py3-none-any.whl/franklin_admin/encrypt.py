import base64
import os
import sys
import getpass
from typing import Optional
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

token_path_templ: str = os.path.dirname(sys.modules['franklin_admin'].__file__) + '/data/admin/{}_token.enc'

def derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """Derive encryption key from password using PBKDF2.
    
    Parameters
    ----------
    password : str
        Password to derive key from.
    salt : bytes
        Random salt for key derivation.
    iterations : int, optional
        Number of PBKDF2 iterations, by default 100_000.
        
    Returns
    -------
    bytes
        Derived encryption key.
    """
    return PBKDF2(password, salt, dkLen=32, count=iterations)

def encrypt_token(api_token: str, password: str) -> bytes:
    """Encrypt an API token using AES-GCM with PBKDF2 key derivation.
    
    Parameters
    ----------
    api_token : str
        GitLab API token to encrypt.
    password : str
        Password for encryption.
        
    Returns
    -------
    bytes
        Encrypted token data containing salt, nonce, tag, and ciphertext.
    """
    salt = get_random_bytes(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(api_token.encode())
    # Store: salt + nonce + tag + ciphertext
    return salt + cipher.nonce + tag + ciphertext

def decrypt_token(token_encrypted_with_salt: bytes, password: str) -> str:
    """Decrypt an API token using AES-GCM with PBKDF2 key derivation.
    
    Parameters
    ----------
    token_encrypted_with_salt : bytes
        Encrypted token data containing salt, nonce, tag, and ciphertext.
    password : str
        Password for decryption.
        
    Returns
    -------
    str
        Decrypted API token.
        
    Raises
    ------
    ValueError
        If decryption fails due to wrong password or corrupted data.
    """
    salt = token_encrypted_with_salt[:16]
    nonce = token_encrypted_with_salt[16:32]
    tag = token_encrypted_with_salt[32:48]
    ciphertext = token_encrypted_with_salt[48:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

def get_api_token(user: str, password: str) -> str:
    """Retrieve and decrypt stored API token for a user.
    
    Parameters
    ----------
    user : str
        Username to retrieve token for.
    password : str
        Password for decryption.
        
    Returns
    -------
    str
        Decrypted API token.
        
    Raises
    ------
    FileNotFoundError
        If encrypted token file doesn't exist.
    ValueError
        If decryption fails.
    """
    with open(token_path_templ.format(user), "rb") as f:
        encrypted = f.read()
    api_token = decrypt_token(encrypted, password)
    return api_token

def store_encrypted_token(user: str, password: str, token: str, overwrite=False) -> None:
    """Encrypt and store an API token for a user.
    
    Parameters
    ----------
    user : str
        Username to store token for.
    password : str
        Password for encryption.
    token : str
        API token to encrypt and store.
        
    Raises
    ------
    OSError
        If token file cannot be written.
    """
    token_file_name = token_path_templ.format(user)
    if os.path.exists(token_file_name) and not overwrite:
        raise FileExistsError(f"Token file {token_file_name} already exists.")
    encrypted = encrypt_token(token, password)
    with open(token_file_name, "wb") as f:
        f.write(encrypted)


# import base64
# import os
# import sys
# import getpass
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.backends import default_backend

# token_path_templ = os.path.dirname(sys.modules['franklin_educator'].__file__) + '/data/admin/{}_token.enc'


# def derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
#     kdf = PBKDF2HMAC(
#         algorithm=hashes.SHA256(),
#         length=32,
#         salt=salt,
#         iterations=iterations,
#         backend=default_backend()
#     )
#     return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# def encrypt_token(api_token: str, password: str) -> bytes:
#     salt = os.urandom(16)
#     key = derive_key(password, salt)
#     f = Fernet(key)
#     token_encrypted = f.encrypt(api_token.encode())
#     return salt + token_encrypted  # store salt + ciphertext

# def decrypt_token(token_encrypted_with_salt: bytes, password: str) -> str:
#     salt = token_encrypted_with_salt[:16]
#     ciphertext = token_encrypted_with_salt[16:]
#     key = derive_key(password, salt)
#     f = Fernet(key)
#     return f.decrypt(ciphertext).decode()

# def get_api_token(user: str, password: str) -> str:
#     with open(token_path_templ.format(user), "rb") as f:
#         encrypted = f.read()
#     api_token = decrypt_token(encrypted, password)
#     return api_token

# # --- Encrypt once and store ---
# def store_encrypted_token(user: str, password: str, token: str):
#     # api_token = getpass.getpass("Enter GitLab API token: ")
#     # admin_password = getpass.getpass("Enter admin password to encrypt: ")
#     token_path_templ.format(user)
#     encrypted = encrypt_token(token, password)
#     with open(token_path_templ.format(user), "wb") as f:
#         f.write(encrypted)
#     print("Token encrypted and stored.")
