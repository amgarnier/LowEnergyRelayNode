# from helpers import aes_ccm
import encryption.PECB as PECB
import binascii


class Pdu:
    def __init__(self, pdu: list[bytearray]):
        self._pdu = pdu
        self._constructed_pdu = bytearray()

    def construct_pdu(self):
        # concatonate al the byte arrays in the list
        self._constructed_pdu = b"".join(self._pdu)
        return self._constructed_pdu

    def get_pdu(self):
        return self._constructed_pdu


class NetworkPdu(Pdu):
    """
    NetworkPdu class represents a Network Protocol Data Unit (PDU) and provides methods to construct, deconstruct, obfuscate, and encrypt/decrypt the PDU.
    Attributes:
        _network_pdu (bytearray): The network PDU message.
        _ivi_nid (bytearray): The Initialization Vector Index and Network ID.
        _obfuscated_data (bytearray): The obfuscated data portion of the PDU.
        _net_mic (bytearray): The Network Message Integrity Check value.
        _ctl (bytes): The Control field.
        _ttl (bytes): The Time-to-Live field.
        _seq (bytearray): The sequence number.
        _src (bytearray): The source address.
        _dst (bytearray): The destination address.
        _transport_pdu (bytearray): The transport PDU.
        _encrypted_data_message (bytearray): The encrypted data message.
    Methods:
        __init__(network_pdu_message: bytearray = bytearray()):
            Initializes a new instance of the NetworkPdu class.
        construct_pdu():
            Constructs the network PDU from its components and returns the constructed PDU.
        deconstruct_pdu():
            Deconstructs the network PDU into its components and prints their hexadecimal representation.
        de_obfusicate_data(IVIndex: bytearray, key: bytearray):
        obfusicate_data():
            Obfuscates the data and returns the obfuscated data.
        encrypt_data(dst: bytearray, transport_pdu: bytearray, key: bytearray, nonce: bytearray):
            Encrypts the data using the provided destination address, transport PDU, key, and nonce.
        decrypt_data(key: bytearray, nonce: bytearray, mic: bytearray):
            Decrypts the encrypted data message using the provided key, nonce, and MIC.
        create_network_from_message():
            Creates a full network message from the given network PDU and returns the constructed PB advertising bearer PDU.
    """

    def __init__(self, network_pdu_message: bytearray = bytearray()):
        self._network_pdu = network_pdu_message
        self._ivi_nid = bytearray()
        self._obfuscated_data = bytearray()
        self._net_mic = bytearray()
        self._ctl = bytes()
        self._ttl = bytes()
        self._seq = bytearray()
        self._src = bytearray()
        self._dst = bytearray()
        self._transport_pdu = bytearray()
        self._encrypted_data_message = bytearray()
        self._net_mic = bytearray()

    def construct_pdu(self):
        super()._pdu = [
            bytearray(self._network_pdu),
            self._ivi_nid,
            self._obfuscated_data,
            self._encrypted_data_message,
            self._net_mic,
        ]
        super().construct_pdu()
        return super().get_pdu()

    def deconstruct_pdu(self):
        """
        Deconstructs the network PDU (Protocol Data Unit) into its components.

        This method extracts and assigns the following components from the network PDU:
        - IVI_NID: The Initialization Vector Index and Network ID.
        - _obfuscated_data: The obfuscated data portion of the PDU.
        - _encrypted_data_message: The encrypted data message portion of the PDU.
        - net_mic: The Network Message Integrity Check value.

        It also prints the hexadecimal representation of each component.

        Returns:
            self: The instance of the class with the deconstructed PDU components.
        """
        # deconstruct the pdu
        self.ivi_nid = bytearray(self._network_pdu[0].to_bytes(1, "big"))
        self._obfuscated_data = bytearray(self._network_pdu[1:7])
        self._encrypted_data_message = bytearray(
            self._network_pdu[7 : len(self._network_pdu) - 8]
        )
        self.net_mic = bytearray(
            self._network_pdu[len(self._network_pdu) - 8 : len(self._network_pdu)]
        )
        return self

    def de_obfusicate_data(self, IVIndex: bytearray, key: bytearray):
        """
        De-obfuscates the data using the provided IVIndex and key.

        Args:
            IVIndex (bytearray): The initialization vector index used for de-obfuscation.
            key (bytearray): The key used for de-obfuscation.

        Returns:
            self: The instance with de-obfuscated data.

        Raises:
            ValueError: If the de-obfuscicated data cannot be converted to bytes.

        Notes:
            - The method performs the following steps:
                1. Concatenates the encrypted data message and network MIC to form the privacy random.
                2. Constructs the privacy plaintext by concatenating a fixed bytearray, IVIndex, and privacy random.
                3. Encrypts the privacy plaintext using ECB mode with the provided key to get the PECB value.
                4. XORs the obfuscated data with the PECB value to get the de-obfuscated data.
                5. Extracts the CTL and TTL values from the de-obfuscated data.
                6. Extracts the sequence number (seq) and source address (src) from the de-obfuscated data.
        """

        privacy_random = self._encrypted_data_message + self._net_mic
        privacy_plaintext = bytearray.fromhex("0000000000") + IVIndex + privacy_random
        pecb_value = PECB.encrypt_data_ecb(bytes(key), bytes(privacy_plaintext)).hex()[
            0:12
        ]
        ObfusicatedData = int(self._obfuscated_data.hex(), 16)
        pecb_int = int(pecb_value, 16)
        de_obfusicated = ObfusicatedData ^ pecb_int
        de_obfusicated_bytes = binascii.unhexlify(hex(de_obfusicated)[2:])
        ctl_ttl = de_obfusicated_bytes[0].to_bytes(1, "big")
        # convert ctl_ttl to binary
        ctl_ttl = int.from_bytes(ctl_ttl, "big")
        ctl_value = 0b10000000 & ctl_ttl
        ttl_value = 0b01111111 & ctl_ttl
        # get first bit of ctl_ttl and convert to byte
        # TODO: binary and operate it to get the first bit
        self._ctl = ctl_value.to_bytes(1, "big")
        # get last 7 bits of ctl_ttl and convert to bytearray
        self._ttl = ttl_value.to_bytes(1, "big")
        self.seq = de_obfusicated_bytes[1:4]
        self.src = de_obfusicated_bytes[4:6]
        return self

    def obfusicate_data(self):
        # do some obfusication

        return self._obfuscated_data

    def encrypt_data(
        self, dst: bytearray, transport_pdu: bytearray, key: bytearray, nonce: bytearray
    ):
        # TODO: cannot implement ccm in PICO
        # plain_text = dst + transport_pdu
        # self._encrypted_data_message, self._netMic = aes_ccm.encrypt_aes_ccm(
        #     plain_text=plain_text, key=key, nonce=nonce
        # )
        # # do some encryption
        # print(self._encrypted_data_message.hex())
        # print(self._net_mic)

        return self

    def decrypt_data(self, key: bytearray, nonce: bytearray, mic: bytearray):
        """
        Decrypts the encrypted data message using the provided key, nonce, and MIC (Message Integrity Code).

        Args:
            key (bytearray): The encryption key used for decryption.
            nonce (bytearray): The nonce value used for decryption.
            mic (bytearray): The Message Integrity Code used for verification.

        Returns:
            bytearray: The original encrypted data message.

        Note:
            Currently, decryption is not performed, and the destination address (_dst) and transport PDU (_transport_pdu)
            are hardcoded for testing purposes.
        """
        # do some decryption
        # plain_text = aes_ccm.decrypt_aes_ccm_verify(
        #     cipher_text=self._encrypted_data_message,
        #     key=key,
        #     nonce=nonce,
        #     mic=mic,
        # )
        # print(plain_text[0:2])
        # self._dst = plain_text[0:2]
        # self._transport_pdu = plain_text[2 : len(plain_text)]
        # TODO: pico can not decrypt for this test it is not needed so we will hard code it
        self._dst = bytearray.fromhex("0003")  # fffd
        self._transport_pdu = bytearray.fromhex(
            "00a6ac00000002"
        )  # 034b50057e400000010000
        return self._encrypted_data_message

    def create_network_from_message(self):
        """
        Creates a full network message from the given network PDU.

        This method constructs an advertising bearer PDU from the current instance,
        then constructs a PB advertising bearer from the advertising bearer PDU.
        Finally, it returns the constructed PB advertising bearer PDU.

        Returns:
            bytes: The constructed PB advertising bearer PDU.
        """
        # code to create a full network message with given network pdu
        # # advertise bearer pdu
        adv_bearer_pdu = AdvBearerMessagePdu(contents=self)
        adv_bearer_pdu.construct_pdu()
        # # pb advertising bearer
        pb_advertising_bearer = PbAdvertisingBearer(contents=adv_bearer_pdu)
        pb_advertising_bearer.construct_pdu()
        return pb_advertising_bearer.get_pdu()


