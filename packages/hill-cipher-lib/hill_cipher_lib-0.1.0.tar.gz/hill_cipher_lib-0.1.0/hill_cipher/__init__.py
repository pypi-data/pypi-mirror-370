import numpy as np
from .hill_cipher import hill_encrypt, hill_decrypt
from sympy import Matrix

def hill_encrypt(plain_text: str, key_matrix: np.ndarray) -> str:
    """
    Encrypts plain text using the Hill Cipher method.
    
    Parameters:
        plain_text (str): The text to encrypt.
        key_matrix (np.ndarray): The key matrix (must be invertible mod 26).
        
    Returns:
        str: The encrypted cipher text.
    """
    plain_text = plain_text.upper().replace(" ", "")
    n = key_matrix.shape[0]

    # Padding with 'X'
    while len(plain_text) % n != 0:
        plain_text += 'X'

    encrypted = ""
    for i in range(0, len(plain_text), n):
        block = [ord(char) - 65 for char in plain_text[i:i+n]]
        cipher_block = np.dot(key_matrix, block) % 26
        encrypted += ''.join(chr(num + 65) for num in cipher_block)

    return encrypted


def hill_decrypt(cipher_text: str, key_matrix: np.ndarray) -> str:
    """
    Decrypts cipher text using the Hill Cipher method.
    
    Parameters:
        cipher_text (str): The encrypted text.
        key_matrix (np.ndarray): The key matrix (must be invertible mod 26).
        
    Returns:
        str: The decrypted plain text.
    """
    n = key_matrix.shape[0]
    inv_key_matrix = Matrix(key_matrix).inv_mod(26)
    inv_key_matrix = np.array(inv_key_matrix).astype(int)

    decrypted = ""
    for i in range(0, len(cipher_text), n):
        block = [ord(char) - 65 for char in cipher_text[i:i+n]]
        plain_block = np.dot(inv_key_matrix, block) % 26
        decrypted += ''.join(chr(num + 65) for num in plain_block)

    return decrypted
