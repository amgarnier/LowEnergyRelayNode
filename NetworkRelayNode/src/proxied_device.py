from encryption.K2FunctionMaster import k2


#
# assumption: nonce and i_v index given in a heartbeat message which is not part of this test
class ProxiedDevice:
    def __init__(
        self,
        unicast_address: bytearray = bytearray(),
        network_key: bytearray = bytearray(),
        nonce: bytearray = bytearray(),
        iv_index: bytearray = bytearray(),
    ):
        self._unicast_address = unicast_address
        self._network_key = network_key  # netkey
        self._nonce = nonce
        self._iv_index = iv_index
        P_bytes = bytes.fromhex("00")
        N_bytes = bytes(self._network_key)
        self._nid, self._network_encryption_key, self._privacy_key = k2(
            N_bytes, P_bytes
        )


if __name__ == "__main__":
    # create proxied device
    proxied_device = ProxiedDevice(
        unicast_address=bytearray.fromhex("70cf7c9732a345b691494810d2e9cbf4"),
        network_key=bytearray.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"),
    )
    # create network encryption key, privacy keys, and nid
    print(
        f"Network Encryption Key: {proxied_device._network_encryption_key.hex()} \n NID: {proxied_device._nid.hex()} \n Privacy Key: {proxied_device._privacy_key.hex()}"
    )