class AdvBearerMessagePdu(Pdu):
    """
    A class to represent an Advertising Bearer Message Protocol Data Unit (PDU).

    This class is used to construct a PDU for advertising bearer messages in a network relay node.

    Attributes:
        _ad_message_type (bytearray): The advertising message type, initialized to "2a" (ADV_NONCONN_IN).
        _contents (bytearray): The contents of the network PDU.

    Methods:
        __init__(contents: NetworkPdu):
            Initializes the AdvBearerMessagePdu with the given network PDU contents.
    """

    def __init__(self, contents: NetworkPdu):
        self._ad_message_type = bytearray.fromhex("2a")  # ADV_NONCONN_IN
        self._contents = contents._network_pdu
        super().__init__([self._ad_message_type, self._contents])
        super().construct_pdu()
        self._contents = super().get_pdu()


class PbAdvertisingBearer(Pdu):
    def __init__(
        self, contents: AdvBearerMessagePdu = AdvBearerMessagePdu(contents=NetworkPdu())
    ):
        self._ad_type = bytearray.fromhex("20")  # ADV_NONCONN_IN
        self._contents = contents._contents
        self._length = (len(self._contents) + 1).to_bytes(1, "big")
        super().__init__(
            [
                bytearray(self._length),
                bytearray(self._ad_type),
                bytearray(self._contents),
            ]
        )
        # self._constructed_pdu = bytearray()
        super().construct_pdu()
        self._contents = super().get_pdu()


