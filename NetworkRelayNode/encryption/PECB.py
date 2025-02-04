import encryption.mpyaes as mpyaes

# to test install via all commands on bottoom


def decrypt_data_ecb(key, ciphertext):
    aes = mpyaes.new(key, mpyaes.MODE_ECB)
    plain_text = aes.decrypt(ciphertext)
    return plain_text


def encrypt_data_ecb(key, plaintext):
    print(f"key:{key}, plaintext:{plaintext}")
    aes = mpyaes.new(key, mpyaes.MODE_ECB)
    enc = aes.encrypt(plaintext=plaintext)
    encrypted = aes.encrypt(plaintext)
    print(f"encrypted:{encrypted}")
    return encrypted


if __name__ == "__main__":

    # Example usage
    key = bytes.fromhex("8b84eedec100067d670971dd2aa700cf")  # 16 bytes = 128 bits
    plainText = bytes.fromhex("000000000012345678b5e5bfdacbaf6c")

    # print(decrypt_data_ecb(key, b"xec\xa4\x87\x51\x67 "))
    # Encrypt the plaintext
    ciphertext = encrypt_data_ecb(key, plainText)
    print(f"Ciphertext (hex): {ciphertext.hex()}")
    plaintext = decrypt_data_ecb(key, ciphertext)
    print(f"Plaintext (hex): {plaintext.hex()}")
