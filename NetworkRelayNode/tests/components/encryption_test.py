import lib.unittest as unittest
import encryption.cmac as cmac


class EncryptionTest(unittest.TestCase):

    def test_cmac(self):
        key = bytes.fromhex("7fb7b598d7e50457438099994907a2f0")
        message = bytes.fromhex("b4ffeaa4b4293b6d2077a172e095c819")
        cmac_val = cmac.CMAC()
        mac = cmac_val.aes_cmac(key, message)
        expected_out = "a53a717d302670eb4970e485c67787be"
        self.assertEqual(mac.hex(), expected_out, "not equal")
