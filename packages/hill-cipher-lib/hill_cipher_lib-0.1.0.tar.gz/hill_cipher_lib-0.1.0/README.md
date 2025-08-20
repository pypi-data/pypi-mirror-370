# Hill Cipher Library

A Python library for encrypting and decrypting text using the **Hill Cipher** algorithm.

## Installation
```bash
pip install .
```

## Usage
```python
import numpy as np
from hill_cipher import hill_encrypt, hill_decrypt

key = np.array([[3, 3], [2, 5]])
plaintext = "HELLO"
ciphertext = hill_encrypt(plaintext, key)
print("Encrypted:", ciphertext)

decrypted = hill_decrypt(ciphertext, key)
print("Decrypted:", decrypted)
```

## License
This project is licensed under the MIT License.
