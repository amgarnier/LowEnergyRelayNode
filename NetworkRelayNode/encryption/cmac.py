#!/usr/bin/python3

import cryptolib
from binascii import hexlify
from math import ceil


# Created by https://github.com/KianBahasadri/micropython-aes-cmac
class CMAC:

    def _xor(self, a, b):
        return bytes(x ^ y for x, y in zip(a, b))

    def _e(self, key, plain):
        aes = cryptolib.aes(key, 1)  # Using ECB mode
        return aes.encrypt(plain)

    def _d(self, key, enc):
        aes = cryptolib.aes(key, 1)  # Using ECB mode
        return aes.decrypt(enc)

    def generate_subkey(self, k):
        const_zero = b"\x00" * 16
        const_rb = (
            b"\x87" + b"\x00" * 15
        )  # Adjusted to align with common CMAC practices

        # Step 1
        l = self._e(k, const_zero)

        # Step 2 and 3
        def shift_left(bit_string):
            shifted = int.from_bytes(bit_string, "big") << 1
            if bit_string[0] & 0x80:
                shifted ^= 0x100000000000000000000000000000087  # Apply Rb polynomial
            return shifted.to_bytes(16, "big")

        k1 = shift_left(l)
        k2 = shift_left(k1)

        return k1, k2

    def aes_cmac(self, key, message):
        const_zero = b"\x00" * 16
        const_bsize = 16

        # Step 1
        k1, k2 = self.generate_subkey(key)

        # Step 2
        n = ceil(len(message) / const_bsize)
        m_block = [message[i * const_bsize : (i + 1) * const_bsize] for i in range(n)]

        # Step 3
        if n == 0:
            n = 1
            m_block = [b""]
            flag = False
        else:
            flag = len(message) % const_bsize == 0

        # Step 4
        if flag:
            m_last = self._xor(m_block[-1], k1)
        else:
            padding = b"\x80" + b"\x00" * (const_bsize - len(m_block[-1]) - 1)
            m_last = self._xor(m_block[-1] + padding, k2)

        # Step 5 and 6
        x = const_zero
        for block in m_block[:-1]:
            y = self._xor(x, block)
            x = self._e(key, y)
        y = self._xor(m_last, x)
        t = self._e(key, y)

        # Step 7
        return t


if __name__ == "__main__":
    key = bytes.fromhex("7fb7b598d7e50457438099994907a2f0")
    message = bytes.fromhex("b4ffeaa4b4293b6d2077a172e095c819")
    cmac = CMAC()
    mac = cmac.aes_cmac(key, message)
    expected_out = "a53a717d302670eb4970e485c67787be"
    print(f"CMAC valid: {mac.hex() == expected_out}")
