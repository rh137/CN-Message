from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

def pad(string): # pad ' ' to string
    while len(string) % 16 != 0:
        string += ' '
    return string

key = 'CNFinalProject' # private key
aes = AES.new(pad(key).encode(), AES.MODE_ECB) # construct AES by private key

def encrypt(plaintext): # encryption of AES
    cyphertext_byte = aes.encrypt(pad(plaintext).encode())
    cyphertext_hex = b2a_hex(cyphertext_byte)
    cyphertext = cyphertext_hex.decode()
    return cyphertext

def decrypt(cyphertext): # decryption of AES
    plaintext = str(aes.decrypt(a2b_hex(pad(cyphertext).encode())), encoding='utf-8',errors="ignore")
    return plaintext