if __name__ == "__main__":

    # deconstruct message with encrypted and obfusicated data
    network_pdu_message = bytearray.fromhex(
        "68eca487516765b5e5bfdacbaf6cb7fb6bff871f035444ce83a670df"
    )
    networkPdu = NetworkPdu(network_pdu_message=network_pdu_message)
    # networkPdu.deconstruct_pdu()

    # # take deconstructed pdu and reconstruct it
    # network_pdu_construct = NetworkPdu()

    # network_pdu_construct.construct_pdu(
    #     ivi_nid=networkPdu.ivi_nid,
    #     obfuscated=networkPdu._obfuscated_data,
    #     encrypted_data=networkPdu.encypted_data,
    #     net_mic=networkPdu.net_mic,
    # )

    # print(network_pdu_construct)

    # deobfusicate the data

    # obfusicatedData = ObfusicatedData(
    #     obfusicated_data=networkPdu.obfuscated, network_pdu=networkPdu
    # )

    # obfusicatedData.de_obfusicate_data(
    #     IVIndex=bytearray.fromhex("12345678"),
    #     key=bytearray.fromhex("8b84eedec100067d670971dd2aa700cf"),
    # )

    message = networkPdu.create_network_from_message()
    print(message)
    # # # advertise bearer pdu
    # adv_bearer_pdu = AdvBearerMessagePdu(contents=networkPdu)
    # print(adv_bearer_pdu._contents.hex())
    # adv_bearer_pdu.construct_pdu()
    # print(adv_bearer_pdu.get_pdu().hex())

    # # # pb advertising bearer
    # pb_advertising_bearer = PbAdvertisingBearer(contents=adv_bearer_pdu)
    # pb_advertising_bearer.construct_pdu()
    # print(pb_advertising_bearer.get_pdu().hex())

    # encryptedData = EncryptedData()
    # encryptedData.encrypt_data(
    #     dst=bytearray.fromhex("fffd"),  # destination address
    #     transport_pdu=bytearray.fromhex(
    #         "034b50057e400000010000"
    #     ),  # input the transport pdu
    #     key=bytearray.fromhex(
    #         "0953fa93e7caac9638f58820220a398e"
    #     ),  # todo: Encrypted key create function to generate this key
    #     nonce=bytearray.fromhex("00800000011201000012345678"),  # todo: generate nonce
    # )
    # print(encryptedData._encrypted_data.hex())

    # # decrypt the data
    # encryptedData.decrypt_data(
    #     key=bytearray.fromhex("0953fa93e7caac9638f58820220a398e"),
    #     nonce=bytearray.fromhex("00800000011201000012345678"),
    #     mic=bytearray.fromhex("035444ce83a670df"),
    # )
    # print(
    #     f"Destination: {encryptedData._dst.hex()} Transport PDU: {encryptedData._transport_pdu.hex()}"
    # )
    pass
