import encryption.cmac as cmac

# this is test of the K2 derivation functions
# The k2 function is used to convert the master security credentials, NetKey as N, and generate the master
# security material, NID, EncryptionKey, and PrivacyKey
c = cmac.CMAC()


def SALT():
    key = bytes(16)  # AES-128 key (16 bytes)
    message = bytearray.fromhex("736D6B32")
    c_obj = c.aes_cmac(key=key, message=message)
    return c_obj.hex()


def T(N, SALT):
    T = c.aes_cmac(SALT, N)
    # T = CMAC.new(SALT, ciphermod=AES)
    # T.update(N)
    return T.hex()


def k1(N, SALT, P):
    TValue = bytes.fromhex(T(N, SALT))
    K1 = c.aes_cmac(TValue, P)
    # K1 = CMAC.new(TValue, ciphermod=AES)
    # K1.update(P)
    return K1.hex()


def TCMAC(T, TX):
    T = c.aes_cmac(T, TX)
    # T = CMAC.new(T, ciphermod=AES)
    # TCMAC = T.update(TX)
    return T.hex()


def k2(N_bytes, P_bytes):
    SALT_Bytes = bytes.fromhex(SALT())
    T_B = bytes.fromhex(T(N_bytes, SALT_Bytes))
    T1 = TCMAC(T_B, (P_bytes + bytes.fromhex("01")))
    T2 = TCMAC(T_B, (bytes.fromhex(T1) + P_bytes + bytes.fromhex("02")))
    T3 = TCMAC(T_B, (bytes.fromhex(T2) + P_bytes + bytes.fromhex("03")))
    bytValue = bytes.fromhex(T1) + bytes.fromhex(T2) + bytes.fromhex(T3)
    intValue = int.from_bytes(bytValue, "big")
    k2 = (intValue) % (2**263)
    k2Hex = hex(k2)
    NID = bytearray.fromhex(k2Hex[2:4])
    EncryptionKey = bytearray.fromhex(k2Hex[4:36])
    PrivacyKey = bytearray.fromhex(k2Hex[36:])
    return NID, EncryptionKey, PrivacyKey


if __name__ == "__main__":
    SALT_HEX = SALT()
    # test salt function of test to equal b73cefbd641ef2ea598c2b6efb62f79c

    # # now we get our T  2ea6467aa3378c4c545eda62935b9b86
    N_hex = "f7a2a44f8e8a8029064f173ddc1e2b00"
    N_bytes = bytes.fromhex(N_hex)
    # SALT_hex = SALT()
    # T_hex = T(N_bytes, bytes.fromhex(SALT_hex))
    # #print(f"T output = {T_hex}")

    # now we split our T values to get to, t1, t2
    P = "00"
    P_bytes = bytes.fromhex(P)
    NID, EncryptionKey, PrivacyKey = k2(N_bytes, P_bytes)
    print(
        f"NID: {NID} \n EncryptionKey: {EncryptionKey.hex()} \n PrivacyKey: {PrivacyKey.hex()}"
    )

# compare for test EncryptionKey: 9f589181a0f50de73c8070c7a6d27f46
# PrivacyKey: 4c715bd4a64b938f99b453351653124f
